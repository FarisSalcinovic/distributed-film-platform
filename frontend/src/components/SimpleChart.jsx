// frontend/src/components/SimpleChart.jsx
import React from 'react';
import { Bar, Line, Pie, Doughnut } from 'react-chartjs-2';
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
  Legend
} from 'chart.js';

// Registruj ChartJS komponente
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const SimpleChart = ({ type = 'bar', title = 'Chart', data, options }) => {
  const defaultOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: title,
      },
    },
  };

  const mergedOptions = { ...defaultOptions, ...options };

  const renderChart = () => {
    switch (type) {
      case 'bar':
        return <Bar data={data} options={mergedOptions} />;
      case 'line':
        return <Line data={data} options={mergedOptions} />;
      case 'pie':
        return <Pie data={data} options={mergedOptions} />;
      case 'doughnut':
        return <Doughnut data={data} options={mergedOptions} />;
      default:
        return <Bar data={data} options={mergedOptions} />;
    }
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow">
      {renderChart()}
    </div>
  );
};

export default SimpleChart;