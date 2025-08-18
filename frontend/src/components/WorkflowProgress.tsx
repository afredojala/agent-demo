import React from 'react';

interface WorkflowStep {
  step: string;
  status: 'completed' | 'in_progress' | 'pending' | 'error';
  description?: string;
  timestamp?: string;
}

interface WorkflowProgressProps {
  workflowName: string;
  steps: WorkflowStep[];
  currentStep: number;
  status: 'running' | 'completed' | 'error' | 'idle';
  onClose?: () => void;
}

const WorkflowProgress: React.FC<WorkflowProgressProps> = ({
  workflowName,
  steps,
  currentStep,
  status,
  onClose
}) => {
  const getStepIcon = (stepStatus: string) => {
    switch (stepStatus) {
      case 'completed':
        return <div className="w-3 h-3 bg-green-500 rounded-full"></div>;
      case 'in_progress':
        return <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>;
      case 'error':
        return <div className="w-3 h-3 bg-red-500 rounded-full"></div>;
      default:
        return <div className="w-3 h-3 bg-gray-300 rounded-full"></div>;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'running':
        return 'border-blue-500 bg-blue-50';
      case 'completed':
        return 'border-green-500 bg-green-50';
      case 'error':
        return 'border-red-500 bg-red-50';
      default:
        return 'border-gray-300 bg-gray-50';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'running':
        return '⚙️';
      case 'completed':
        return '✅';
      case 'error':
        return '❌';
      default:
        return '📋';
    }
  };

  return (
    <div className={`border-l-4 p-4 rounded-r-lg ${getStatusColor()}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <span className="text-lg">{getStatusIcon()}</span>
          <h3 className="font-semibold text-gray-800">
            {workflowName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} Workflow
          </h3>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-sm"
          >
            ✕
          </button>
        )}
      </div>

      <div className="space-y-2">
        {steps.map((step, index) => (
          <div key={index} className="flex items-start space-x-3">
            <div className="flex-shrink-0 mt-1">
              {getStepIcon(step.status)}
            </div>
            <div className="flex-1 min-w-0">
              <p className={`text-sm ${
                step.status === 'completed' ? 'text-green-700' :
                step.status === 'in_progress' ? 'text-blue-700' :
                step.status === 'error' ? 'text-red-700' :
                'text-gray-600'
              }`}>
                {step.step}
              </p>
              {step.description && (
                <p className="text-xs text-gray-500 mt-1">{step.description}</p>
              )}
            </div>
            {step.timestamp && (
              <div className="text-xs text-gray-400 flex-shrink-0">
                {step.timestamp}
              </div>
            )}
          </div>
        ))}
      </div>

      {status === 'running' && (
        <div className="mt-4 flex items-center space-x-2 text-sm text-blue-600">
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
          <span>Workflow in progress... Step {currentStep + 1} of {steps.length}</span>
        </div>
      )}

      {status === 'completed' && (
        <div className="mt-4 text-sm text-green-600">
          ✓ Workflow completed successfully
        </div>
      )}

      {status === 'error' && (
        <div className="mt-4 text-sm text-red-600">
          ✗ Workflow encountered an error
        </div>
      )}
    </div>
  );
};

export default WorkflowProgress;