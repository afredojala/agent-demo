import React, { useState, useEffect } from 'react';

interface Customer {
  id: string;
  name: string;
  email?: string;
  ticket_count?: number;
}

interface DashboardStats {
  total_customers: number;
  total_tickets: number;
  open_tickets: number;
  closed_tickets: number;
}

const CustomerDashboard: React.FC = () => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch customers
        const customersResponse = await fetch('http://localhost:8000/customers');
        const customersData = await customersResponse.json();
        
        // Enrich with ticket counts
        const enrichedCustomers = await Promise.all(
          customersData.map(async (customer: Customer) => {
            try {
              const ticketsResponse = await fetch(
                `http://localhost:8000/tickets?customer_id=${customer.id}`
              );
              const tickets = await ticketsResponse.json();
              return { ...customer, ticket_count: tickets.length };
            } catch {
              return { ...customer, ticket_count: 0 };
            }
          })
        );

        setCustomers(enrichedCustomers);

        // Calculate stats
        const totalTickets = enrichedCustomers.reduce((sum, c) => sum + (c.ticket_count || 0), 0);
        const mockStats: DashboardStats = {
          total_customers: enrichedCustomers.length,
          total_tickets: totalTickets,
          open_tickets: Math.floor(totalTickets * 0.7), // Mock: 70% open
          closed_tickets: Math.floor(totalTickets * 0.3), // Mock: 30% closed
        };
        setStats(mockStats);
        
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded mb-4"></div>
          <div className="grid grid-cols-4 gap-4 mb-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Customer Dashboard</h2>
      
      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-2xl font-bold text-blue-600">{stats.total_customers}</div>
            <div className="text-gray-600">Total Customers</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-2xl font-bold text-green-600">{stats.total_tickets}</div>
            <div className="text-gray-600">Total Tickets</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-2xl font-bold text-orange-600">{stats.open_tickets}</div>
            <div className="text-gray-600">Open Tickets</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-2xl font-bold text-gray-600">{stats.closed_tickets}</div>
            <div className="text-gray-600">Closed Tickets</div>
          </div>
        </div>
      )}

      {/* Customer List with Ticket Counts */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="p-4 border-b">
          <h3 className="text-lg font-semibold text-gray-800">Customer Activity</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Customer
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tickets
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {customers.map((customer) => (
                <tr key={customer.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{customer.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">{customer.email || 'No email'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {customer.ticket_count || 0}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      (customer.ticket_count || 0) > 3 
                        ? 'bg-red-100 text-red-800' 
                        : (customer.ticket_count || 0) > 1 
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {(customer.ticket_count || 0) > 3 
                        ? 'High Activity' 
                        : (customer.ticket_count || 0) > 1 
                        ? 'Active'
                        : 'Low Activity'
                      }
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default CustomerDashboard;