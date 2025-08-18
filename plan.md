Short answer: if by “Codex” you mean the **old OpenAI Codex API/models (code-davinci-002, etc.)**, those were retired—so we can’t build on them today. The modern, supported path is **function/tool calling** with current models (same idea Codex pioneered, but better), which is perfect for your agent-controls-the-views demo. ([OpenAI Platform][1], [OpenAI][2])

If you instead mean the **new ChatGPT “Codex” coding agent** you might’ve seen in the news: that lives *inside ChatGPT* and isn’t an API you can program against. For a buildable demo, we’ll implement with the **OpenAI API’s function calling** (or your preferred provider) + CrewAI. ([OpenAI Platform][3])

Below is a minimal, working blueprint you can drop into a repo.

---

# 1) Repo layout

```
agent-demo/
  backend/
    app.py                # FastAPI + deterministic JSON
    seed.py               # seed sqlite
    models.py             # pydantic models
    db.sqlite3
  agent/
    crew.py               # CrewAI setup
    tools.py              # tool functions (HTTP clients + view intents)
    openai_client.py      # function-calling helper
    evals/triage_and_note.yaml
  frontend/
    src/
      main.tsx
      agentSocket.ts      # ws client
      registry.ts         # component + view registry
      views/TriageBoard.tsx
      views/EntityDetail.tsx
      panels/NotesPanel.tsx
    vite.config.ts
```

---

# 2) Backend — FastAPI (deterministic, agent-friendly)

`backend/app.py`

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
import sqlite3, os

app = FastAPI(title="MiniCRM", version="1.0.0")

DB_PATH = os.getenv("DB_PATH", "db.sqlite3")

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- Models (make contracts explicit) ---
class Customer(BaseModel):
    id: str
    name: str
    email: Optional[str] = None

class Ticket(BaseModel):
    id: str
    customer_id: str
    title: str
    status: str = Field(pattern="^(open|closed)$")
    created_at: str

class NoteIn(BaseModel):
    ticket_id: str
    body: str

class Note(BaseModel):
    id: str
    ticket_id: str
    body: str
    created_at: str

class EmailIn(BaseModel):
    to: str
    subject: str
    body: str

def rows(conn, q, args=()):
    cur = conn.execute(q, args)
    return [dict(r) for r in cur.fetchall()]

# --- Endpoints ---
@app.get("/customers", response_model=List[Customer])
def list_customers(name: Optional[str] = None):
    conn = db()
    if name:
        return rows(conn, "SELECT * FROM customers WHERE name LIKE ? ORDER BY name", (f"%{name}%",))
    return rows(conn, "SELECT * FROM customers ORDER BY name")

@app.get("/tickets", response_model=List[Ticket])
def list_tickets(customer_id: str, status: Optional[str] = None):
    conn = db()
    if status:
        return rows(conn, "SELECT * FROM tickets WHERE customer_id=? AND status=? ORDER BY created_at", (customer_id, status))
    return rows(conn, "SELECT * FROM tickets WHERE customer_id=? ORDER BY created_at", (customer_id,))

@app.post("/notes", response_model=Note)
def create_note(note: NoteIn):
    if not note.ticket_id:
        raise HTTPException(status_code=400, detail={"error_code":"MISSING_FIELD","message":"ticket_id required"})
    conn = db()
    cur = conn.execute("INSERT INTO notes(ticket_id, body, created_at) VALUES(?,?,strftime('%Y-%m-%dT%H:%M:%SZ','now'))",
                       (note.ticket_id, note.body))
    conn.commit()
    nid = cur.lastrowid
    (row,) = rows(conn, "SELECT id,ticket_id,body,created_at FROM notes WHERE id=?", (nid,))
    return row

@app.post("/emails")
def send_email(payload: EmailIn):
    # mock send
    return {"status":"sent","to":payload.to,"subject":payload.subject}

@app.get("/healthz")
def healthz():
    return {"ok": True}
