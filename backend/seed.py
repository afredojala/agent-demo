# ABOUTME: Database seeding script for the mini-CRM system
# ABOUTME: Creates SQLite tables and populates with comprehensive realistic data
import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.getenv("DB_PATH", "backend/db.sqlite3")


def init_database():
    conn = sqlite3.connect(DB_PATH)

    # Create tables with extended schema
    conn.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            industry TEXT,
            company_size TEXT,
            plan_type TEXT,
            region TEXT,
            contact_person TEXT,
            phone TEXT,
            website TEXT,
            created_at TEXT NOT NULL,
            last_activity TEXT,
            health_score INTEGER DEFAULT 75,
            mrr REAL DEFAULT 0,
            lifecycle_stage TEXT DEFAULT 'prospect'
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'open',
            priority TEXT DEFAULT 'medium',
            category TEXT,
            assigned_to TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            resolved_at TEXT,
            first_response_at TEXT,
            sla_breach BOOLEAN DEFAULT 0,
            satisfaction_rating INTEGER,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL,
            body TEXT NOT NULL,
            author TEXT NOT NULL,
            note_type TEXT DEFAULT 'internal',
            created_at TEXT NOT NULL,
            FOREIGN KEY (ticket_id) REFERENCES tickets (id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS team_members (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            email TEXT,
            department TEXT,
            timezone TEXT DEFAULT 'UTC',
            active BOOLEAN DEFAULT 1
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            interaction_type TEXT NOT NULL,
            subject TEXT,
            details TEXT,
            created_at TEXT NOT NULL,
            created_by TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    """)

    # Clear existing data
    conn.execute("DELETE FROM interactions")
    conn.execute("DELETE FROM notes")
    conn.execute("DELETE FROM tickets")
    conn.execute("DELETE FROM customers")
    conn.execute("DELETE FROM team_members")

    # Insert team members
    team_members = [
        ("tm_1", "Sarah Johnson", "Support Manager", "sarah@company.com", "Customer Success", "EST", 1),
        ("tm_2", "Mike Chen", "Senior Support", "mike@company.com", "Customer Success", "PST", 1),
        ("tm_3", "Emily Rodriguez", "Support Specialist", "emily@company.com", "Customer Success", "CST", 1),
        ("tm_4", "David Kim", "Technical Lead", "david@company.com", "Engineering", "PST", 1),
        ("tm_5", "Lisa Thompson", "Account Manager", "lisa@company.com", "Sales", "EST", 1),
        ("tm_6", "James Wilson", "Support Specialist", "james@company.com", "Customer Success", "GMT", 1),
    ]

    conn.executemany(
        "INSERT INTO team_members (id, name, role, email, department, timezone, active) VALUES (?, ?, ?, ?, ?, ?, ?)", 
        team_members
    )

    # Insert comprehensive customer data
    base_date = datetime.now()
    customers = [
        # Enterprise Customers
        ("cust_1", "Acme Corporation", "contact@acmecorp.com", "Manufacturing", "enterprise", "premium", "North America", 
         "John Mitchell", "+1-555-0101", "www.acmecorp.com", 
         (base_date - timedelta(days=365)).isoformat(), (base_date - timedelta(days=2)).isoformat(), 85, 15000, "customer"),
        
        ("cust_2", "TechFlow Industries", "support@techflow.com", "Technology", "enterprise", "enterprise", "North America",
         "Sarah Chang", "+1-555-0102", "www.techflow.com",
         (base_date - timedelta(days=180)).isoformat(), (base_date - timedelta(days=1)).isoformat(), 92, 25000, "customer"),
        
        ("cust_3", "Global Manufacturing Co", "help@globalmanuf.com", "Manufacturing", "large", "premium", "Europe",
         "Hans Mueller", "+49-555-0103", "www.globalmanuf.com",
         (base_date - timedelta(days=300)).isoformat(), (base_date - timedelta(days=5)).isoformat(), 78, 12000, "customer"),
        
        # Mid-market customers
        ("cust_4", "DataSync Solutions", "admin@datasync.io", "SaaS", "medium", "professional", "North America",
         "Maria Rodriguez", "+1-555-0104", "www.datasync.io",
         (base_date - timedelta(days=120)).isoformat(), (base_date - timedelta(days=3)).isoformat(), 88, 5000, "customer"),
        
        ("cust_5", "CloudFirst Consulting", "team@cloudfirst.com", "Consulting", "medium", "professional", "Asia Pacific",
         "Raj Patel", "+91-555-0105", "www.cloudfirst.com",
         (base_date - timedelta(days=90)).isoformat(), (base_date - timedelta(days=1)).isoformat(), 91, 7500, "customer"),
        
        ("cust_6", "RetailMax Systems", "it@retailmax.com", "Retail", "medium", "professional", "North America",
         "Jennifer Lee", "+1-555-0106", "www.retailmax.com",
         (base_date - timedelta(days=240)).isoformat(), (base_date - timedelta(days=10)).isoformat(), 65, 4500, "at_risk"),
        
        # Small businesses  
        ("cust_7", "StartupOne Inc", "founders@startupone.co", "Fintech", "small", "starter", "North America",
         "Alex Thompson", "+1-555-0107", "www.startupone.co",
         (base_date - timedelta(days=45)).isoformat(), (base_date - timedelta(days=7)).isoformat(), 82, 1500, "customer"),
        
        ("cust_8", "Creative Labs", "hello@creativelabs.design", "Design", "small", "starter", "Europe",
         "Sophie Dubois", "+33-555-0108", "www.creativelabs.design",
         (base_date - timedelta(days=30)).isoformat(), (base_date - timedelta(days=4)).isoformat(), 89, 800, "customer"),
        
        # Prospects and trials
        ("cust_9", "Enterprise Solutions Ltd", "info@entsol.co.uk", "Enterprise Software", "large", "trial", "Europe",
         "Robert Clarke", "+44-555-0109", "www.entsol.co.uk",
         (base_date - timedelta(days=14)).isoformat(), (base_date - timedelta(days=2)).isoformat(), 75, 0, "trial"),
        
        ("cust_10", "InnovateTech", "contact@innovatetech.ai", "AI/ML", "medium", "trial", "Asia Pacific",
         "Yuki Tanaka", "+81-555-0110", "www.innovatetech.ai",
         (base_date - timedelta(days=7)).isoformat(), (base_date - timedelta(days=1)).isoformat(), 88, 0, "trial"),
        
        # Problem customers
        ("cust_11", "LegacySystems Corp", "support@legacysystems.com", "Legacy IT", "large", "premium", "North America",
         "Bob Anderson", "+1-555-0111", "www.legacysystems.com",
         (base_date - timedelta(days=400)).isoformat(), (base_date - timedelta(days=21)).isoformat(), 45, 8000, "churn_risk"),
        
        ("cust_12", "BudgetSoft Inc", "admin@budgetsoft.com", "Software", "small", "starter", "North America",
         "Carol Williams", "+1-555-0112", "www.budgetsoft.com",
         (base_date - timedelta(days=200)).isoformat(), (base_date - timedelta(days=15)).isoformat(), 55, 300, "churn_risk"),
    ]

    conn.executemany(
        """INSERT INTO customers 
           (id, name, email, industry, company_size, plan_type, region, contact_person, phone, website, 
            created_at, last_activity, health_score, mrr, lifecycle_stage) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
        customers
    )

    # Insert comprehensive ticket scenarios
    tickets = []
    ticket_categories = ["Bug", "Feature Request", "Technical Support", "Account Issue", "Integration", "Performance", "Security", "Training"]
    priorities = ["low", "medium", "high", "critical"]
    statuses = ["open", "in_progress", "waiting_customer", "resolved", "closed"]
    
    # Create realistic ticket scenarios for each customer
    ticket_scenarios = [
        # Acme Corporation (Enterprise, Manufacturing)
        ("ticket_1", "cust_1", "SSO Integration Failing", "Critical authentication issue preventing 500+ users from accessing the system", 
         "open", "critical", "Integration", "tm_4", (base_date - timedelta(days=12)).isoformat(), None, None, None, 1, None),
        
        ("ticket_2", "cust_1", "Bulk Data Import Performance", "Monthly inventory import taking 6+ hours, needs optimization",
         "in_progress", "high", "Performance", "tm_2", (base_date - timedelta(days=8)).isoformat(), 
         (base_date - timedelta(days=8, hours=2)).isoformat(), None, None, 0, None),
        
        ("ticket_3", "cust_1", "Custom Dashboard for Manufacturing KPIs", "Request for specialized manufacturing dashboard with OEE metrics",
         "waiting_customer", "medium", "Feature Request", "tm_5", (base_date - timedelta(days=5)).isoformat(),
         (base_date - timedelta(days=5, hours=1)).isoformat(), None, (base_date - timedelta(days=5, hours=3)).isoformat(), 0, None),
        
        # TechFlow Industries (Enterprise, Technology) 
        ("ticket_4", "cust_2", "API Rate Limit Issues", "Hitting API limits during peak usage, need enterprise quotas",
         "resolved", "high", "Technical Support", "tm_4", (base_date - timedelta(days=6)).isoformat(),
         (base_date - timedelta(days=6, hours=1)).isoformat(), (base_date - timedelta(days=4)).isoformat(), 
         (base_date - timedelta(days=6, hours=1)).isoformat(), 0, 5),
        
        ("ticket_5", "cust_2", "Webhook Endpoint Configuration", "Need help setting up webhooks for real-time data sync",
         "closed", "medium", "Integration", "tm_2", (base_date - timedelta(days=15)).isoformat(),
         (base_date - timedelta(days=15, hours=2)).isoformat(), (base_date - timedelta(days=14)).isoformat(),
         (base_date - timedelta(days=15, hours=2)).isoformat(), 0, 4),
        
        # Global Manufacturing Co (Large, Europe) 
        ("ticket_6", "cust_3", "GDPR Compliance Documentation", "Need updated data processing agreements for EU operations",
         "open", "high", "Security", "tm_1", (base_date - timedelta(days=18)).isoformat(), None, None, None, 1, None),
        
        ("ticket_7", "cust_3", "Multi-language Support Issues", "German and French translations missing in new features",
         "in_progress", "medium", "Bug", "tm_3", (base_date - timedelta(days=3)).isoformat(),
         (base_date - timedelta(days=3, hours=4)).isoformat(), None, None, 0, None),
        
        # DataSync Solutions (Medium, SaaS)
        ("ticket_8", "cust_4", "Database Connection Timeouts", "Frequent timeout errors during large data synchronization jobs",
         "open", "high", "Performance", "tm_4", (base_date - timedelta(days=2)).isoformat(), None, None, None, 0, None),
        
        ("ticket_9", "cust_4", "Advanced Filtering Feature", "Request for complex filter combinations in data views",
         "open", "low", "Feature Request", "tm_2", (base_date - timedelta(days=1)).isoformat(), None, None, None, 0, None),
        
        # CloudFirst Consulting (Medium, Asia Pacific)
        ("ticket_10", "cust_5", "Training Session for New Features", "Need training for team on latest platform updates",
         "resolved", "medium", "Training", "tm_6", (base_date - timedelta(days=10)).isoformat(),
         (base_date - timedelta(days=10, hours=1)).isoformat(), (base_date - timedelta(days=7)).isoformat(),
         (base_date - timedelta(days=10, hours=1)).isoformat(), 0, 5),
        
        # RetailMax Systems (At Risk Customer)
        ("ticket_11", "cust_6", "Point of Sale Integration Broken", "POS system not syncing with inventory management",
         "open", "critical", "Integration", "tm_1", (base_date - timedelta(days=25)).isoformat(), None, None, None, 1, None),
        
        ("ticket_12", "cust_6", "Billing Discrepancy", "Invoice shows incorrect usage charges for past 3 months",
         "waiting_customer", "high", "Account Issue", "tm_5", (base_date - timedelta(days=20)).isoformat(),
         (base_date - timedelta(days=20, hours=2)).isoformat(), None, (base_date - timedelta(days=20, hours=2)).isoformat(), 1, None),
        
        # StartupOne Inc (Small, Fintech)
        ("ticket_13", "cust_7", "Payment Gateway Setup", "Help configuring Stripe integration for subscription billing",
         "closed", "medium", "Integration", "tm_2", (base_date - timedelta(days=30)).isoformat(),
         (base_date - timedelta(days=30, hours=1)).isoformat(), (base_date - timedelta(days=28)).isoformat(),
         (base_date - timedelta(days=30, hours=1)).isoformat(), 0, 4),
        
        ("ticket_14", "cust_7", "Mobile App Crashing on iOS", "App crashes when accessing user profile section",
         "in_progress", "high", "Bug", "tm_4", (base_date - timedelta(days=4)).isoformat(),
         (base_date - timedelta(days=4, hours=3)).isoformat(), None, None, 0, None),
        
        # Creative Labs (Small, Design)
        ("ticket_15", "cust_8", "Custom Branding Options", "Want to customize colors and logo in client portals",
         "open", "low", "Feature Request", "tm_3", (base_date - timedelta(days=2)).isoformat(), None, None, None, 0, None),
        
        # Enterprise Solutions Ltd (Trial)
        ("ticket_16", "cust_9", "Enterprise Features Demo", "Need demonstration of advanced security features",
         "open", "medium", "Technical Support", "tm_5", (base_date - timedelta(days=3)).isoformat(), None, None, None, 0, None),
        
        # InnovateTech (Trial)  
        ("ticket_17", "cust_10", "ML Pipeline Integration", "Assistance with machine learning workflow integration",
         "in_progress", "high", "Integration", "tm_4", (base_date - timedelta(days=2)).isoformat(),
         (base_date - timedelta(days=2, hours=1)).isoformat(), None, None, 0, None),
        
        # LegacySystems Corp (Churn Risk)
        ("ticket_18", "cust_11", "Migration Timeline Concerns", "Worried about migration timeline and business disruption",
         "open", "critical", "Account Issue", "tm_1", (base_date - timedelta(days=30)).isoformat(), None, None, None, 1, None),
        
        ("ticket_19", "cust_11", "Legacy System Compatibility", "Old mainframe systems not integrating properly",
         "waiting_customer", "high", "Integration", "tm_4", (base_date - timedelta(days=45)).isoformat(),
         (base_date - timedelta(days=45, hours=4)).isoformat(), None, (base_date - timedelta(days=45, hours=6)).isoformat(), 1, None),
        
        # BudgetSoft Inc (Churn Risk)
        ("ticket_20", "cust_12", "Price Increase Notification", "Concerned about upcoming price changes and alternatives",
         "open", "high", "Account Issue", "tm_1", (base_date - timedelta(days=7)).isoformat(), None, None, None, 0, None),
    ]

    conn.executemany(
        """INSERT INTO tickets 
           (id, customer_id, title, description, status, priority, category, assigned_to, created_at, 
            updated_at, resolved_at, first_response_at, sla_breach, satisfaction_rating) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        ticket_scenarios
    )

    # Insert comprehensive notes with authors
    notes = [
        # SSO Integration Issue (Critical)
        ("ticket_1", "Customer reports 500+ users unable to authenticate since morning. Checking SAML configuration.", "tm_4", "internal", (base_date - timedelta(days=12, hours=-1)).isoformat()),
        ("ticket_1", "SAML endpoint is responding but certificates appear to be expired. Escalating to security team.", "tm_4", "internal", (base_date - timedelta(days=12, hours=-3)).isoformat()),
        ("ticket_1", "Security team confirms certificates expired at midnight. Working on renewal process.", "tm_1", "internal", (base_date - timedelta(days=12, hours=-6)).isoformat()),
        ("ticket_1", "Temporary workaround deployed. Users can login via backup auth method. Full fix ETA 4 hours.", "tm_4", "customer_update", (base_date - timedelta(days=12, hours=-8)).isoformat()),
        
        # Bulk Data Import Performance
        ("ticket_2", "Customer's monthly inventory import now taking 6+ hours instead of usual 2 hours. Investigating.", "tm_2", "internal", (base_date - timedelta(days=8, hours=-1)).isoformat()),
        ("ticket_2", "Database query analysis shows inefficient joins on large tables. Recommending index optimization.", "tm_2", "internal", (base_date - timedelta(days=8, hours=-4)).isoformat()),
        ("ticket_2", "Applied database optimizations. Import time reduced to 3 hours. Customer testing ongoing.", "tm_2", "customer_update", (base_date - timedelta(days=7)).isoformat()),
        
        # API Rate Limits (Resolved)
        ("ticket_4", "Customer hitting 10,000 req/hour limit during peak usage. Current usage shows 15,000 req/hour needed.", "tm_4", "internal", (base_date - timedelta(days=6, hours=-1)).isoformat()),
        ("ticket_4", "Upgraded customer to Enterprise API tier (50,000 req/hour). Monitoring usage patterns.", "tm_4", "customer_update", (base_date - timedelta(days=6, hours=-2)).isoformat()),
        ("ticket_4", "Usage has stabilized. Customer confirms no more rate limit errors. Marking as resolved.", "tm_4", "internal", (base_date - timedelta(days=4)).isoformat()),
        
        # GDPR Compliance (Long-standing)
        ("ticket_6", "Customer needs updated DPA for Q4 compliance audit. Legal team reviewing requirements.", "tm_1", "internal", (base_date - timedelta(days=18, hours=-2)).isoformat()),
        ("ticket_6", "Legal has reviewed EU requirements. DPA template needs updates for cross-border data transfers.", "tm_1", "internal", (base_date - timedelta(days=15)).isoformat()),
        ("ticket_6", "Waiting for final approval from compliance team. Expected completion next week.", "tm_1", "customer_update", (base_date - timedelta(days=10)).isoformat()),
        
        # POS Integration Issue (At-risk customer)
        ("ticket_11", "Critical integration failure affecting customer's retail operations. Immediate attention required.", "tm_1", "internal", (base_date - timedelta(days=25, hours=-1)).isoformat()),
        ("ticket_11", "API logs show authentication errors from POS system. Customer may have changed credentials.", "tm_1", "internal", (base_date - timedelta(days=25, hours=-4)).isoformat()),
        ("ticket_11", "Customer confirmed no credential changes. Investigating API endpoint compatibility.", "tm_1", "customer_update", (base_date - timedelta(days=24)).isoformat()),
        ("ticket_11", "POS vendor updated their API without notice. Working on compatibility patch. ETA 48 hours.", "tm_1", "internal", (base_date - timedelta(days=20)).isoformat()),
        ("ticket_11", "Customer expressing frustration with delayed resolution. Escalating to management.", "tm_1", "escalation", (base_date - timedelta(days=15)).isoformat()),
        
        # Billing Discrepancy  
        ("ticket_12", "Customer disputes usage charges for past 3 months. Reviewing billing data and usage logs.", "tm_5", "internal", (base_date - timedelta(days=20, hours=-2)).isoformat()),
        ("ticket_12", "Found billing system bug that double-counted API calls for this customer. Calculating refund.", "tm_5", "internal", (base_date - timedelta(days=18)).isoformat()),
        ("ticket_12", "Refund amount calculated: $2,340. Awaiting customer approval before processing.", "tm_5", "customer_update", (base_date - timedelta(days=15)).isoformat()),
        
        # Mobile App Crash
        ("ticket_14", "iOS app crash reported on user profile section. Reproduced on iOS 17.1, iPhone 14 Pro.", "tm_4", "internal", (base_date - timedelta(days=4, hours=-2)).isoformat()),
        ("ticket_14", "Memory leak identified in profile image loading. Fix developed, testing in progress.", "tm_4", "internal", (base_date - timedelta(days=3)).isoformat()),
        ("ticket_14", "Fix ready for deployment. Customer to receive update via TestFlight tomorrow.", "tm_4", "customer_update", (base_date - timedelta(days=2)).isoformat()),
        
        # Migration Concerns (Churn risk)
        ("ticket_18", "Customer concerned about migration timeline impacting Q4 operations. Need detailed project plan.", "tm_1", "internal", (base_date - timedelta(days=30, hours=-1)).isoformat()),
        ("ticket_18", "Scheduled call with customer and solutions architect to discuss migration approach.", "tm_1", "customer_update", (base_date - timedelta(days=28)).isoformat()),
        ("ticket_18", "Customer call completed. Agreed on phased migration starting after Q4. Detailed timeline provided.", "tm_1", "internal", (base_date - timedelta(days=25)).isoformat()),
        ("ticket_18", "Customer still expressing concerns. Need executive sponsor involvement.", "tm_1", "escalation", (base_date - timedelta(days=20)).isoformat()),
    ]

    conn.executemany(
        "INSERT INTO notes (ticket_id, body, author, note_type, created_at) VALUES (?, ?, ?, ?, ?)", 
        notes
    )

    # Insert customer interactions (calls, meetings, emails)
    interactions = [
        # Acme Corporation interactions
        ("cust_1", "call", "Quarterly Business Review Q3", "Discussed growth plans, upcoming product launches, and support needs. Very positive feedback on service quality.", (base_date - timedelta(days=30)).isoformat(), "tm_5"),
        ("cust_1", "email", "SSO Configuration Update", "Sent updated SSO configuration guide and security best practices documentation.", (base_date - timedelta(days=20)).isoformat(), "tm_4"),
        ("cust_1", "meeting", "Manufacturing Dashboard Demo", "Demonstrated new OEE tracking features. Customer very interested in implementation.", (base_date - timedelta(days=10)).isoformat(), "tm_5"),
        
        # TechFlow Industries interactions  
        ("cust_2", "call", "API Integration Planning", "Discussed roadmap for new API features and webhook improvements.", (base_date - timedelta(days=25)).isoformat(), "tm_4"),
        ("cust_2", "email", "Enterprise Plan Benefits", "Outlined benefits of Enterprise tier including higher rate limits and priority support.", (base_date - timedelta(days=8)).isoformat(), "tm_5"),
        
        # RetailMax (at-risk) interactions
        ("cust_6", "call", "Emergency Support Call", "Urgent call regarding POS integration failure. Customer very frustrated with timeline.", (base_date - timedelta(days=25)).isoformat(), "tm_1"),
        ("cust_6", "meeting", "Escalation Review", "Management meeting to address ongoing issues and customer concerns.", (base_date - timedelta(days=15)).isoformat(), "tm_1"),
        ("cust_6", "email", "Billing Resolution Update", "Provided update on billing discrepancy investigation and proposed resolution.", (base_date - timedelta(days=10)).isoformat(), "tm_5"),
        
        # Trial customers
        ("cust_9", "call", "Enterprise Trial Kickoff", "Initial call to set up enterprise trial and demonstrate advanced features.", (base_date - timedelta(days=14)).isoformat(), "tm_5"),
        ("cust_10", "meeting", "ML Integration Workshop", "Technical workshop on integrating ML pipelines with our platform.", (base_date - timedelta(days=5)).isoformat(), "tm_4"),
        
        # Churn risk customers
        ("cust_11", "call", "Migration Concerns Discussion", "Detailed discussion about migration timeline and business impact concerns.", (base_date - timedelta(days=28)).isoformat(), "tm_1"),
        ("cust_11", "meeting", "Executive Sponsor Meeting", "C-level meeting to address migration concerns and ensure customer success.", (base_date - timedelta(days=18)).isoformat(), "tm_1"),
        ("cust_12", "call", "Pricing Discussion", "Customer concerned about upcoming price increase. Discussed options and alternatives.", (base_date - timedelta(days=7)).isoformat(), "tm_5"),
    ]

    conn.executemany(
        "INSERT INTO interactions (customer_id, interaction_type, subject, details, created_at, created_by) VALUES (?, ?, ?, ?, ?, ?)",
        interactions
    )

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


if __name__ == "__main__":
    init_database()
