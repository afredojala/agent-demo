# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an agent-controlled UI demo showcasing OpenAI function calling with dynamic frontend control. The system consists of three main components:

- **Backend**: FastAPI mini-CRM with SQLite (customers, tickets, notes)
- **Agent**: OpenAI function calling system with custom tools and WebSocket UI control
- **Frontend**: React app that responds to agent-controlled view intents via WebSocket

The key innovation is the agent's ability to control the frontend UI through WebSocket "view intents" while executing business tasks.

## Development Commands

### Initial Setup
```bash
# Copy environment template and add OpenAI API key
cp .env.example .env
# Edit .env to add your OPENAI_API_KEY

# Initialize database with seed data
uv run python run_demo.py
```

### Running the Full Demo (requires 4 terminals)
```bash
# Terminal 1: Start FastAPI backend (port 8000)
uv run uvicorn backend.app:app --reload

# Terminal 2: Start WebSocket server (port 8765)
uv run python agent/websocket_server.py

# Terminal 3: Start agent chat server (port 8001)
uv run python agent/chat_server.py

# Terminal 4: Start React frontend (port 3000)
cd frontend && npm install && npm run dev
```

### Individual Component Testing
```bash
# Run backend API only
uv run uvicorn backend.app:app --reload

# Test agent system directly
uv run python agent/crew.py

# Initialize database manually
uv run python -c "from backend.seed import init_database; init_database()"
```

## Architecture Details

### Agent System (`agent/`)
- **crew.py**: Main agent execution loop with OpenAI function calling
- **tools.py**: HTTP client functions for API calls + WebSocket intent emitter
- **openai_client.py**: OpenAI client configuration and tool definitions
- **websocket_server.py**: WebSocket server that broadcasts view intents to frontend

### Backend (`backend/`)
- **app.py**: FastAPI server with CORS, SQLite database, mini-CRM endpoints
- **models.py**: Pydantic models for customers, tickets, notes
- **seed.py**: Database initialization and sample data creation