```

Why this works for agents: **simple, stable schemas and structured errors** → easier tool calling and self-correction. (Matches OpenAI’s function-calling/structured-outputs guidance.) ([OpenAI Platform][3])

---

# 3) “View intents” channel (agent controls the UI)

A tiny WebSocket server can live in your agent process (or backend). The agent emits messages like:

```json
{"type":"set_view","view_id":"triage"}
{"type":"add_panel","panel":"NotesPanel"}
{"type":"remove_panel","panel":"NotesPanel"}
```

In the frontend, subscribe and update a **view registry**.

`frontend/src/registry.ts`

```ts
export type ViewIntent =
  | { type: "set_view"; view_id: "customer-list"|"customer-detail"|"triage" }
  | { type: "add_panel"; panel: "NotesPanel" }
  | { type: "remove_panel"; panel: "NotesPanel" };

export const registry = {
  currentView: "customer-list" as "customer-list"|"customer-detail"|"triage",
  layout: {
    "customer-list": ["EntityList"],
    "customer-detail": ["EntityDetail", "NotesPanel"],
    "triage": ["TriageBoard", "NotesPanel"],
  },
  constraints: {
    NotesPanel: { mustMountWithin: ["EntityDetail","TriageBoard"] }
  }
};

export function applyIntent(intent: ViewIntent) {
  if (intent.type === "set_view") registry.currentView = intent.view_id;
  if (intent.type === "add_panel") {
    const v = registry.currentView;
    if (!registry.layout[v].includes(intent.panel)) registry.layout[v].push(intent.panel);
  }
  if (intent.type === "remove_panel") {
    const v = registry.currentView;
    registry.layout[v] = registry.layout[v].filter(p => p !== intent.panel);
  }
}
```

`frontend/src/agentSocket.ts`

```ts
import { applyIntent, ViewIntent } from "./registry";
const ws = new WebSocket(import.meta.env.VITE_AGENT_WS);
ws.onmessage = (e) => {
  const intent = JSON.parse(e.data) as ViewIntent;
  applyIntent(intent);
  // trigger state update (use a store like Zustand or simple event emitter)
};
```

---

# 4) Agent — CrewAI + OpenAI function calling

We keep the “planner” small and define **strongly typed tools**. (Same developer model OpenAI recommends for tool use.) ([OpenAI Platform][3])

`agent/tools.py`

```python
import requests, os, json, websockets, asyncio

API_BASE = os.getenv("API_BASE", "http://localhost:8000")
AGENT_WS = os.getenv("AGENT_WS", "ws://localhost:8765")

def search_customers(name: str):
    r = requests.get(f"{API_BASE}/customers", params={"name": name}, timeout=10)
    r.raise_for_status()
    return r.json()

def list_tickets(customer_id: str, status: str = "open"):
    r = requests.get(f"{API_BASE}/tickets", params={"customer_id": customer_id, "status": status}, timeout=10)
    r.raise_for_status()
    return r.json()

def create_note(ticket_id: str, body: str):
    r = requests.post(f"{API_BASE}/notes", json={"ticket_id": ticket_id, "body": body}, timeout=10)
    if r.status_code >= 400:
        raise RuntimeError(r.json())
    return r.json()

def send_email(to: str, subject: str, body: str):
    r = requests.post(f"{API_BASE}/emails", json={"to": to, "subject": subject, "body": body}, timeout=10)
    r.raise_for_status()
    return r.json()

async def emit_intent(intent: dict):
    async with websockets.connect(AGENT_WS) as ws:
        await ws.send(json.dumps(intent))
```

`agent/openai_client.py` (tool schemas for function calling)

```python
from openai import OpenAI
client = OpenAI()  # expects OPENAI_API_KEY

tools = [
  {
    "type":"function",
    "function":{
      "name":"tool_search_customers",
      "description":"Search customers by (partial) name.",
      "parameters":{"type":"object","properties":{"name":{"type":"string"}},"required":["name"]}
    }
  },
  {
    "type":"function",
    "function":{
      "name":"tool_list_tickets",
      "description":"List tickets for a given customer id and status.",
      "parameters":{"type":"object","properties":{"customer_id":{"type":"string"},"status":{"type":"string","enum":["open","closed"]}},
                    "required":["customer_id"]}
    }
  },
  {
    "type":"function",
    "function":{
      "name":"tool_create_note",
      "description":"Create a note on a ticket.",
      "parameters":{"type":"object","properties":{"ticket_id":{"type":"string"},"body":{"type":"string"}},
                    "required":["ticket_id","body"]}
    }
  },
  {
    "type":"function",
    "function":{
      "name":"tool_emit_view_intent",
      "description":"Control the UI by setting a view or adding/removing panels.",
      "parameters":{"type":"object",
        "oneOf":[
          {"properties":{"type":{"const":"set_view"},"view_id":{"type":"string","enum":["customer-list","customer-detail","triage"]}},
           "required":["type","view_id"]},
          {"properties":{"type":{"const":"add_panel"},"panel":{"type":"string","enum":["NotesPanel"]}},
           "required":["type","panel"]},
          {"properties":{"type":{"const":"remove_panel"},"panel":{"type":"string","enum":["NotesPanel"]}},
           "required":["type","panel"]}
        ]
      }
    }
  }
]
```

`agent/crew.py` (minimal loop; CrewAI or a plain loop both work)

```python
import json, asyncio
from agent.openai_client import client, tools
from agent.tools import search_customers, list_tickets, create_note, send_email, emit_intent

