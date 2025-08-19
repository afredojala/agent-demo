import { applyIntent, ViewIntent, registry } from "./registry";

const WS_URL = import.meta.env.VITE_AGENT_WS || "ws://localhost:8765";

let ws: WebSocket | null = null;
let forceRender: (() => void) | null = null;

export function setForceRender(fn: () => void) {
  forceRender = fn;
}

export function sendEvent(payload: Record<string, unknown>) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: "event", payload }));
  } else {
    console.warn("Agent WebSocket not connected");
  }
}

function connectWebSocket() {
  try {
    ws = new WebSocket(WS_URL);
    
    ws.onopen = () => {
      console.log("Agent WebSocket connected");
    };
    
    ws.onmessage = (event) => {
      try {
        const intent = JSON.parse(event.data) as ViewIntent;
        console.log("Received intent:", intent);
        console.log("Registry before:", JSON.stringify({currentView: registry.currentView, layout: registry.layout}));
        applyIntent(intent);
        console.log("Registry after:", JSON.stringify({currentView: registry.currentView, layout: registry.layout}));
        if (forceRender) {
          console.log("Calling forceRender...");
          forceRender();
        } else {
          console.log("forceRender not available!");
        }
      } catch (error) {
        console.error("Failed to parse intent:", error);
      }
    };
    
    ws.onclose = () => {
      console.log("Agent WebSocket disconnected, reconnecting in 5s...");
      setTimeout(connectWebSocket, 5000);
    };
    
    ws.onerror = (error) => {
      console.error("Agent WebSocket error:", error);
    };
  } catch (error) {
    console.error("Failed to connect to agent WebSocket:", error);
    setTimeout(connectWebSocket, 5000);
  }
}

connectWebSocket();