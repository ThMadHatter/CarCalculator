import React from 'react';
import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Legend,
} from 'recharts';
import { Card, Space } from 'antd';
import { LineChartOutlined } from '@ant-design/icons';
import { formatCurrency } from '../../utils/numbers';

interface CarValueChartProps {
  yearValues: number[];
  stdDev?: (number | undefined)[];
  registrationYear: number;
  purchaseYearIndex: number;
}

const CarValueChart: React.FC<CarValueChartProps> = ({
  yearValues,
  stdDev = [],
  registrationYear,
  purchaseYearIndex,
}) => {
  const chartData = yearValues.map((value, index) => {
    const deviation = stdDev[index];
    const upperBound = deviation !== undefined ? value + deviation : value;
    const lowerBound = deviation !== undefined ? Math.max(0, value - deviation) : value;

    return {
      year: registrationYear + index,
      value,
      isPurchaseYear: index === purchaseYearIndex,
      range: [lowerBound, upperBound],
    };
  });

  const purchaseYear = registrationYear + purchaseYearIndex;

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const value = payload.find((p) => p.dataKey === 'value')?.value;
      const range = payload.find((p) => p.dataKey === 'range')?.value;

      return (
        <div className="bg-white p-3 border rounded shadow-lg">
          <p className="font-medium">Year: {label}</p>
          {value !== undefined && <p className="text-blue-600">Value: {formatCurrency(value)}</p>}
          {range && (
            <p className="text-gray-500 text-sm">
              Confidence Range: {formatCurrency(range[0])} - {formatCurrency(range[1])}
            </p>
          )}
          {data.isPurchaseYear && (
            <p className="text-green-600 text-sm font-medium" style={{ marginTop: 4 }}>
              📅 Purchase Year
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  const hasStdDev = stdDev.some((d) => d !== undefined && d > 0);

  return (
    <Card
      title={
        <Space>
          <LineChartOutlined />
          Car Value Over Time
        </Space>
      }
      style={{ marginBottom: 16 }}
    >
      <ResponsiveContainer width="100%" height={350}>
        <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
          <XAxis
            dataKey="year"
            type="number"
            scale="linear"
            domain={['dataMin', 'dataMax']}
            tickFormatter={(v) => v.toString()}
          />
          <YAxis tickFormatter={(value) => formatCurrency(value, 0)} domain={['dataMin', 'auto']} />
          <Tooltip content={<CustomTooltip />} />
          <Legend verticalAlign="top" height={36} />

          <ReferenceLine
            x={purchaseYear}
            stroke="#52c41a"
            strokeWidth={2}
            strokeDasharray="5 5"
            label={{ value: 'Purchase', position: 'topLeft', fill: '#52c41a' }}
          />

          {hasStdDev && (
            <Area
              dataKey="range"
              stroke={false}
              fill="#1890ff"
              fillOpacity={0.15}
              isAnimationActive={false}
              name="Price Confidence Range"
            />
          )}

          <Line
            type="monotone"
            dataKey="value"
            stroke="#1890ff"
            strokeWidth={3}
            dot={(props: any) => {
              const { cx, cy, payload } = props;
              return (
                <circle
                  cx={cx}
                  cy={cy}
                  r={payload.isPurchaseYear ? 6 : 4}
                  fill={payload.isPurchaseYear ? '#52c41a' : '#1890ff'}
                  stroke={payload.isPurchaseYear ? '#389e0d' : '#096dd9'}
                  strokeWidth={2}
                />
              );
            }}
            activeDot={{ r: 8, stroke: '#1890ff', strokeWidth: 2 }}
            name="Estimated value"
            isAnimationActive={false}
          />
        </ComposedChart>
      </ResponsiveContainer>

      <div style={{ fontSize: '12px', color: '#666', marginTop: '8px', textAlign: 'center' }}>
        {hasStdDev ? (
          <>
            Shaded band shows the estimated price range (±1 standard deviation).
            <br />
            Green dot indicates your purchase year.
          </>
        ) : (
          'Green dot indicates your purchase year. Values shown are estimates based on market data.'
        )}
      </div>
    </Card>
  );
};

export default CarValueChart;
