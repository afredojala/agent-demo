import React, { useState, useEffect } from 'react';

interface AnalyticsData {
  customerStats: Array<{
    customer: string;
    ticket_count: number;
  }>;
  statusSummary: {
    total_customers: number;
    total_open_tickets: number;
    total_closed_tickets: number;
  };
}

const AnalyticsView: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        // Fetch customers and calculate analytics
        const response = await fetch('http://localhost:8000/customers');
        const customers = await response.json();
        
        const customerStats = await Promise.all(
          customers.map(async (customer: any) => {
            try {
              const ticketsResponse = await fetch(
                `http://localhost:8000/tickets?customer_id=${customer.id}`
              );
              const tickets = await ticketsResponse.json();
              return {
                customer: customer.name,
                ticket_count: tickets.length
              };
            } catch {
              return {
                customer: customer.name,
                ticket_count: 0
              };
            }
          })
        );

        // Calculate status summary
        let totalOpenTickets = 0;
        let totalClosedTickets = 0;
        
        for (const customer of customers) {
          try {
            const openResponse = await fetch(
              `http://localhost:8000/tickets?customer_id=${customer.id}&status=open`
            );
            const closedResponse = await fetch(
              `http://localhost:8000/tickets?customer_id=${customer.id}&status=closed`
            );
            
            const openTickets = await openResponse.json();
            const closedTickets = await closedResponse.json();
            
            totalOpenTickets += openTickets.length;
            totalClosedTickets += closedTickets.length;
          } catch {
            // Continue if there's an error with individual customer
          }
        }

        setAnalytics({
          customerStats: customerStats.sort((a, b) => b.ticket_count - a.ticket_count),
          statusSummary: {
            total_customers: customers.length,
            total_open_tickets: totalOpenTickets,
            total_closed_tickets: totalClosedTickets,
          }
        });
      } catch (error) {
        console.error('Error fetching analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded mb-4"></div>
          <div className="grid grid-cols-2 gap-6">
            <div className="h-80 bg-gray-200 rounded"></div>
            <div className="h-80 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  const totalTickets = analytics?.statusSummary.total_open_tickets + analytics?.statusSummary.total_closed_tickets;

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Analytics & Reports</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Ticket Status Chart */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Ticket Status Overview</h3>
          
          {analytics && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-600">Open Tickets</span>
                <span className="text-sm font-bold text-orange-600">
                  {analytics.statusSummary.total_open_tickets}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-orange-600 h-2 rounded-full"
                  style={{
                    width: `${totalTickets ? (analytics.statusSummary.total_open_tickets / totalTickets) * 100 : 0}%`
                  }}
                ></div>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-600">Closed Tickets</span>
                <span className="text-sm font-bold text-green-600">
                  {analytics.statusSummary.total_closed_tickets}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-600 h-2 rounded-full"
                  style={{
                    width: `${totalTickets ? (analytics.statusSummary.total_closed_tickets / totalTickets) * 100 : 0}%`
                  }}
                ></div>
              </div>
              
              <div className="mt-4 p-3 bg-gray-50 rounded">
                <div className="text-sm text-gray-600">
                  <strong>Total Tickets:</strong> {totalTickets}
                </div>
                <div className="text-sm text-gray-600">
                  <strong>Resolution Rate:</strong> {totalTickets ? Math.round((analytics.statusSummary.total_closed_tickets / totalTickets) * 100) : 0}%
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Customer Activity Chart */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Top Customers by Tickets</h3>
          
          {analytics && (
            <div className="space-y-3">
              {analytics.customerStats.slice(0, 8).map((customer, index) => (
                <div key={customer.customer} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white ${
                      index < 3 ? 'bg-blue-500' : 'bg-gray-400'
                    }`}>
                      {index + 1}
                    </div>
                    <span className="text-sm font-medium text-gray-700 truncate">
                      {customer.customer}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-20 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full"
                        style={{
                          width: `${analytics.customerStats[0]?.ticket_count ? (customer.ticket_count / analytics.customerStats[0].ticket_count) * 100 : 0}%`
                        }}
                      ></div>
                    </div>
                    <span className="text-sm font-bold text-gray-800 w-6 text-right">
                      {customer.ticket_count}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Summary Statistics */}
        <div className="bg-white p-6 rounded-lg shadow-md lg:col-span-2">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Summary Statistics</h3>
          
          {analytics && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {analytics.statusSummary.total_customers}
                </div>
                <div className="text-sm text-blue-800">Total Customers</div>
              </div>
              <div className="text-center p-4 bg-orange-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">
                  {analytics.statusSummary.total_open_tickets}
                </div>
                <div className="text-sm text-orange-800">Open Tickets</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {analytics.statusSummary.total_closed_tickets}
                </div>
                <div className="text-sm text-green-800">Closed Tickets</div>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-600">
                  {totalTickets ? (analytics.statusSummary.total_open_tickets / analytics.statusSummary.total_customers).toFixed(1) : '0.0'}
                </div>
                <div className="text-sm text-gray-800">Avg Open/Customer</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsView;