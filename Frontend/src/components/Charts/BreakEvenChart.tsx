import React from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  ReferenceLine,
  Legend
} from 'recharts';
import { formatCurrency } from '../../utils/numbers';

interface BreakEvenChartProps {
  buyMonthlySeries: number[];
  rentMonthlySeries: number[];
  monthsToBreakEven: number | null;
  years: number;
}

const BreakEvenChart: React.FC<BreakEvenChartProps> = ({ 
  buyMonthlySeries, 
  rentMonthlySeries, 
  monthsToBreakEven,
  years 
}) => {
  // Calculate cumulative costs
  const chartData = buyMonthlySeries.map((buyCost, index) => {
  const month = index + 1;
  const rentCost = rentMonthlySeries[index] || 0;

  const cumulativeBuyCost = buyMonthlySeries.slice(0, index + 1).reduce((sum, cost) => sum + cost, 0);
  const cumulativeRentCost = rentMonthlySeries.slice(0, index + 1).reduce((sum, cost) => sum + cost, 0);

  return {
    month,
    buyCumulative: cumulativeBuyCost,
    rentCumulative: cumulativeRentCost,
    buyMonthly: buyCost,
    rentMonthly: rentCost,
  };
});


  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const monthLabel = `Month ${label}`;
      const yearLabel = `Year ${Math.ceil(label / 12)}`;
      
      return (
        <div className="bg-white p-3 border rounded shadow-lg">
          <p className="font-medium">{monthLabel} ({yearLabel})</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: {formatCurrency(entry.value)}
            </p>
          ))}
          {monthsToBreakEven === label && (
            <p className="text-green-600 text-sm font-medium">
              🎯 Break-Even Point
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ height: 400, width: '100%' }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
          <XAxis 
            dataKey="month"
            tickFormatter={(value) => `M${value}`}
          />
          <YAxis 
            tickFormatter={(value) => formatCurrency(value).replace('€', '€')}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          
          {/* Reference line for break-even point */}
          {monthsToBreakEven && (
            <ReferenceLine 
              x={monthsToBreakEven} 
              stroke="#52c41a" 
              strokeWidth={2}
              strokeDasharray="5 5"
              label={{ 
                value: `Break-Even (Month ${monthsToBreakEven})`, 
                position: "topLeft" 
              }}
            />
          )}
          
          <Line
            type="monotone"
            dataKey="buyCumulative"
            stroke="#1890ff"
            strokeWidth={3}
            name="Cumulative Buying Cost"
            dot={false}
            activeDot={{ r: 6 }}
          />
          
          <Line
            type="monotone"
            dataKey="rentCumulative"
            stroke="#ff4d4f"
            strokeWidth={3}
            name="Cumulative Renting Cost"
            dot={false}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
      
      <div style={{ 
        fontSize: '12px', 
        color: '#666', 
        marginTop: '8px',
        textAlign: 'center' 
      }}>
        {monthsToBreakEven ? (
          <>
            Break-even occurs at month {monthsToBreakEven} (Year {Math.ceil(monthsToBreakEven / 12)}).
            After this point, buying becomes more cost-effective than renting.
          </>
        ) : (
          'Renting remains more cost-effective throughout the entire period.'
        )}
      </div>
    </div>
  );
};

export default BreakEvenChart;