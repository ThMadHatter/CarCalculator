import React, { useState } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Legend,
  Label
} from 'recharts';
import { Switch, Space, Card, Empty } from 'antd';
import { LineChartOutlined } from '@ant-design/icons';
import { formatCurrency } from '../../utils/numbers';
import { BreakEvenAnalysisResponse } from '../../types/api';

interface BreakEvenChartProps {
  data: BreakEvenAnalysisResponse;
}

type CostType = 'overall_cost' | 'monthly_cost';

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff8042', '#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

const BreakEvenChart: React.FC<BreakEvenChartProps> = ({ data }) => {
  const [costType, setCostType] = useState<CostType>('overall_cost');

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border rounded shadow-lg">
          <p className="font-medium">Years Owned: {label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: {formatCurrency(entry.value)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  const hasData = data && data.purchase_series.some(s => s.data_points.length > 0);

  return (
    <Card
      title={
        <Space>
          <LineChartOutlined />
          Break-Even Analysis
        </Space>
      }
      extra={
        <Space>
          <span>Monthly Cost</span>
          <Switch
            checked={costType === 'overall_cost'}
            onChange={(checked) => setCostType(checked ? 'overall_cost' : 'monthly_cost')}
          />
          <span>Overall Cost</span>
        </Space>
      }
    >
      {hasData ? (
        <ResponsiveContainer width="100%" height={400}>
          <LineChart margin={{ top: 20, right: 30, left: 20, bottom: 40 }}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
            <XAxis 
              dataKey="years_owned"
              type="number"
              allowDuplicatedCategory={false}
            >
              <Label value="Years of Ownership" offset={-20} position="insideBottom" />
            </XAxis>
            <YAxis 
              tickFormatter={(value) => formatCurrency(value, 0)}
            >
              <Label value={costType === 'overall_cost' ? 'Overall Cost' : 'Monthly Cost'} angle={-90} position="insideLeft" style={{ textAnchor: 'middle' }} />
            </YAxis>
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ bottom: 0 }}/>

            <Line
              type="monotone"
              data={data.rental_series}
              dataKey={costType}
              stroke="#ff4d4f"
              strokeWidth={3}
              name="Rental Cost"
              dot={false}
              activeDot={{ r: 6 }}
            />

            {data.purchase_series.map((series, index) => (
              <Line
                key={series.purchase_year}
                type="monotone"
                data={series.data_points}
                dataKey={costType}
                stroke={COLORS[index % COLORS.length]}
                strokeWidth={2}
                name={`Buy in ${series.purchase_year}`}
                dot={false}
                activeDot={{ r: 6 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <div style={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Empty description="No historical data available to perform the analysis." />
        </div>
      )}
    </Card>
  );
};

export default BreakEvenChart;
