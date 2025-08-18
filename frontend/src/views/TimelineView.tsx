import React, { useState, useEffect } from 'react';

interface TimelineEvent {
  id: string;
  type: 'ticket' | 'note' | 'customer';
  title: string;
  description: string;
  timestamp: string;
  customer?: string;
  status?: string;
}

const TimelineView: React.FC = () => {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTimelineData = async () => {
      try {
        const events: TimelineEvent[] = [];
        
        // Fetch customers and their tickets to build timeline
        const customersResponse = await fetch('http://localhost:8000/customers');
        const customers = await customersResponse.json();
        
        for (const customer of customers) {
          // Add customer creation event (mock)
          events.push({
            id: `customer-${customer.id}`,
            type: 'customer',
            title: 'New Customer Added',
            description: `${customer.name} joined the system`,
            timestamp: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(), // Random date in last 30 days
            customer: customer.name
          });

          try {
            // Fetch tickets for timeline
            const ticketsResponse = await fetch(
              `http://localhost:8000/tickets?customer_id=${customer.id}`
            );
            const tickets = await ticketsResponse.json();

            tickets.forEach((ticket: any) => {
              events.push({
                id: `ticket-${ticket.id}`,
                type: 'ticket',
                title: `Ticket Created: ${ticket.title}`,
                description: `Support ticket opened for ${customer.name}`,
                timestamp: ticket.created_at,
                customer: customer.name,
                status: ticket.status
              });

              // Mock: Add some note events
              if (Math.random() > 0.7) {
                events.push({
                  id: `note-${ticket.id}-${Math.random()}`,
                  type: 'note',
                  title: 'Note Added',
                  description: `Follow-up note added to ticket "${ticket.title}"`,
                  timestamp: new Date(new Date(ticket.created_at).getTime() + Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
                  customer: customer.name
                });
              }
            });
          } catch (error) {
            console.error(`Error fetching tickets for ${customer.name}:`, error);
          }
        }

        // Sort events by timestamp (newest first)
        events.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
        
        setEvents(events.slice(0, 50)); // Limit to 50 most recent events
      } catch (error) {
        console.error('Error fetching timeline data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTimelineData();
  }, []);

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffHours < 1) return 'Less than an hour ago';
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    
    return date.toLocaleDateString();
  };

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'customer':
        return (
          <div className="w-3 h-3 bg-blue-500 rounded-full ring-4 ring-white"></div>
        );
      case 'ticket':
        return (
          <div className="w-3 h-3 bg-orange-500 rounded-full ring-4 ring-white"></div>
        );
      case 'note':
        return (
          <div className="w-3 h-3 bg-green-500 rounded-full ring-4 ring-white"></div>
        );
      default:
        return (
          <div className="w-3 h-3 bg-gray-500 rounded-full ring-4 ring-white"></div>
        );
    }
  };

  const getEventColor = (type: string) => {
    switch (type) {
      case 'customer':
        return 'border-l-blue-500 bg-blue-50';
      case 'ticket':
        return 'border-l-orange-500 bg-orange-50';
      case 'note':
        return 'border-l-green-500 bg-green-50';
      default:
        return 'border-l-gray-500 bg-gray-50';
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded mb-4"></div>
          <div className="space-y-4">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="flex space-x-4">
                <div className="w-3 h-3 bg-gray-300 rounded-full mt-6"></div>
                <div className="flex-1 h-20 bg-gray-200 rounded"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Activity Timeline</h2>
      
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200"></div>
          
          <div className="space-y-6">
            {events.map((event, index) => (
              <div key={event.id} className="relative flex items-start space-x-6">
                {/* Timeline dot */}
                <div className="relative z-10 flex items-center justify-center">
                  {getEventIcon(event.type)}
                </div>
                
                {/* Event content */}
                <div className={`flex-1 min-w-0 p-4 rounded-lg border-l-4 ${getEventColor(event.type)}`}>
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-semibold text-gray-800 truncate">
                        {event.title}
                      </h4>
                      <p className="text-sm text-gray-600 mt-1">
                        {event.description}
                      </p>
                      {event.customer && (
                        <div className="flex items-center mt-2 space-x-2">
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                            {event.customer}
                          </span>
                          {event.status && (
                            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                              event.status === 'open' 
                                ? 'bg-orange-100 text-orange-800' 
                                : 'bg-green-100 text-green-800'
                            }`}>
                              {event.status}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                    
                    <div className="flex flex-col items-end text-xs text-gray-500">
                      <span>{formatTime(event.timestamp)}</span>
                      <span className="capitalize text-gray-400">
                        {event.type}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {events.length === 0 && (
              <div className="text-center py-12">
                <div className="text-gray-400 text-lg mb-2">📅</div>
                <h3 className="text-sm font-medium text-gray-900">No timeline events</h3>
                <p className="text-sm text-gray-500">Timeline events will appear here as they occur.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TimelineView;