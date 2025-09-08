import React from 'react';
import { Card, Row, Col, Statistic, Divider, Space, Tag } from 'antd';
import { TrophyOutlined, BankOutlined, ToolOutlined, CarOutlined } from '@ant-design/icons';
import { EstimateResponse } from '../../types/api';
import { formatCurrency } from '../../utils/numbers';

interface ResultsCardProps {
  results: EstimateResponse;
}

const ResultsCard: React.FC<ResultsCardProps> = ({ results }) => {
  const {
    purchase_price,
    estimated_final_value,
    monthly_depreciation,
    monthly_maintenance,
    loan_monthly_payment,
    loan_total_interest,
    total_monthly_cost,
  } = results;

  const totalDepreciation = purchase_price - estimated_final_value;
  const valueRetained = (estimated_final_value / purchase_price) * 100;

  return (
    <Card 
      title={
        <Space>
          <TrophyOutlined />
          Cost Analysis Results
        </Space>
      }
      style={{ marginBottom: 16 }}
    >
      <Row gutter={[16, 16]}>
        {/* Primary metrics */}
        <Col xs={24} sm={8}>
          <Statistic
            title="Purchase Price"
            value={purchase_price}
            formatter={value => formatCurrency(value as number)}
            prefix={<CarOutlined />}
          />
        </Col>
        
        <Col xs={24} sm={8}>
          <Statistic
            title="Estimated Final Value"
            value={estimated_final_value}
            formatter={value => formatCurrency(value as number)}
            prefix={<TrophyOutlined />}
          />
        </Col>
        
        <Col xs={24} sm={8}>
          <div>
            <Statistic
              title="Total Monthly Cost"
              value={total_monthly_cost}
              formatter={value => formatCurrency(value as number)}
              prefix={<BankOutlined />}
            />
            <Tag color="blue" style={{ marginTop: 4 }}>
              All expenses included
            </Tag>
          </div>
        </Col>
      </Row>

      <Divider />

      <Row gutter={[16, 16]}>
        {/* Monthly breakdown */}
        <Col xs={24} sm={6}>
          <Statistic
            title="Monthly Depreciation"
            value={monthly_depreciation}
            formatter={value => formatCurrency(value as number)}
            valueStyle={{ color: '#ff4d4f' }}
          />
        </Col>
        
        <Col xs={24} sm={6}>
          <Statistic
            title="Monthly Maintenance"
            value={monthly_maintenance}
            formatter={value => formatCurrency(value as number)}
            prefix={<ToolOutlined />}
            valueStyle={{ color: '#fa8c16' }}
          />
        </Col>
        
        <Col xs={24} sm={6}>
          <Statistic
            title="Loan Payment"
            value={loan_monthly_payment}
            formatter={value => formatCurrency(value as number)}
            prefix={<BankOutlined />}
            valueStyle={{ color: '#1890ff' }}
          />
        </Col>
        
        <Col xs={24} sm={6}>
          <Statistic
            title="Total Interest"
            value={loan_total_interest}
            formatter={value => formatCurrency(value as number)}
            valueStyle={{ color: '#722ed1' }}
          />
        </Col>
      </Row>

      <Divider />

      <Row gutter={[16, 16]}>
        {/* Additional insights */}
        <Col xs={24} sm={12}>
          <Statistic
            title="Total Depreciation"
            value={totalDepreciation}
            formatter={value => formatCurrency(value as number)}
            valueStyle={{ color: '#ff4d4f' }}
          />
          <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
            Over entire ownership period
          </div>
        </Col>
        
        <Col xs={24} sm={12}>
          <Statistic
            title="Value Retention"
            value={valueRetained}
            formatter={value => `${(value as number).toFixed(1)}%`}
            valueStyle={{ 
              color: valueRetained > 50 ? '#52c41a' : valueRetained > 30 ? '#fa8c16' : '#ff4d4f' 
            }}
          />
          <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
            Percentage of original value retained
          </div>
        </Col>
      </Row>
    </Card>
  );
};

export default ResultsCard;