### Frontend (`frontend/`)
- **React + TypeScript + Vite + Tailwind**
- **agentSocket.ts**: WebSocket client for receiving view intents from agent
- **views/**: TriageBoard, EntityList, EntityDetail components
- **components/**: ChatInterface for user interaction

### Communication Flow
1. Agent executes task using OpenAI function calling
2. Agent calls API tools to manipulate data (search customers, create notes, etc.)
3. Agent emits "view intents" via WebSocket to control frontend UI
4. Frontend receives WebSocket messages and updates views accordingly
5. User sees dynamic UI changes as agent completes business tasks

## Environment Configuration

### Required Environment Variables (.env)
```
OPENAI_API_KEY=your_openai_api_key_here
DB_PATH=backend/db.sqlite3
API_BASE=http://localhost:8000
AGENT_WS=ws://localhost:8765
VITE_AGENT_WS=ws://localhost:8765
```

### Port Configuration
- **8000**: FastAPI backend API
- **8765**: WebSocket server for agent-frontend communication  
- **3000**: React frontend development server

## Key Technical Concepts

### Agent Tools
The agent has access to these custom tools:

#### Core Business Tools
- `search_customers(name, location, criteria)`: Search customers with advanced filtering
- `list_tickets(customer_id, status)`: Get tickets for a customer
- `create_note(ticket_id, body)`: Add note to ticket
- `send_email(to, subject, body)`: Send email (mock)
- `get_customer_stats(metric)`: Get customer analytics and statistics
- `bulk_update_tickets(operation, criteria)`: Perform bulk operations on tickets
- `generate_report(report_type, date_range)`: Generate various business reports

#### Workflow Engine Tools
- `execute_workflow(workflow_name, context)`: Execute predefined multi-step workflows
- `workflow_decision(condition, data, options)`: Make branching decisions in workflows
- `set_workflow_state(key, value)`: Store workflow state data
- `get_workflow_state(key)`: Retrieve workflow context
- `create_customer(name, email, priority)`: Create new customers
- `schedule_followup(customer_id, days, task_type)`: Schedule future actions
- `check_sla_status(ticket_id)`: Check SLA compliance
- `assign_ticket(ticket_id, assignee)`: Assign tickets to team members

#### UI Control
- `emit_intent(intent)`: Control frontend view via WebSocket

### Available Views
The agent can control these frontend views:
- **triage**: Kanban-style ticket management board
- **customer-list**: Customer browsing and search interface
- **dashboard**: Customer activity dashboard with stats
- **analytics**: Charts and metrics visualization
- **timeline**: Chronological activity timeline
- **calendar**: Scheduled events and deadlines
- **workflow**: Multi-step workflow execution and monitoring

### WebSocket View Intents
Agent sends JSON messages to control frontend:
```json
{"type": "set_view", "view_id": "analytics"}
{"type": "add_panel", "panel": "NotesPanel"}
```

### OpenAI Integration
- Uses `openrouter/openai/gpt-4o` model
- Function calling with custom tool definitions
- Iterative execution loop with tool result feedback

## Available Agent Commands

Users can now interact with the agent using natural language. Example commands:

### Customer Management
- "Show me all customers"
- "Find high activity customers" 
- "Search for customers with open tickets"

### Analytics & Reports
- "Show customer analytics"
- "Generate a daily summary report"
- "Show customer health report"
- "Display ticket statistics"

### Ticket Operations
- "Show Acme's open tickets"
- "Close resolved tickets"
- "Add a note to ticket_1"
- "Escalate old tickets"

### View Navigation  
- "Show dashboard view"
- "Switch to analytics"
- "Display timeline"
- "Open calendar view"
- "Show workflow management"

### Multi-Step Workflows 🚀
- **"Onboard TechCorp as a new customer"**: Full customer onboarding with premium/standard routing
- **"Run ticket escalation workflow"**: Automated SLA checking and escalation decisions
- **"Generate weekly business report"**: Comprehensive reporting with trend analysis and recommendations
- **"Run customer health check workflow"**: Proactive customer health monitoring with automated actions

### Workflow Features
- **Decision Points**: Agent makes intelligent routing decisions based on data
- **Branching Logic**: Different paths based on customer type, SLA status, health metrics
- **State Management**: Workflows maintain context across multiple steps
- **Progress Tracking**: Real-time workflow execution visualization
- **Error Handling**: Graceful failure recovery and status reporting

## Rich Data Architecture

### Comprehensive Customer Profiles
- **12 diverse customers** across industries: Manufacturing, Technology, SaaS, Fintech, Retail, Design, AI/ML
- **Company segments**: Enterprise, Large, Medium, Small with realistic MRR ($300 - $25,000)
- **Lifecycle stages**: Prospects, Trials, Customers, At-risk, Churn-risk with health scores (45-92)
- **Geographic distribution**: North America, Europe, Asia Pacific with timezones
- **Rich metadata**: Contact persons, phone numbers, websites, plan types

### Realistic Ticket Scenarios  
- **20 detailed tickets** with comprehensive context and business impact
- **Ticket categories**: Bug, Feature Request, Technical Support, Account Issue, Integration, Performance, Security, Training
- **Priority levels**: Low, Medium, High, Critical with SLA breach tracking
- **Ticket lifecycle**: Open, In-Progress, Waiting Customer, Resolved, Closed
- **Team assignments**: 6 team members across Customer Success, Engineering, Sales
- **Rich ticket details**: Descriptions, resolution timelines, satisfaction ratings

### Team & Interaction Data
- **6 team members** with roles, departments, and timezones
- **25+ detailed notes** on tickets with timestamps and authors (internal, customer updates, escalations)
- **15+ customer interactions**: Calls, meetings, emails with business context
- **SLA compliance tracking** with breach indicators and response times
- **Team performance metrics** and ticket assignment tracking

### Advanced Analytics Endpoints
- **`/analytics/summary`**: Customer health, ticket metrics, recent activity
- **`/analytics/revenue`**: Revenue by plan/region/industry with MRR tracking  
- **`/analytics/support`**: Team performance, SLA compliance, ticket matrix
- **Rich business intelligence** with automated insights and recommendations

### Business Scenarios
- **Enterprise customers**: Acme Corp (SSO issues), TechFlow (API scaling), Global Manufacturing (GDPR)
- **At-risk scenarios**: RetailMax (POS integration failure), churn-risk customers with escalations
- **Growth opportunities**: Trial customers, startup onboarding, expansion revenue
- **Real operational issues**: Performance problems, security compliance, billing discrepancies

## Development Notes

- All Python commands should use `uv run` prefix
- Database auto-creates at `backend/db.sqlite3` on first run with comprehensive seed data
- Frontend automatically connects to WebSocket on startup
- Agent supports interactive chat through `/api/chat` endpoint
- Chat interface includes quick action buttons for common tasks
- Agent automatically switches views based on task context
- Rich analytics available at `/analytics/*` endpoints
- No current linting/formatting tools configured - add as needed