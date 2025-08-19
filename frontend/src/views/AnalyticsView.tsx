import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';
import ChartRenderer from '../components/ChartRenderer';
import { registry } from '../registry';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

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

const AnimatedCounter = ({ value, duration = 2000 }: { value: number; duration?: number }) => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let startTime: number;
    const animateCount = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      const currentCount = Math.floor(progress * value);
      setCount(currentCount);
      
      if (progress < 1) {
        requestAnimationFrame(animateCount);
      }
    };
    
    requestAnimationFrame(animateCount);
  }, [value, duration]);

  return <span>{count}</span>;
};

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
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-6"
        >
          <div className="glass p-6">
            <div className="animate-pulse space-y-4">
              <div className="h-8 bg-white/10 rounded mb-4"></div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="h-80 bg-white/5 rounded-xl"></div>
                <div className="h-80 bg-white/5 rounded-xl"></div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  const totalTickets = analytics?.statusSummary.total_open_tickets + analytics?.statusSummary.total_closed_tickets;

  // Chart data
  const doughnutData = {
    labels: ['Open Tickets', 'Closed Tickets'],
    datasets: [{
      data: [analytics?.statusSummary.total_open_tickets || 0, analytics?.statusSummary.total_closed_tickets || 0],
      backgroundColor: [
        'rgba(249, 115, 22, 0.8)',
        'rgba(34, 197, 94, 0.8)',
      ],
      borderColor: [
        'rgba(249, 115, 22, 1)',
        'rgba(34, 197, 94, 1)',
      ],
      borderWidth: 2,
    }]
  };

  const barData = {
    labels: analytics?.customerStats.slice(0, 6).map(c => c.customer.split(' ')[0]) || [],
    datasets: [{
      label: 'Tickets',
      data: analytics?.customerStats.slice(0, 6).map(c => c.ticket_count) || [],
      backgroundColor: 'rgba(79, 70, 229, 0.8)',
      borderColor: 'rgba(79, 70, 229, 1)',
      borderWidth: 2,
      borderRadius: 8,
    }]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#f1f5f9',
          font: {
            size: 12
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        titleColor: '#f1f5f9',
        bodyColor: '#cbd5e1',
        borderColor: 'rgba(79, 70, 229, 0.5)',
        borderWidth: 1,
      }
    },
    scales: {
      y: {
        ticks: {
          color: '#94a3b8'
        },
        grid: {
          color: 'rgba(148, 163, 184, 0.1)'
        }
      },
      x: {
        ticks: {
          color: '#94a3b8'
        },
        grid: {
          color: 'rgba(148, 163, 184, 0.1)'
        }
      }
    }
  };

  // Check for dynamic charts
  const dynamicChart = registry.charts['dynamic-chart'];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 space-y-6"
    >
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass p-6"
      >
        <h2 className="text-3xl font-bold gradient-text mb-2">Analytics & Reports</h2>
        <p className="text-gray-300 text-sm">Real-time insights and performance metrics</p>
      </motion.div>

      {/* Dynamic Chart Section */}
      {dynamicChart && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
        >
          <ChartRenderer
            chartConfig={dynamicChart.chartConfig}
            title={dynamicChart.title}
            description={dynamicChart.description}
            containerId="dynamic-chart"
          />
        </motion.div>
      )}
      
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { 
            label: 'Total Customers', 
            value: analytics?.statusSummary.total_customers || 0, 
            icon: '👥', 
            color: 'from-blue-500 to-cyan-500',
            bgColor: 'bg-blue-500/10 border-blue-500/30'
          },
          { 
            label: 'Open Tickets', 
            value: analytics?.statusSummary.total_open_tickets || 0, 
            icon: '🎫', 
            color: 'from-orange-500 to-red-500',
            bgColor: 'bg-orange-500/10 border-orange-500/30'
          },
          { 
            label: 'Closed Tickets', 
            value: analytics?.statusSummary.total_closed_tickets || 0, 
            icon: '✅', 
            color: 'from-green-500 to-emerald-500',
            bgColor: 'bg-green-500/10 border-green-500/30'
          },
          { 
            label: 'Resolution Rate', 
            value: totalTickets ? Math.round((analytics?.statusSummary.total_closed_tickets / totalTickets) * 100) : 0, 
            icon: '📊', 
            color: 'from-purple-500 to-pink-500',
            bgColor: 'bg-purple-500/10 border-purple-500/30',
            suffix: '%'
          }
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`glass-strong p-6 border ${stat.bgColor} glow-purple`}
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-2xl">{stat.icon}</span>
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${stat.color} flex items-center justify-center opacity-20`}></div>
            </div>
            <div className="space-y-1">
              <div className={`text-3xl font-bold bg-gradient-to-r ${stat.color} bg-clip-text text-transparent`}>
                <AnimatedCounter value={stat.value} />
                {stat.suffix}
              </div>
              <div className="text-sm text-gray-300">{stat.label}</div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Ticket Status Doughnut Chart */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="glass-strong p-6 glow"
        >
          <h3 className="text-xl font-semibold text-white mb-6 flex items-center">
            <span className="mr-2">📊</span>
            Ticket Status Distribution
          </h3>
          <div className="h-64 flex items-center justify-center">
            {analytics && <Doughnut data={doughnutData} options={chartOptions} />}
          </div>
        </motion.div>

        {/* Customer Activity Bar Chart */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-strong p-6 glow"
        >
          <h3 className="text-xl font-semibold text-white mb-6 flex items-center">
            <span className="mr-2">📈</span>
            Top Customers Activity
          </h3>
          <div className="h-64">
            {analytics && <Bar data={barData} options={chartOptions} />}
          </div>
        </motion.div>

        {/* Customer Rankings */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-strong p-6 lg:col-span-2 glow-purple"
        >
          <h3 className="text-xl font-semibold text-white mb-6 flex items-center">
            <span className="mr-2">🏆</span>
            Customer Activity Rankings
          </h3>
          
          {analytics && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {analytics.customerStats.slice(0, 8).map((customer, index) => (
                <motion.div
                  key={customer.customer}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + (index * 0.05) }}
                  className="bg-white/5 border border-white/10 rounded-xl p-4 hover:bg-white/10 transition-all duration-200"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <motion.div 
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ delay: 0.7 + (index * 0.05), type: "spring" }}
                        className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold text-white ${
                          index === 0 ? 'bg-gradient-to-r from-yellow-400 to-orange-500' :
                          index === 1 ? 'bg-gradient-to-r from-gray-300 to-gray-500' :
                          index === 2 ? 'bg-gradient-to-r from-amber-600 to-yellow-700' :
                          'bg-gradient-to-r from-indigo-500 to-purple-600'
                        }`}
                      >
                        {index + 1}
                      </motion.div>
                      <div>
                        <div className="text-sm font-medium text-white truncate">
                          {customer.customer}
                        </div>
                        <div className="text-xs text-gray-400">Customer</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-indigo-400">
                        <AnimatedCounter value={customer.ticket_count} duration={1500} />
                      </div>
                      <div className="text-xs text-gray-400">tickets</div>
                    </div>
                  </div>
                  <div className="mt-3">
                    <div className="w-full bg-white/10 rounded-full h-2">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ 
                          width: `${analytics.customerStats[0]?.ticket_count ? (customer.ticket_count / analytics.customerStats[0].ticket_count) * 100 : 0}%` 
                        }}
                        transition={{ delay: 0.8 + (index * 0.05), duration: 1 }}
                        className="bg-gradient-to-r from-indigo-500 to-purple-600 h-2 rounded-full"
                      />
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </motion.div>
  );
};

export default AnalyticsView;