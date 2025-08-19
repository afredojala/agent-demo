export type ViewIntent =
  | { type: "set_view"; view_id: "customer-list" | "customer-detail" | "triage" | "dashboard" | "analytics" | "timeline" | "calendar" | "workflow" }
  | { type: "add_panel"; panel: "NotesPanel" }
  | { type: "remove_panel"; panel: "NotesPanel" }
  | { type: "render_chart"; chartConfig: any; containerId: string; title?: string; description?: string }
  | { type: "add_component"; id: string; component: string; props?: any }
  | { type: "update_component_props"; id: string; props: any }
  | { type: "remove_component"; id: string };

export const registry = {
  currentView: "customer-list" as "customer-list" | "customer-detail" | "triage" | "dashboard" | "analytics" | "timeline" | "calendar" | "workflow",
  layout: {
    "customer-list": ["EntityList"],
    "customer-detail": ["EntityDetail", "NotesPanel"],
    "triage": ["TriageBoard", "NotesPanel"],
    "dashboard": ["CustomerDashboard"],
    "analytics": ["AnalyticsView"],
    "timeline": ["TimelineView"],
    "calendar": ["CalendarView"],
    "workflow": ["WorkflowView"],
  },
  constraints: {
    NotesPanel: { mustMountWithin: ["EntityDetail", "TriageBoard"] }
  },
  charts: {} as Record<string, { chartConfig: any; title?: string; description?: string }>,
  components: {} as Record<string, { component: string; props: any }>
};

export function applyIntent(intent: ViewIntent) {
  if (intent.type === "set_view") {
    registry.currentView = intent.view_id;
  }
  if (intent.type === "add_panel") {
    const v = registry.currentView;
    if (!registry.layout[v].includes(intent.panel)) {
      registry.layout[v].push(intent.panel);
    }
  }
  if (intent.type === "remove_panel") {
    const v = registry.currentView;
    registry.layout[v] = registry.layout[v].filter(p => p !== intent.panel);
  }
  if (intent.type === "render_chart") {
    registry.charts[intent.containerId] = {
      chartConfig: intent.chartConfig,
      title: intent.title,
      description: intent.description
    };
    // Auto-switch to analytics view if chart is rendered
    registry.currentView = "analytics";
  }
  if (intent.type === "add_component") {
    registry.components[intent.id] = {
      component: intent.component,
      props: intent.props || {}
    };
  }
  if (intent.type === "update_component_props") {
    if (registry.components[intent.id]) {
      registry.components[intent.id].props = {
        ...registry.components[intent.id].props,
        ...intent.props
      };
    }
  }
  if (intent.type === "remove_component") {
    if (registry.components[intent.id]) {
      delete registry.components[intent.id];
    }
  }
}