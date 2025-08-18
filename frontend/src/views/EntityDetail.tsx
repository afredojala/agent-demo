import React from 'react';

const EntityDetail: React.FC = () => {
  return (
    <div className="border rounded-lg p-4 bg-white shadow">
      <h2 className="text-lg font-semibold mb-4">Entity Detail</h2>
      <div className="space-y-3">
        <div>
          <h3 className="font-medium">Acme Corp</h3>
          <p className="text-sm text-gray-600">contact@acme.com</p>
        </div>
        <div className="border-t pt-3">
          <h4 className="font-medium text-sm mb-2">Recent Activity</h4>
          <div className="text-sm text-gray-600 space-y-1">
            <div>• Login issues reported</div>
            <div>• Feature request submitted</div>
            <div>• Payment bug resolved</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EntityDetail;