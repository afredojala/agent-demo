import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Chart } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface ChartRendererProps {
  chartConfig: any;
  title?: string;
  description?: string;
  containerId: string;
}

const ChartRenderer: React.FC<ChartRendererProps> = ({ 
  chartConfig, 
  title, 
  description, 
  containerId 
}) => {
  const chartRef = useRef<any>(null);

  useEffect(() => {
    // Clean up previous chart instance
    if (chartRef.current) {
      chartRef.current.destroy();
    }
  }, [chartConfig]);

  if (!chartConfig) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-strong p-6 text-center"
      >
        <div className="text-gray-300">
          <div className="text-4xl mb-2">📊</div>
          <div className="text-lg">Waiting for chart data...</div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.5, type: "spring" }}
      className="glass-strong p-6 glow"
      id={containerId}
    >
      {title && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-4"
        >
          <h3 className="text-xl font-semibold text-white flex items-center">
            <span className="mr-2">📈</span>
            {title}
          </h3>
          {description && (
            <p className="text-sm text-gray-300 mt-1">{description}</p>
          )}
        </motion.div>
      )}
      
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3, duration: 0.4 }}
        className="h-64 md:h-80"
      >
        <Chart
          ref={chartRef}
          type={chartConfig.type}
          data={chartConfig.data}
          options={{
            ...chartConfig.options,
            responsive: true,
            maintainAspectRatio: false,
            animation: {
              duration: 1500,
              easing: 'easeInOutQuart',
            },
          }}
        />
      </motion.div>
      
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="mt-4 text-xs text-gray-400 text-center"
      >
        🤖 Generated dynamically by AI agent
      </motion.div>
    </motion.div>
  );
};

export default ChartRenderer;