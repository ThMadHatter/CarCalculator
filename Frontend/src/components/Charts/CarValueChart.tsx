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
  ReferenceArea,
  Legend
} from 'recharts';
import { Card, Space } from 'antd';
import { LineChartOutlined } from '@ant-design/icons';
import { formatCurrency } from '../../utils/numbers';

interface CarValueChartProps {
  yearValues: number[];              // series (chronological)
  registrationYear: number;          // base year for the first element in yearValues
  purchaseYearIndex: number;         // 0-based index into yearValues (purchase year)
  priceAvg?: number | null;          // optional average price (single value)
  priceStddev?: number | null;       // optional standard deviation (single value)
}

const CarValueChart: React.FC<CarValueChartProps> = ({
  yearValues,
  registrationYear,
  purchaseYearIndex,
  priceAvg = null,
  priceStddev = null
}) => {
  // Defensive defaults
  const avg = typeof priceAvg === 'number' ? priceAvg : null;
  const stddev = typeof priceStddev === 'number' ? Math.max(0, priceStddev) : 0;

  // Precompute band bounds (ensure non-negative lower bound)
  const bandUpper = avg !== null ? avg + stddev : null;
  const bandLower = avg !== null ? Math.max(0, avg - stddev) : null;

  // Transform data for chart.
  // Assumes yearValues[0] corresponds to registrationYear (chronological).
  const chartData = yearValues.map((value, index) => ({
    year: registrationYear + index,
    value,
    avg: avg !== null ? avg : undefined, // same avg value for all points (if available)
    isPurchaseYear: index === purchaseYearIndex
  }));

  const purchaseYear = registrationYear + purchaseYearIndex; // 0-based mapping

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border rounded shadow-lg">
          <p className="font-medium">Year: {label}</p>
          <p className="text-blue-600">Value: {formatCurrency(payload[0].value)}</p>
          {avg !== null && (
            <p className="text-gray-700 text-sm">
              Avg: {formatCurrency(avg)} {stddev ? `(± ${formatCurrency(stddev)})` : ''}
            </p>
          )}
          {data.isPurchaseYear && (
            <p className="text-green-600 text-sm font-medium">📅 Purchase Year</p>
          )}
        </div>
      );
    }
    return null;
  };

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
        <LineChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
          <XAxis
            dataKey="year"
            type="number"
            scale="linear"
            domain={['dataMin', 'dataMax']}
            tickFormatter={(v) => v.toString()}
          />
          <YAxis tickFormatter={(value) => formatCurrency(value)} />
          <Tooltip content={<CustomTooltip />} />
          <Legend verticalAlign="top" height={24} />

          {/* Stddev band (avg ± stddev). Drawn across entire x range when avg is present */}
          {avg !== null && bandLower !== null && bandUpper !== null && (
            <ReferenceArea
              x1={'dataMin'}
              x2={'dataMax'}
              y1={bandLower}
              y2={bandUpper}
              strokeOpacity={0}
              fill="#1890ff"
              fillOpacity={0.12}
            />
          )}

          {/* Reference line for purchase year */}
          <ReferenceLine
            x={purchaseYear}
            stroke="#52c41a"
            strokeWidth={2}
            strokeDasharray="5 5"
            label={{ value: 'Purchase', position: 'topLeft' }}
          />

          {/* Average dashed line (if available) */}
          {avg !== null && (
            <Line
              type="monotone"
              dataKey="avg"
              stroke="#096dd9"
              strokeWidth={2}
              strokeDasharray="4 4"
              dot={false}
              name="Average"
              isAnimationActive={false}
            />
          )}

          {/* Actual value line */}
          <Line
            type="monotone"
            dataKey="value"
            stroke="#1890ff"
            strokeWidth={3}
            dot={(props) => {
              const { cx, cy, payload } = props as any;
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
        </LineChart>
      </ResponsiveContainer>

      <div
        style={{
          fontSize: '12px',
          color: '#666',
          marginTop: '8px',
          textAlign: 'center'
        }}
      >
        {avg !== null ? (
          <>
            Shaded band shows ±1 standard deviation around the average price.
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
