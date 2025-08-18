export type ViewIntent =
  | { type: "set_view"; view_id: "customer-list" | "customer-detail" | "triage" }
  | { type: "add_panel"; panel: "NotesPanel" }
  | { type: "remove_panel"; panel: "NotesPanel" };

export const registry = {
  currentView: "customer-list" as "customer-list" | "customer-detail" | "triage",
  layout: {
    "customer-list": ["EntityList"],
    "customer-detail": ["EntityDetail", "NotesPanel"],
    "triage": ["TriageBoard", "NotesPanel"],
  },
  constraints: {
    NotesPanel: { mustMountWithin: ["EntityDetail", "TriageBoard"] }
  }
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
}