def call_tool(name, args):
    if name == "tool_search_customers": return search_customers(**args)
    if name == "tool_list_tickets":     return list_tickets(**args)
    if name == "tool_create_note":      return create_note(**args)
    if name == "tool_emit_view_intent": return asyncio.run(emit_intent(args))
    raise ValueError(f"Unknown tool {name}")

def run_task(user_goal: str):
    messages=[{"role":"system","content":"You are an operations agent that completes tasks using tools and controls the app's views via view-intents."},
              {"role":"user","content":user_goal}]
    while True:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",  # or your preferred function-calling model
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0
        )
        choice = resp.choices[0]
        messages.append(choice.message)
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                tool_name = tc.function.name
                args = json.loads(tc.function.arguments or "{}")
                tool_result = call_tool(tool_name, args)
                messages.append({"role":"tool","tool_call_id": tc.id, "content": json.dumps(tool_result)})
            continue
        # no more tool calls → we are done
        return choice.message.content

if __name__ == "__main__":
    print(run_task("Show Acme’s open tickets in a triage view; for the oldest one, add a follow-up note and email me a short summary."))
```

This uses **function calling / structured outputs**, the recommended method for tool-using agents in the OpenAI API. ([OpenAI Platform][3])

---

# 5) Frontend (React/Vite) — tiny proof UI

`frontend/src/main.tsx`

```tsx
import React from "react";
import ReactDOM from "react-dom/client";
import { registry } from "./registry";
import TriageBoard from "./views/TriageBoard";
import EntityDetail from "./views/EntityDetail";
import "./agentSocket"; // subscribes to WS + updates registry

function App() {
  const [tick, setTick] = React.useState(0);
  // naive event to re-render on registry changes (swap in a proper store later)
  (window as any).forceRender = () => setTick(x => x+1);

  const view = registry.currentView;
  const layout = registry.layout[view];

  return (
    <div className="p-4 space-y-4">
      <h1 className="text-xl font-bold">Agent-Controlled Demo</h1>
      <div className="text-sm opacity-70">Current view: {view}</div>
      <div className="grid grid-cols-2 gap-4">
        {layout.includes("TriageBoard") && <TriageBoard />}
        {layout.includes("EntityDetail") && <EntityDetail />}
        {layout.includes("EntityList") && <div>/* TODO customer list */</div>}
        {layout.includes("NotesPanel") && <div className="col-span-2 border p-3 rounded">NotesPanel</div>}
      </div>
    </div>
  );
}
ReactDOM.createRoot(document.getElementById("root")!).render(<App />);
```

---

# 6) A 90-second scripted demo (works with the code above)

1. You run:

```bash
# terminal 1
uvicorn backend.app:app --reload
# terminal 2
python agent/crew.py
# terminal 3 (frontend)
pnpm dev
```

2. Say in the agent input (or `run_task()`):
   “**Open Acme triage, add a follow-up note on the oldest open ticket, and email me a summary. Then switch to customer detail and hide notes.**”

3. Watch: the agent calls `/customers` → sets **triage** view via WS → fetches tickets → adds a note → calls `/emails` → sets **customer-detail** → removes **NotesPanel**.

---

# 7) Evals (optional but quick win)

`agent/evals/triage_and_note.yaml`

```yaml
name: triage_and_note
user: "Show Acme’s open tickets; add a follow-up note on the oldest one; email me a summary."
asserts:
  - tool_called: tool_search_customers
  - tool_called: tool_emit_view_intent
  - tool_called: tool_list_tickets
  - tool_called: tool_create_note
  - tool_called: tool_emit_view_intent
```

