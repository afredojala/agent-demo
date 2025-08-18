# ABOUTME: Database seeding script for the mini-CRM system
# ABOUTME: Creates SQLite tables and populates with sample data
import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.getenv("DB_PATH", "backend/db.sqlite3")


def init_database():
    conn = sqlite3.connect(DB_PATH)

    # Create tables
    conn.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            created_at TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL,
            body TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (ticket_id) REFERENCES tickets (id)
        )
    """)

    # Clear existing data
    conn.execute("DELETE FROM notes")
    conn.execute("DELETE FROM tickets")
    conn.execute("DELETE FROM customers")

    # Insert sample customers
    customers = [
        ("cust_1", "Acme Corp", "contact@acme.com"),
        ("cust_2", "TechCorp Inc", "support@techcorp.com"),
        ("cust_3", "Global Solutions", "help@globalsolutions.com"),
    ]

    conn.executemany(
        "INSERT INTO customers (id, name, email) VALUES (?, ?, ?)", customers
    )

    # Insert sample tickets
    base_date = datetime.now() - timedelta(days=7)
    tickets = [
        (
            "ticket_1",
            "cust_1",
            "Login issues with new system",
            "open",
            (base_date + timedelta(days=1)).isoformat(),
        ),
        (
            "ticket_2",
            "cust_1",
            "Feature request for dashboard",
            "open",
            (base_date + timedelta(days=2)).isoformat(),
        ),
        (
            "ticket_3",
            "cust_1",
            "Bug in payment processing",
            "closed",
            (base_date + timedelta(days=3)).isoformat(),
        ),
        (
            "ticket_4",
            "cust_2",
            "Performance issues on mobile",
            "open",
            (base_date + timedelta(days=4)).isoformat(),
        ),
        (
            "ticket_5",
            "cust_3",
            "Data export not working",
            "open",
            (base_date + timedelta(days=5)).isoformat(),
        ),
    ]

    conn.executemany(
        "INSERT INTO tickets (id, customer_id, title, status, created_at) VALUES (?, ?, ?, ?, ?)",
        tickets,
    )

    # Insert sample notes
    notes = [
        (
            "ticket_1",
            "Initial investigation shows authentication service is down",
            (base_date + timedelta(days=1, hours=2)).isoformat(),
        ),
        (
            "ticket_1",
            "Escalated to infrastructure team",
            (base_date + timedelta(days=1, hours=4)).isoformat(),
        ),
        (
            "ticket_4",
            "Reproduced on iPhone 15, investigating",
            (base_date + timedelta(days=4, hours=1)).isoformat(),
        ),
    ]

    conn.executemany(
        "INSERT INTO notes (ticket_id, body, created_at) VALUES (?, ?, ?)", notes
    )

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


if __name__ == "__main__":
    init_database()
