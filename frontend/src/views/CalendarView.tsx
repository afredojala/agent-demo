import React, { useState, useEffect } from 'react';

interface CalendarEvent {
  id: string;
  title: string;
  type: 'follow-up' | 'deadline' | 'meeting' | 'reminder';
  date: string;
  customer?: string;
  status?: string;
}

const CalendarView: React.FC = () => {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentDate, setCurrentDate] = useState(new Date());

  useEffect(() => {
    const generateMockEvents = async () => {
      try {
        // Fetch customers to generate realistic events
        const customersResponse = await fetch('http://localhost:8000/customers');
        const customers = await customersResponse.json();
        
        const mockEvents: CalendarEvent[] = [];
        const today = new Date();
        
        customers.forEach((customer: any, index: number) => {
          // Generate some future events for each customer
          const followUpDate = new Date(today);
          followUpDate.setDate(today.getDate() + (index + 1) * 3); // Spread out follow-ups
          
          mockEvents.push({
            id: `follow-up-${customer.id}`,
            title: `Follow-up call with ${customer.name}`,
            type: 'follow-up',
            date: followUpDate.toISOString().split('T')[0],
            customer: customer.name,
            status: 'scheduled'
          });
          
          // Add some deadline events
          if (index % 2 === 0) {
            const deadlineDate = new Date(today);
            deadlineDate.setDate(today.getDate() + (index + 1) * 5);
            
            mockEvents.push({
              id: `deadline-${customer.id}`,
              title: `Response deadline for ${customer.name}`,
              type: 'deadline',
              date: deadlineDate.toISOString().split('T')[0],
              customer: customer.name,
              status: 'pending'
            });
          }
          
          // Add some meeting events
          if (index % 3 === 0) {
            const meetingDate = new Date(today);
            meetingDate.setDate(today.getDate() + (index + 1) * 7);
            
            mockEvents.push({
              id: `meeting-${customer.id}`,
              title: `Team meeting about ${customer.name}`,
              type: 'meeting',
              date: meetingDate.toISOString().split('T')[0],
              customer: customer.name,
              status: 'confirmed'
            });
          }
        });

        // Add some general reminders
        const reminderDate = new Date(today);
        reminderDate.setDate(today.getDate() + 1);
        mockEvents.push({
          id: 'reminder-weekly',
          title: 'Weekly team standup',
          type: 'reminder',
          date: reminderDate.toISOString().split('T')[0],
        });

        setEvents(mockEvents);
      } catch (error) {
        console.error('Error generating calendar events:', error);
      } finally {
        setLoading(false);
      }
    };

    generateMockEvents();
  }, []);

  const getCurrentMonthEvents = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    
    return events.filter(event => {
      const eventDate = new Date(event.date);
      return eventDate >= firstDay && eventDate <= lastDay;
    });
  };

  const getEventColor = (type: string) => {
    switch (type) {
      case 'follow-up':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'deadline':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'meeting':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'reminder':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    });
  };

  const getUpcomingEvents = () => {
    const today = new Date().toISOString().split('T')[0];
    return events
      .filter(event => event.date >= today)
      .sort((a, b) => a.date.localeCompare(b.date))
      .slice(0, 10);
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded mb-4"></div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 h-96 bg-gray-200 rounded"></div>
            <div className="h-96 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  const monthEvents = getCurrentMonthEvents();
  const upcomingEvents = getUpcomingEvents();

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Calendar & Schedule</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calendar Overview */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-800">
              {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
            </h3>
            <div className="flex space-x-2">
              <button
                onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1))}
                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded"
              >
                Previous
              </button>
              <button
                onClick={() => setCurrentDate(new Date())}
                className="px-3 py-1 text-sm bg-blue-500 hover:bg-blue-600 text-white rounded"
              >
                Today
              </button>
              <button
                onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1))}
                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded"
              >
                Next
              </button>
            </div>
          </div>

          {/* Events for current month */}
          <div className="space-y-4">
            {monthEvents.length > 0 ? (
              monthEvents
                .sort((a, b) => a.date.localeCompare(b.date))
                .map((event) => (
                  <div
                    key={event.id}
                    className={`p-4 rounded-lg border ${getEventColor(event.type)}`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium">{event.title}</h4>
                        {event.customer && (
                          <p className="text-sm opacity-75 mt-1">Customer: {event.customer}</p>
                        )}
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium">{formatDate(event.date)}</div>
                        <div className="text-xs capitalize">{event.type}</div>
                      </div>
                    </div>
                  </div>
                ))
            ) : (
              <div className="text-center py-12">
                <div className="text-gray-400 text-4xl mb-4">📅</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No events this month</h3>
                <p className="text-sm text-gray-500">Scheduled events will appear here.</p>
              </div>
            )}
          </div>
        </div>

        {/* Upcoming Events Sidebar */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Upcoming Events</h3>
          
          <div className="space-y-3">
            {upcomingEvents.length > 0 ? (
              upcomingEvents.map((event) => (
                <div
                  key={event.id}
                  className="p-3 rounded-lg bg-gray-50 border-l-4 border-blue-500"
                >
                  <div className="text-sm font-medium text-gray-800 truncate">
                    {event.title}
                  </div>
                  <div className="text-xs text-gray-600 mt-1">
                    {formatDate(event.date)}
                  </div>
                  {event.customer && (
                    <div className="text-xs text-gray-500 mt-1 truncate">
                      {event.customer}
                    </div>
                  )}
                  <div className={`inline-block text-xs px-2 py-0.5 rounded mt-2 ${getEventColor(event.type)}`}>
                    {event.type}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <div className="text-gray-400 text-2xl mb-2">⏰</div>
                <p className="text-sm text-gray-500">No upcoming events</p>
              </div>
            )}
          </div>

          {/* Legend */}
          <div className="mt-6 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">Event Types</h4>
            <div className="space-y-2 text-xs">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-blue-500 rounded"></div>
                <span>Follow-ups</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-red-500 rounded"></div>
                <span>Deadlines</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded"></div>
                <span>Meetings</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-yellow-500 rounded"></div>
                <span>Reminders</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CalendarView;