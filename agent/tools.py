# ABOUTME: Tool functions for the agent system
# ABOUTME: HTTP clients for API calls and WebSocket intent emitter for UI control
import httpx
import json
import websockets
import os
from typing import Optional

API_BASE = os.getenv("API_BASE", "http://localhost:8000")
AGENT_WS = os.getenv("AGENT_WS", "ws://localhost:8765")


def start_workflow(name: str):
    """Start a workflow run and return its metadata."""
    with httpx.Client() as client:
        response = client.post(
            f"{API_BASE}/workflows", json={"name": name}, timeout=10
        )
        response.raise_for_status()
        return response.json()


def record_workflow_step(run_id: int, name: str, status: str, result: Optional[str] = None):
    """Record a step's progress for a workflow run."""
    with httpx.Client() as client:
        response = client.post(
            f"{API_BASE}/workflows/{run_id}/steps",
            json={"name": name, "status": status, "result": result},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()


def search_customers(name: str = None, location: str = None, criteria: str = None):
    """Search customers by various criteria."""
    with httpx.Client() as client:
        params = {}
        if name:
            params["name"] = name
        
        response = client.get(f"{API_BASE}/customers", params=params, timeout=10)
        response.raise_for_status()
        customers = response.json()
        
        # Apply additional filtering based on criteria
        if location and customers:
            # Mock location filtering - in real system would be in database
            location_keywords = location.lower().split()
            filtered = []
            for customer in customers:
                # Simple mock: check if location keywords appear in customer name/email
                customer_text = f"{customer.get('name', '')} {customer.get('email', '')}".lower()
                if any(keyword in customer_text for keyword in location_keywords):
                    filtered.append(customer)
            customers = filtered
            
        if criteria and customers:
            # Apply general criteria filtering
            criteria_lower = criteria.lower()
            if "high activity" in criteria_lower:
                # Mock: return customers with more tickets (simplified)
                enriched_customers = []
                for customer in customers:
                    tickets_response = client.get(
                        f"{API_BASE}/tickets",
                        params={"customer_id": customer["id"]},
                        timeout=10
                    )
                    ticket_count = len(tickets_response.json())
                    customer["ticket_count"] = ticket_count
                    if ticket_count > 2:  # Mock threshold
                        enriched_customers.append(customer)
                customers = enriched_customers
                
        return customers


def list_tickets(customer_id: str, status: str = "open"):
    with httpx.Client() as client:
        response = client.get(
            f"{API_BASE}/tickets",
            params={"customer_id": customer_id, "status": status},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()


def create_note(ticket_id: str, body: str):
    with httpx.Client() as client:
        response = client.post(
            f"{API_BASE}/notes", json={"ticket_id": ticket_id, "body": body}, timeout=10
        )
        if response.status_code >= 400:
            raise RuntimeError(response.json())
        return response.json()


def send_email(to: str, subject: str, body: str):
    with httpx.Client() as client:
        response = client.post(
            f"{API_BASE}/emails",
            json={"to": to, "subject": subject, "body": body},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()


async def emit_intent(intent: dict):
    try:
        async with websockets.connect(AGENT_WS) as ws:
            await ws.send(json.dumps(intent))
            return {"status": "sent", "intent": intent}
    except Exception as e:
        return {"status": "error", "message": str(e)}



def tool_receive_event(event: dict):
    """Process events received from the frontend.

    Events can trigger workflows or update internal state. The payload
    structure is expected to be a dictionary.
    """

    event_type = event.get("type")

    # Workflow execution request
    if event_type == "workflow":
        workflow = event.get("name")
        context = event.get("context", {})
        if workflow:
            return execute_workflow(workflow, context)
        return {"status": "error", "message": "missing workflow name"}

    # Persist arbitrary state
    if event_type == "state":
        key = event.get("key")
        value = event.get("value", {})
        if key:
            return set_workflow_state(key, value)
        return {"status": "error", "message": "missing state key"}

    # Default: acknowledge receipt
    return {"status": "received", "event": event}

async def tool_add_component(component: str, component_id: str, props: dict | None = None):
    """Dynamically add a UI component by emitting an intent to the frontend."""
    intent = {
        "type": "add_component",
        "id": component_id,
        "component": component,
        "props": props or {},
    }
    return await emit_intent(intent)



def get_customer_stats(metric: str):
    """Get customer analytics and statistics."""
    with httpx.Client() as client:
        # Get all customers
        customers_response = client.get(f"{API_BASE}/customers", timeout=10)
        customers = customers_response.json()
        
        if metric == "ticket_count":
            stats = []
            for customer in custom30ers:
                tickets_response = client.get(
                    f"{API_BASE}/tickets",
                    params={"customer_id": customer["id"]},
                    timeout=10
                )
                ticket_count = len(tickets_response.json())
                stats.append({
                    "customer": customer["name"],
                    "ticket_count": ticket_count
                })
            return {"metric": "ticket_count", "data": stats}
            
        elif metric == "status_summary":
            total_open = 0
            total_closed = 0
            for customer in customers:
                open_tickets = client.get(
                    f"{API_BASE}/tickets",
                    params={"customer_id": customer["id"], "status": "open"},
                    timeout=10
                ).json()
                closed_tickets = client.get(
                    f"{API_BASE}/tickets", 
                    params={"customer_id": customer["id"], "status": "closed"},
                    timeout=10
                ).json()
                total_open += len(open_tickets)
                total_closed += len(closed_tickets)
            
            return {
                "metric": "status_summary",
                "data": {
                    "total_customers": len(customers),
                    "total_open_tickets": total_open,
                    "total_closed_tickets": total_closed
                }
            }
        
        elif metric == "all":
            # Combine multiple metrics
            stats = get_customer_stats("ticket_count")
            summary = get_customer_stats("status_summary")
            return {
                "metric": "all",
                "ticket_counts": stats["data"],
                "summary": summary["data"]
            }
            
        return {"metric": metric, "data": "Metric not implemented yet"}


def bulk_update_tickets(operation: str, criteria: str = "", new_status: str = ""):
    """Perform bulk operations on tickets."""
    with httpx.Client() as client:
        # Get all customers to iterate through their tickets
        customers_response = client.get(f"{API_BASE}/customers", timeout=10)
        customers = customers_response.json()
        
        updated_count = 0
        
        if operation == "close_resolved":
            # This is a mock operation - in real system would check ticket content/notes
            for customer in customers:
                tickets_response = client.get(
                    f"{API_BASE}/tickets",
                    params={"customer_id": customer["id"], "status": "open"},
                    timeout=10
                )
                tickets = tickets_response.json()
                # Mock: close tickets older than a certain date (simplified)
                for ticket in tickets[:2]:  # Close first 2 open tickets as demo
                    # In real system, would call UPDATE endpoint
                    updated_count += 1
            
            return {
                "operation": operation,
                "updated_count": updated_count,
                "message": f"Closed {updated_count} resolved tickets"
            }
        
        return {
            "operation": operation,
            "updated_count": 0,
            "message": f"Operation '{operation}' not fully implemented yet"
        }


async def create_visualization(chart_type: str, data_query: str, title: str = "", description: str = ""):
    """Create dynamic visualizations based on user queries."""
    with httpx.Client() as client:
        # Determine what data to fetch based on the query
        chart_data = None
        chart_config = None
        
        try:
            if "customer" in data_query.lower() and ("ticket" in data_query.lower() or "activity" in data_query.lower()):
                # Customer activity/ticket data
                customers_response = client.get(f"{API_BASE}/customers", timeout=10)
                customers = customers_response.json()
                
                customer_data = []
                for customer in customers[:8]:  # Top 8 for readability
                    tickets_response = client.get(
                        f"{API_BASE}/tickets",
                        params={"customer_id": customer["id"]},
                        timeout=10
                    )
                    ticket_count = len(tickets_response.json())
                    customer_data.append({
                        "label": customer["name"].split()[0],  # First name only
                        "value": ticket_count,
                        "fullName": customer["name"]
                    })
                
                # Sort by value (ticket count)
                customer_data.sort(key=lambda x: x["value"], reverse=True)
                
                if chart_type in ["bar", "column"]:
                    chart_config = {
                        "type": "bar",
                        "data": {
                            "labels": [item["label"] for item in customer_data],
                            "datasets": [{
                                "label": "Tickets",
                                "data": [item["value"] for item in customer_data],30
                                "backgroundColor": [
                                    "rgba(79, 70, 229, 0.8)",
                                    "rgba(124, 58, 237, 0.8)", 
                                    "rgba(236, 72, 153, 0.8)",
                                    "rgba(34, 197, 94, 0.8)",
                                    "rgba(249, 115, 22, 0.8)",
                                    "rgba(59, 130, 246, 0.8)",
                                    "rgba(168, 85, 247, 0.8)",
                                    "rgba(244, 63, 94, 0.8)"
                                ],
                                "borderColor": [
                                    "rgba(79, 70, 229, 1)",
                                    "rgba(124, 58, 237, 1)", 
                                    "rgba(236, 72, 153, 1)",
                                    "rgba(34, 197, 94, 1)",
                                    "rgba(249, 115, 22, 1)",
                                    "rgba(59, 130, 246, 1)",
                                    "rgba(168, 85, 247, 1)",
                                    "rgba(244, 63, 94, 1)"
                                ],
                                "borderWidth": 2,
                                "borderRadius": 8
                            }]
                        },
                        "options": {
                            "responsive": True,
                            "plugins": {
                                "title": {
                                    "display": True,
                                    "text": title or "Customer Activity",
                                    "color": "#f1f5f9",
                                    "font": {"size": 16}
                                },
                                "legend": {
                                    "labels": {
                                        "color": "#f1f5f9"
                                    }
                                }
                            },
                            "scales": {
                                "y": {
                                    "ticks": {"color": "#94a3b8"},
                                    "grid": {"color": "rgba(148, 163, 184, 0.1)"}
                                },
                                "x": {
                                    "ticks": {"color": "#94a3b8"},
                                    "grid": {"color": "rgba(148, 163, 184, 0.1)"}
                                }
                            }
                        }
                    }
                    
                elif chart_type in ["pie", "doughnut"]:
                    chart_config = {
                        "type": "doughnut",
                        "data": {
                            "labels": [item["label"] for item in customer_data[:6]],  # Top 6 for pie
                            "datasets": [{
                                "data": [item["value"] for item in customer_data[:6]],
                                "backgroundColor": [
                                    "rgba(79, 70, 229, 0.8)",
                                    "rgba(124, 58, 237, 0.8)", 
                                    "rgba(236, 72, 153, 0.8)",
                                    "rgba(34, 197, 94, 0.8)",
                                    "rgba(249, 115, 22, 0.8)",
                                    "rgba(59, 130, 246, 0.8)"
                                ],
                                "borderColor": [
                                    "rgba(79, 70, 229, 1)",
                                    "rgba(124, 58, 237, 1)", 
                                    "rgba(236, 72, 153, 1)",
                                    "rgba(34, 197, 94, 1)",
                                    "rgba(249, 115, 22, 1)",
                                    "rgba(59, 130, 246, 1)"
                                ],
                                "borderWidth": 2
                            }]
                        },
                        "options": {
                            "responsive": True,
                            "plugins": {
                                "title": {
                                    "display": True,
                                    "text": title or "Customer Distribution",
                                    "color": "#f1f5f9",
                                    "font": {"size": 16}
                                },
                                "legend": {
                                    "labels": {
                                        "color": "#f1f5f9"
                                    }
                                }
                            }
                        }
                    }
            
            elif "ticket" in data_query.lower() and ("status" in data_query.lower() or "resolution" in data_query.lower()):
                # Ticket status/resolution data
                customers_response = client.get(f"{API_BASE}/customers", timeout=10)
                customers = customers_response.json()
                
                total_open = 0
                total_closed = 0
                for customer in customers:
                    open_tickets = client.get(
                        f"{API_BASE}/tickets",30
                        params={"customer_id": customer["id"], "status": "open"},
                        timeout=10
                    ).json()
                    closed_tickets = client.get(
                        f"{API_BASE}/tickets", 
                        params={"customer_id": customer["id"], "status": "closed"},
                        timeout=10
                    ).json()
                    total_open += len(open_tickets)
                    total_closed += len(closed_tickets)
                
                chart_config = {
                    "type": "doughnut",
                    "data": {
                        "labels": ["Open Tickets", "Closed Tickets"],
                        "datasets": [{
                            "data": [total_open, total_closed],
                            "backgroundColor": [
                                "rgba(249, 115, 22, 0.8)",
                                "rgba(34, 197, 94, 0.8)"
                            ],
                            "borderColor": [
                                "rgba(249, 115, 22, 1)",
                                "rgba(34, 197, 94, 1)"
                            ],
                            "borderWidth": 2
                        }]
                    },
                    "options": {
                        "responsive": True,
                        "plugins": {
                            "title": {
                                "display": True,
                                "text": title or "Ticket Status Distribution",
                                "color": "#f1f5f9",
                                "font": {"size": 16}
                            },
                            "legend": {
                                "labels": {
                                    "color": "#f1f5f9"
                                }
                            }
                        }
                    }
                }
            
            elif "trend" in data_query.lower() or "time" in data_query.lower():
                # Mock time-series data for trends
                months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
                ticket_data = [12, 19, 15, 22, 18, 25]  # Mock trend data
                
                chart_config = {
                    "type": "line",
                    "data": {
                        "labels": months,
                        "datasets": [{
                            "label": "Tickets Created",
                            "data": ticket_data,
                            "borderColor": "rgba(79, 70, 229, 1)",
                            "backgroundColor": "rgba(79, 70, 229, 0.1)",
                            "borderWidth": 3,
                            "fill": True,
                            "tension": 0.4
                        }]
                    },
                    "options": {
                        "responsive": True,
                        "plugins": {
                            "title": {
                                "display": True,
                                "text": title or "Ticket Trends Over Time",
                                "color": "#f1f5f9",
                                "font": {"size": 16}
                            },
                            "legend": {
                                "labels": {
                                    "color": "#f1f5f9"
                                }
                            }
                        },
                        "scales": {
                            "y": {
                                "ticks": {"color": "#94a3b8"},
                                "grid": {"color": "rgba(148, 163, 184, 0.1)"}
                            },
                            "x": {
                                "ticks": {"color": "#94a3b8"},
                                "grid": {"color": "rgba(148, 163, 184, 0.1)"}
                            }
                        }
                    }
                }
            
            else:
                # Default: customer ticket counts
                return await create_visualization("bar", "customer ticket activity", title, description)
            
            # Send chart via WebSocket
            intent = {
                "type": "render_chart",
                "chartConfig": chart_config,
                "containerId": "dynamic-chart",
                "title": title,
                "description": description
            }
            
            result = await emit_intent(intent)
            
            return {
                "status": "success",
                "chart_type": chart_type,
                "data_query": data_query,
                "title": title,
                "intent_result": result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create visualization: {str(e)}",
                "chart_type": chart_type,
                "data_query": data_query
            }


def generate_report(report_type: str, date_range: str = ""):
    """Generate various types of reports using comprehensive analytics."""
    with httpx.Client() as client:
        if report_type == "daily_summary":
            # Get comprehensive analytics summary
            response = client.get(f"{API_BASE}/analytics/summary", timeout=10)
            summary_data = response.json()
            
            return {
                "report_type": report_type,
                "data": {
                    "date": "today",
                    "customers": summary_data["customers"],
                    "tickets": summary_data["tickets"], 
                    "health_distribution": summary_data["health_distribution"],
                    "recent_activity": summary_data["recent_activity"][:5]
                }
            }
        
        elif report_type == "customer_health":
            # Get detailed customer health analysis
            customers = client.get(f"{API_BASE}/customers", timeout=10).json()
            health_data = []
            
            for customer in customers:
                # Use the actual health score from the database
                health_score = customer.get("health_score", 75)
                lifecycle_stage = customer.get("lifecycle_stage", "prospect")
                mrr = customer.get("mrr", 0)
                
                if health_score >= 90:
                    health_status = "Excellent"
                elif health_score >= 75:
                    health_status = "Good" 
                elif health_score >= 60:
                    health_status = "Fair"
                else:
                    health_status = "Needs Attention"
                
                # Get actual ticket count
                open_tickets = client.get(
                    f"{API_BASE}/tickets",
                    params={"customer_id": customer["id"], "status": "open"},
                    timeout=10
                ).json()
                
                health_data.append({
                    "customer": customer["name"],
                    "health_score": health_score,
                    "health_status": health_status,
                    "lifecycle_stage": lifecycle_stage,
                    "mrr": mrr,
                    "open_tickets": len(open_tickets),
                    "industry": customer.get("industry", "Unknown"),
                    "plan_type": customer.get("plan_type", "Unknown"),
                    "region": customer.get("region", "Unknown")
                })
            
            return {
                "report_type": report_type,
                "data": health_data
            }
        
        elif report_type == "weekly_summary":
            # Comprehensive weekly business report
            summary = client.get(f"{API_BASE}/analytics/summary", timeout=10).json()
            revenue = client.get(f"{API_BASE}/analytics/revenue", timeout=10).json()
            support = client.get(f"{API_BASE}/analytics/support", timeout=10).json()
            
            return {
                "report_type": report_type,
                "data": {
                    "period": "weekly",
                    "customer_metrics": summary["customers"],
                    "ticket_metrics": summary["tickets"],
                    "revenue_analysis": revenue,
                    "support_metrics": support,
                    "key_insights": _generate_insights(summary, revenue, support)
                }
            }
        
        elif report_type == "ticket_analysis":
            # Detailed ticket analytics
            support_data = client.get(f"{API_BASE}/analytics/support", timeout=10).json()
            
            return {
                "report_type": report_type,
                "data": {
                    "ticket_distribution": support_data["ticket_matrix"],
                    "team_performance": support_data["team_performance"],
                    "sla_compliance": support_data["sla_compliance"],
                    "recommendations": _generate_support_recommendations(support_data)
                }
            }
        
        return {
            "report_type": report_type,
            "data": f"Report type '{report_type}' not implemented yet"
        }


def _generate_insights(summary, revenue, support):
    """Generate business insights from analytics data."""
    insights = []
    
    # Customer growth insights
    trial_customers = summary["customers"]["trial_customers"] 
    paying_customers = summary["customers"]["paying_customers"]
    churn_risk = summary["customers"]["churn_risk_customers"]
    
    if trial_customers > 5:
        insights.append(f"Strong trial pipeline with {trial_customers} prospects")
    
    if churn_risk > 2:
        insights.append(f"ALERT: {churn_risk} customers at churn risk - immediate action needed")
    
    # Revenue insights
    total_mrr = summary["customers"]["total_mrr"]
    if total_mrr > 50000:
        insights.append(f"Strong MRR performance: ${total_mrr:,}/month")
    
    # Support insights
    sla_compliance = support["sla_compliance"]["compliance_rate"]
    if sla_compliance < 95:
        insights.append(f"SLA compliance at {sla_compliance}% - below target")
    
    # Critical tickets
    critical_tickets = summary["tickets"]["critical_tickets"]
    if critical_tickets > 0:
        insights.append(f"URGENT: {critical_tickets} critical tickets require immediate attention")
    
    return insights


def _generate_support_recommendations(support_data):
    """Generate support recommendations based on metrics."""
    recommendations = []
    
    # SLA compliance recommendations
    compliance_rate = support_data["sla_compliance"]["compliance_rate"]
    if compliance_rate < 95:
        recommendations.append("Improve SLA compliance by optimizing ticket routing and response times")
    
    # Team performance recommendations
    team_performance = support_data["team_performance"]
    for member in team_performance:
        if member["assigned_tickets"] > 0:
            resolution_rate = (member["resolved_tickets"] / member["assigned_tickets"]) * 100
            if resolution_rate < 70:
                recommendations.append(f"Provide additional training for {member['name']} - low resolution rate")
    
    return recommendations


# Workflow Engine
workflow_state = {}


def execute_workflow(workflow_name: str, context: dict = None):
    """Execute a predefined multi-step workflow."""
    context = context or {}
    workflow_id = f"{workflow_name}_{hash(str(context))}"
    
    if workflow_name == "customer_onboarding":
        return _customer_onboarding_workflow(workflow_id, context)
    elif workflow_name == "ticket_escalation":
        return _ticket_escalation_workflow(workflow_id, context)
    elif workflow_name == "weekly_report":
        return _weekly_report_workflow(workflow_id, context)
    elif workflow_name == "customer_health_check":
        return _customer_health_check_workflow(workflow_id, context)
    
    return {"error": f"Unknown workflow: {workflow_name}"}


def workflow_decision(condition: str, data: dict = None, options: list = None):
    """Make a decision in a workflow based on conditions."""
    data = data or {}
    options = options or []
    
    # Simple decision logic - in real system would be more sophisticated
    if "high_value" in condition.lower():
        # Check if customer has indicators of high value
        ticket_count = data.get("ticket_count", 0)
        email_domain = data.get("email", "").split("@")[-1] if data.get("email") else ""
        
        # Mock decision logic
        if ticket_count > 3 or any(domain in email_domain.lower() for domain in ["enterprise", "corp", "inc"]):
            return {"decision": "premium", "reason": "High-value customer detected"}
        else:
            return {"decision": "standard", "reason": "Standard customer profile"}
    
    elif "sla_critical" in condition.lower():
        days_old = data.get("days_old", 0)
        priority = data.get("priority", "normal")
        
        if days_old > 7 or priority == "high":
            return {"decision": "escalate", "reason": "SLA breach risk detected"}
        elif days_old > 3:
            return {"decision": "monitor", "reason": "Approaching SLA limit"}
        else:
            return {"decision": "continue", "reason": "Within SLA bounds"}
    
    # Default decision
    if options:
        return {"decision": options[0], "reason": "Default option selected"}
    
    return {"decision": "unknown", "reason": f"Could not evaluate condition: {condition}"}


def set_workflow_state(key: str, value: dict):
    """Store workflow state data."""
    workflow_state[key] = value
    return {"status": "stored", "key": key}


def get_workflow_state(key: str):
    """Retrieve workflow state data."""
    return workflow_state.get(key, {})


def _customer_onboarding_workflow(workflow_id: str, context: dict):
    """Customer onboarding workflow with decision points."""
    customer_name = context.get("customer_name", "Unknown Customer")
    customer_email = context.get("customer_email", "")
    
    steps = []
    
    # Step 1: Create customer record
    try:
        customer_data = create_customer(customer_name, customer_email, "standard")
        customer_id = customer_data.get("id", f"mock_{hash(customer_name)}")
        steps.append(f"✓ Created customer record for {customer_name}")
        
        # Step 2: Decision point - check if high-value customer
        decision_result = workflow_decision("high_value_check", {
            "email": customer_email,
            "ticket_count": 0
        }, ["premium", "standard"])
        
        if decision_result["decision"] == "premium":
            # Premium path
            steps.append(f"✓ Identified as premium customer: {decision_result['reason']}")
            schedule_followup(customer_id, 1, "call", "Welcome call for premium customer")
            steps.append("✓ Scheduled premium welcome call within 24 hours")
            
            # Create priority ticket
            create_note("onboarding_ticket", f"Premium onboarding for {customer_name} - expedited setup")
            steps.append("✓ Created premium onboarding ticket")
            
        else:
            # Standard path  
            steps.append(f"✓ Processing as standard customer: {decision_result['reason']}")
            send_email(customer_email, "Welcome to our service", f"Welcome {customer_name}! We'll be in touch soon.")
            steps.append("✓ Sent welcome email")
            
            schedule_followup(customer_id, 3, "email", "Follow-up email for standard customer")
            steps.append("✓ Scheduled follow-up email in 3 days")
        
        # Step 3: Schedule health check
        schedule_followup(customer_id, 7, "check-in", "One week health check")
        steps.append("✓ Scheduled 7-day health check")
        
        return {
            "workflow": "customer_onboarding",
            "status": "completed",
            "customer_id": customer_id,
            "steps": steps,
            "path": decision_result["decision"]
        }
        
    except Exception as e:
        return {
            "workflow": "customer_onboarding", 
            "status": "error",
            "error": str(e),
            "steps": steps
        }


def _ticket_escalation_workflow(workflow_id: str, context: dict):
    """Ticket escalation workflow with SLA checking."""
    steps = []
    escalated_count = 0
    monitored_count = 0
    
    try:
        # Get all customers and their tickets
        customers_response = get_customer_stats("all")
        customers = customers_response.get("ticket_counts", [])
        
        steps.append("✓ Retrieved customer ticket data")
        
        for customer_data in customers:
            customer_name = customer_data["customer"]
            
            # Mock: Check tickets for this customer
            tickets = list_tickets("mock_customer_id", "open")  # Simplified
            
            for i, ticket in enumerate(tickets[:2]):  # Limit for demo
                # Mock SLA check
                sla_result = check_sla_status(ticket.get("id", f"ticket_{i}"))
                
                decision = workflow_decision("sla_critical", {
                    "days_old": sla_result.get("days_old", 0),
                    "priority": ticket.get("priority", "normal")
                })
                
                if decision["decision"] == "escalate":
                    assign_ticket(ticket.get("id"), "manager")
                    steps.append(f"🚨 Escalated ticket for {customer_name}: {decision['reason']}")
                    escalated_count += 1
                    
                elif decision["decision"] == "monitor":
                    assign_ticket(ticket.get("id"), "senior_support")  
                    steps.append(f"⚠️  Monitoring ticket for {customer_name}: {decision['reason']}")
                    monitored_count += 1
                    
                else:
                    steps.append(f"✓ Ticket for {customer_name} within SLA")
        
        # Summary email
        if escalated_count > 0 or monitored_count > 0:
            summary = f"Escalation Summary: {escalated_count} escalated, {monitored_count} monitoring"
            send_email("manager@company.com", "Ticket Escalation Report", summary)
            steps.append("✓ Sent escalation summary to management")
        
        return {
            "workflow": "ticket_escalation",
            "status": "completed", 
            "escalated_count": escalated_count,
            "monitored_count": monitored_count,
            "steps": steps
        }
        
    except Exception as e:
        return {
            "workflow": "ticket_escalation",
            "status": "error",
            "error": str(e),
            "steps": steps
        }


def _weekly_report_workflow(workflow_id: str, context: dict):
    """Weekly report generation with trend analysis."""
    steps = []
    
    try:
        # Step 1: Gather metrics
        daily_report = generate_report("daily_summary")
        health_report = generate_report("customer_health") 
        stats = get_customer_stats("all")
        
        steps.append("✓ Gathered business metrics")
        
        # Step 2: Analyze trends (mock trend detection)
        daily_data = daily_report.get("data", {})
        health_data = health_report.get("data", [])
        
        open_tickets = daily_data.get("open_tickets", 0)
        total_customers = daily_data.get("total_customers", 0)
        
        # Decision point: Are there concerning trends?
        decision = workflow_decision("trend_analysis", {
            "open_ticket_ratio": open_tickets / max(total_customers, 1),
            "unhealthy_customers": len([c for c in health_data if c.get("health_status") == "Needs Attention"])
        })
        
        steps.append("✓ Analyzed trends and patterns")
        
        # Step 3: Generate recommendations based on analysis
        recommendations = []
        action_items = []
        
        if open_tickets > total_customers * 0.5:  # More than 0.5 tickets per customer
            recommendations.append("High ticket volume detected - consider additional support staff")
            action_items.append("Schedule team capacity review meeting")
            
        unhealthy_count = len([c for c in health_data if c.get("health_status") == "Needs Attention"])
        if unhealthy_count > 0:
            recommendations.append(f"{unhealthy_count} customers need immediate attention")
            action_items.append("Review customer health issues with account managers")
        
        # Step 4: Compile comprehensive report
        report_data = {
            "period": "Weekly Report",
            "metrics": daily_data,
            "customer_health": health_data,
            "recommendations": recommendations,
            "action_items": action_items,
            "generated_at": "now"
        }
        
        steps.append("✓ Compiled comprehensive weekly report")
        
        # Step 5: Schedule actions if needed
        if action_items:
            for action in action_items:
                schedule_followup("management", 1, "review", action)
            steps.append(f"✓ Scheduled {len(action_items)} follow-up actions")
        
        # Step 6: Send report
        report_summary = f"Weekly Report: {total_customers} customers, {open_tickets} open tickets"
        if recommendations:
            report_summary += f", {len(recommendations)} recommendations"
            
        send_email("team@company.com", "Weekly Business Report", report_summary)
        steps.append("✓ Sent weekly report to team")
        
        return {
            "workflow": "weekly_report",
            "status": "completed",
            "report_data": report_data,
            "steps": steps
        }
        
    except Exception as e:
        return {
            "workflow": "weekly_report",
            "status": "error", 
            "error": str(e),
            "steps": steps
        }


def _customer_health_check_workflow(workflow_id: str, context: dict):
    """Customer health check workflow with proactive actions."""
    steps = []
    actions_taken = 0
    
    try:
        # Get customer health data
        health_report = generate_report("customer_health")
        health_data = health_report.get("data", [])
        
        steps.append("✓ Retrieved customer health data")
        
        for customer in health_data:
            customer_name = customer["customer"]
            health_status = customer["health_status"] 
            open_tickets = customer["open_tickets"]
            
            # Decision point: What action to take based on health?
            if health_status == "Needs Attention":
                # Critical path
                assign_ticket("priority_review", "manager")
                schedule_followup("mock_id", 1, "call", f"Urgent review for {customer_name}")
                steps.append(f"🚨 Critical: Scheduled urgent review for {customer_name}")
                actions_taken += 1
                
            elif health_status == "Fair" and open_tickets > 3:
                # Monitor path
                schedule_followup("mock_id", 2, "check-in", f"Health check for {customer_name}")
                steps.append(f"⚠️  Monitoring: Scheduled check-in for {customer_name}")
                actions_taken += 1
                
            elif health_status == "Excellent":
                # Success story path
                steps.append(f"✅ {customer_name} showing excellent health")
                
            else:
                steps.append(f"✓ {customer_name} health status: {health_status}")
        
        # Summary actions
        if actions_taken > 0:
            summary = f"Customer Health Summary: {actions_taken} proactive actions taken"
            send_email("management@company.com", "Customer Health Alert", summary)
            steps.append("✓ Sent health summary to management")
        
        return {
            "workflow": "customer_health_check",
            "status": "completed",
            "actions_taken": actions_taken,
            "health_summary": health_data,
            "steps": steps
        }
        
    except Exception as e:
        return {
            "workflow": "customer_health_check",
            "status": "error",
            "error": str(e),
            "steps": steps
        }


def create_customer(name: str, email: str = None, priority: str = "standard"):
    """Create a new customer in the system."""
    # Mock customer creation
    customer_id = f"cust_{hash(name + str(email))}"
    
    return {
        "id": customer_id,
        "name": name,
        "email": email,
        "priority": priority,
        "status": "created",
        "created_at": "now"
    }


def schedule_followup(customer_id: str, days: int, task_type: str, description: str = ""):
    """Schedule a follow-up action for a customer."""
    followup_id = f"followup_{hash(customer_id + str(days))}"
    
    return {
        "id": followup_id,
        "customer_id": customer_id,
        "scheduled_date": f"now + {days} days",
        "task_type": task_type,
        "description": description,
        "status": "scheduled"
    }


def check_sla_status(ticket_id: str):
    """Check if a ticket is compliant with SLA requirements."""
    # Mock SLA check
    mock_age = hash(ticket_id) % 10  # Random age between 0-9 days
    
    return {
        "ticket_id": ticket_id,
        "days_old": mock_age,
        "sla_limit": 5,
        "status": "compliant" if mock_age <= 5 else "breach_risk",
        "urgency": "high" if mock_age > 7 else "normal"
    }


def assign_ticket(ticket_id: str, assignee: str):
    """Assign a ticket to a team member."""
    return {
        "ticket_id": ticket_id,
        "assigned_to": assignee,
        "assigned_at": "now",
        "status": "assigned"
    }
