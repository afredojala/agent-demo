import React, { useState, useEffect } from 'react';
import WorkflowProgress from '../components/WorkflowProgress';

interface WorkflowExecution {
  id: string;
  name: string;
  status: 'running' | 'completed' | 'error' | 'idle';
  steps: Array<{
    step: string;
    status: 'completed' | 'in_progress' | 'pending' | 'error';
    description?: string;
    timestamp?: string;
  }>;
  currentStep: number;
  startTime: string;
  result?: any;
}

const WorkflowView: React.FC = () => {
  const [workflows, setWorkflows] = useState<WorkflowExecution[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null);

  useEffect(() => {
    // Mock workflow data - in real app this would come from WebSocket or API
    const mockWorkflows: WorkflowExecution[] = [
      {
        id: 'wf_1',
        name: 'customer_onboarding',
        status: 'completed',
        currentStep: 4,
        startTime: new Date(Date.now() - 300000).toISOString(), // 5 minutes ago
        steps: [
          { step: '✓ Created customer record for TechCorp Inc', status: 'completed', timestamp: '5 min ago' },
          { step: '✓ Identified as premium customer: Enterprise email domain', status: 'completed', timestamp: '5 min ago' },
          { step: '✓ Scheduled premium welcome call within 24 hours', status: 'completed', timestamp: '4 min ago' },
          { step: '✓ Created premium onboarding ticket', status: 'completed', timestamp: '4 min ago' },
          { step: '✓ Scheduled 7-day health check', status: 'completed', timestamp: '4 min ago' }
        ],
        result: {
          workflow: 'customer_onboarding',
          status: 'completed',
          path: 'premium'
        }
      },
      {
        id: 'wf_2', 
        name: 'ticket_escalation',
        status: 'completed',
        currentStep: 3,
        startTime: new Date(Date.now() - 120000).toISOString(), // 2 minutes ago
        steps: [
          { step: '✓ Retrieved customer ticket data', status: 'completed', timestamp: '2 min ago' },
          { step: '🚨 Escalated ticket for Acme Corp: SLA breach risk detected', status: 'completed', timestamp: '2 min ago' },
          { step: '⚠️ Monitoring ticket for Global Solutions: Approaching SLA limit', status: 'completed', timestamp: '2 min ago' },
          { step: '✓ Sent escalation summary to management', status: 'completed', timestamp: '1 min ago' }
        ],
        result: {
          workflow: 'ticket_escalation',
          escalated_count: 1,
          monitored_count: 1
        }
      }
    ];

    setWorkflows(mockWorkflows);
  }, []);

  const getWorkflowSummary = (workflow: WorkflowExecution) => {
    const completedSteps = workflow.steps.filter(s => s.status === 'completed').length;
    const totalSteps = workflow.steps.length;
    
    return `${completedSteps}/${totalSteps} steps completed`;
  };

  const getWorkflowDescription = (workflowName: string) => {
    switch (workflowName) {
      case 'customer_onboarding':
        return 'Automated customer setup with premium/standard routing';
      case 'ticket_escalation':
        return 'SLA monitoring and automated escalation workflow';
      case 'weekly_report':
        return 'Comprehensive business reporting with trend analysis';
      case 'customer_health_check':
        return 'Proactive customer health monitoring and actions';
      default:
        return 'Multi-step business workflow with decision points';
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Workflow Management</h2>
      
      {workflows.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 text-4xl mb-4">⚙️</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Active Workflows</h3>
          <p className="text-sm text-gray-500">
            Workflows will appear here when triggered by agent commands like "onboard a customer" or "run escalation workflow"
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Workflow List */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Workflows</h3>
            
            <div className="space-y-4">
              {workflows.map((workflow) => (
                <div
                  key={workflow.id}
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-colors ${
                    selectedWorkflow === workflow.id 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setSelectedWorkflow(workflow.id)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-800">
                      {workflow.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </h4>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      workflow.status === 'completed' ? 'bg-green-100 text-green-800' :
                      workflow.status === 'running' ? 'bg-blue-100 text-blue-800' :
                      workflow.status === 'error' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {workflow.status}
                    </span>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-2">
                    {getWorkflowDescription(workflow.name)}
                  </p>
                  
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>{getWorkflowSummary(workflow)}</span>
                    <span>{new Date(workflow.startTime).toLocaleTimeString()}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Workflow Details */}
          <div className="bg-white rounded-lg shadow-md p-6">
            {selectedWorkflow ? (
              (() => {
                const workflow = workflows.find(w => w.id === selectedWorkflow);
                return workflow ? (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Workflow Details</h3>
                    
                    <WorkflowProgress
                      workflowName={workflow.name}
                      steps={workflow.steps}
                      currentStep={workflow.currentStep}
                      status={workflow.status}
                    />

                    {workflow.result && (
                      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                        <h4 className="font-medium text-gray-800 mb-2">Result Summary</h4>
                        <pre className="text-sm text-gray-600 overflow-x-auto">
                          {JSON.stringify(workflow.result, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                ) : null;
              })()
            ) : (
              <div className="text-center py-12">
                <div className="text-gray-400 text-3xl mb-2">📋</div>
                <p className="text-gray-500">Select a workflow to view details</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Workflow Templates */}
      <div className="mt-8 bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Available Workflows</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { name: 'customer_onboarding', icon: '👤', description: 'New customer setup' },
            { name: 'ticket_escalation', icon: '🚨', description: 'SLA monitoring' },
            { name: 'weekly_report', icon: '📊', description: 'Business reporting' },
            { name: 'customer_health_check', icon: '💚', description: 'Health monitoring' }
          ].map((template) => (
            <div key={template.name} className="p-4 border rounded-lg hover:border-blue-300 transition-colors">
              <div className="text-2xl mb-2">{template.icon}</div>
              <h4 className="font-medium text-gray-800 mb-1">
                {template.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </h4>
              <p className="text-sm text-gray-600">{template.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WorkflowView;