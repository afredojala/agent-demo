import React from "react";
import ReactDOM from "react-dom/client";
import { motion, AnimatePresence } from "framer-motion";
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
import { ComponentFactory } from "./components/ComponentFactory";
import "./index.css";

function App() {
  const [tick, setTick] = React.useState(0);
  const [isTransitioning, setIsTransitioning] = React.useState(false);

  React.useEffect(() => {
    setForceRender(() => setTick(x => x + 1));
  }, []);

  const handleViewChange = (viewId: string) => {
    setIsTransitioning(true);
    setTimeout(() => {
      applyIntent({ type: "set_view", view_id: viewId as any });
      setTick(x => x + 1);
      setIsTransitioning(false);
    }, 200);
  };

  const view = registry.currentView;
  const layout = registry.layout[view];

  return (
    <>
      {/* Animated background */}
      <div className="animated-bg"></div>
      <div className="mesh-overlay"></div>
      
      <div className="min-h-screen p-4 relative">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Header */}
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass p-6 animate-float"
          >
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold gradient-text">Agentic Demo</h1>
                <div className="text-sm text-gray-300 mt-1 flex items-center space-x-4">
                  <span>Current view: <span className="text-indigo-400 font-medium">{view}</span></span>
                  <span className="text-gray-500">•</span>
                  <span>Components: <span className="text-purple-400">{layout.length}</span></span>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-xs text-green-400">Agent Active</span>
              </div>
            </div>
          </motion.div>
          
          <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
            {/* Main content area */}
            <div className="xl:col-span-3 space-y-6">
              <AnimatePresence mode="wait">
                <motion.div
                  key={view}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                  className={isTransitioning ? "pointer-events-none opacity-50" : ""}
                >
                  {/* Full-width views */}
                  {layout.includes("CustomerDashboard") && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.1 }}
                    >
                      <CustomerDashboard />
                    </motion.div>
                  )}
                  {layout.includes("AnalyticsView") && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.1 }}
                    >
                      <AnalyticsView />
                    </motion.div>
                  )}
                  {layout.includes("TimelineView") && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.1 }}
                    >
                      <TimelineView />
                    </motion.div>
                  )}
                  {layout.includes("CalendarView") && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.1 }}
                    >
                      <CalendarView />
                    </motion.div>
                  )}
                  {layout.includes("WorkflowView") && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.1 }}
                    >
                      <WorkflowView />
                    </motion.div>
                  )}
                  
                  {/* Grid-based views */}
                  {!layout.some(l => ["CustomerDashboard", "AnalyticsView", "TimelineView", "CalendarView", "WorkflowView"].includes(l)) && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      {layout.includes("TriageBoard") && (
                        <motion.div
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.1 }}
                        >
                          <TriageBoard />
                        </motion.div>
                      )}
                      {layout.includes("EntityDetail") && (
                        <motion.div
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.2 }}
                        >
                          <EntityDetail />
                        </motion.div>
                      )}
                      {layout.includes("EntityList") && (
                        <motion.div
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.15 }}
                        >
                          <EntityList />
                        </motion.div>
                      )}
                    </div>
                  )}
                  
                  {layout.includes("NotesPanel") && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 }}
                    >
                      <NotesPanel />
                    </motion.div>
                  )}
                  {Object.entries(registry.components).map(([id, cfg]) => (
                    <ComponentFactory key={id} component={cfg.component} props={cfg.props} />
                  ))}
                </motion.div>
              </AnimatePresence>
            </div>
            
            {/* Sidebar */}
            <div className="xl:col-span-1">
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
                className="sticky top-4"
              >
                <ChatInterface onViewChange={handleViewChange} />
              </motion.div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root")!);
root.render(<App />);