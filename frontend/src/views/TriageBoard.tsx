import React from 'react';

interface Ticket {
  id: string;
  title: string;
  status: string;
  created_at: string;
}

const TriageBoard: React.FC = () => {
  const [tickets, setTickets] = React.useState<Ticket[]>([]);

  React.useEffect(() => {
    // Mock data for now - in real app, this would fetch from API
    setTickets([
      { id: 'ticket_1', title: 'Login issues with new system', status: 'open', created_at: '2024-01-15T10:30:00Z' },
      { id: 'ticket_2', title: 'Feature request for dashboard', status: 'open', created_at: '2024-01-16T14:20:00Z' },
      { id: 'ticket_4', title: 'Performance issues on mobile', status: 'open', created_at: '2024-01-18T09:15:00Z' },
    ]);
  }, []);

  return (
    <div className="border rounded-lg p-4 bg-white shadow">
      <h2 className="text-lg font-semibold mb-4">Triage Board</h2>
      <div className="space-y-3">
        {tickets.map(ticket => (
          <div key={ticket.id} className="border-l-4 border-blue-500 pl-3 py-2 bg-gray-50">
            <div className="font-medium">{ticket.title}</div>
            <div className="text-sm text-gray-600">
              {ticket.id} • {new Date(ticket.created_at).toLocaleDateString()}
            </div>
            <div className="text-xs mt-1">
              <span className="px-2 py-1 bg-green-100 text-green-800 rounded">
                {ticket.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TriageBoard;