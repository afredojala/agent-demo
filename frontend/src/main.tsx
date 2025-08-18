import React from "react";
import ReactDOM from "react-dom/client";
import { registry, applyIntent } from "./registry";
import { setForceRender } from "./agentSocket";
import TriageBoard from "./views/TriageBoard";
import EntityDetail from "./views/EntityDetail";
import EntityList from "./views/EntityList";
import CustomerDashboard from "./views/CustomerDashboard";
import AnalyticsView from "./views/AnalyticsView";
import TimelineView from "./views/TimelineView";
import CalendarView from "./views/CalendarView";
import WorkflowView from "./views/WorkflowView";
import NotesPanel from "./panels/NotesPanel";
import ChatInterface from "./components/ChatInterface";
import "./index.css";

function App() {
  const [tick, setTick] = React.useState(0);

  React.useEffect(() => {
    setForceRender(() => setTick(x => x + 1));
  }, []);

  const handleViewChange = (viewId: string) => {
    applyIntent({ type: "set_view", view_id: viewId as any });
    setTick(x => x + 1);
  };

  const view = registry.currentView;
  const layout = registry.layout[view];

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-6xl mx-auto space-y-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <h1 className="text-2xl font-bold">Agent-Controlled Demo</h1>
          <div className="text-sm text-gray-600 mt-1">Current view: {view}</div>
          <div className="text-xs text-gray-500 mt-1">
            Active components: {layout.join(", ")}
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 space-y-4">
            {/* Full-width views */}
            {layout.includes("CustomerDashboard") && <CustomerDashboard />}
            {layout.includes("AnalyticsView") && <AnalyticsView />}
            {layout.includes("TimelineView") && <TimelineView />}
            {layout.includes("CalendarView") && <CalendarView />}
            {layout.includes("WorkflowView") && <WorkflowView />}
            
            {/* Grid-based views */}
            {!layout.some(l => ["CustomerDashboard", "AnalyticsView", "TimelineView", "CalendarView", "WorkflowView"].includes(l)) && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {layout.includes("TriageBoard") && <TriageBoard />}
                {layout.includes("EntityDetail") && <EntityDetail />}
                {layout.includes("EntityList") && <EntityList />}
              </div>
            )}
            
            {layout.includes("NotesPanel") && <NotesPanel />}
          </div>
          
          <div>
            <ChatInterface onViewChange={handleViewChange} />
          </div>
        </div>
      </div>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root")!);
root.render(<App />);