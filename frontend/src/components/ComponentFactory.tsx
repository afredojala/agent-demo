import React from "react";
import ChartRenderer from "./ChartRenderer";
import ChatInterface from "./ChatInterface";
import WorkflowProgress from "./WorkflowProgress";

const componentRegistry: Record<string, React.ComponentType<any>> = {
  ChartRenderer,
  ChatInterface,
  WorkflowProgress,
};

export const ComponentFactory: React.FC<{ component: string; props?: any }> = ({ component, props }) => {
  const Comp = componentRegistry[component];
  if (!Comp) return null;
  return <Comp {...props} />;
};

export default componentRegistry;
