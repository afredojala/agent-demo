import React from 'react';

interface Customer {
  id: string;
  name: string;
  email: string;
}

const EntityList: React.FC = () => {
  const [customers, setCustomers] = React.useState<Customer[]>([]);

  React.useEffect(() => {
    setCustomers([
      { id: 'cust_1', name: 'Acme Corp', email: 'contact@acme.com' },
      { id: 'cust_2', name: 'TechCorp Inc', email: 'support@techcorp.com' },
      { id: 'cust_3', name: 'Global Solutions', email: 'help@globalsolutions.com' },
    ]);
  }, []);

  return (
    <div className="border rounded-lg p-4 bg-white shadow">
      <h2 className="text-lg font-semibold mb-4">Customer List</h2>
      <div className="space-y-2">
        {customers.map(customer => (
          <div key={customer.id} className="p-3 border rounded hover:bg-gray-50 cursor-pointer">
            <div className="font-medium">{customer.name}</div>
            <div className="text-sm text-gray-600">{customer.email}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default EntityList;