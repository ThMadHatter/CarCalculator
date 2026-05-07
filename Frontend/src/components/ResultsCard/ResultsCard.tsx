import React from 'react';
import { Card, Row, Col, Statistic, Divider, Space, Tag, Tooltip } from 'antd';
import { TrophyOutlined, BankOutlined, ToolOutlined, CarOutlined, InfoCircleOutlined } from '@ant-design/icons';
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
    monthly_cost_during_loan,
    monthly_cost_after_loan,
    inflation_impact_total,
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
      <Row gutter={[24, 24]}>
        {/* Primary metrics */}
        <Col xs={24} sm={6}>
          <Statistic
            title="Purchase Price"
            value={purchase_price}
            formatter={value => formatCurrency(value as number)}
            prefix={<CarOutlined />}
          />
        </Col>
        
        <Col xs={24} sm={6}>
          <Statistic
            title="Estimated Final Value"
            value={estimated_final_value}
            formatter={value => formatCurrency(value as number)}
            prefix={<TrophyOutlined />}
          />
        </Col>
        
        <Col xs={24} sm={6}>
          <Statistic
            title={
              <span>
                Avg. Monthly Cost{' '}
                <Tooltip title="Average cost per month over the entire ownership period, including depreciation, maintenance, and loan.">
                  <InfoCircleOutlined style={{ fontSize: '12px' }} />
                </Tooltip>
              </span>
            }
            value={total_monthly_cost}
            formatter={value => formatCurrency(value as number)}
            prefix={<BankOutlined />}
            valueStyle={{ fontWeight: 'bold' }}
          />
        </Col>

        <Col xs={24} sm={6}>
          <Statistic
            title={
              <span>
                Inflation Impact{' '}
                <Tooltip title="Total additional cost due to inflation over the ownership period.">
                  <InfoCircleOutlined style={{ fontSize: '12px' }} />
                </Tooltip>
              </span>
            }
            value={inflation_impact_total}
            formatter={value => `+ ${formatCurrency(value as number)}`}
            valueStyle={{ color: inflation_impact_total > 0 ? '#ff4d4f' : 'inherit', fontSize: '18px' }}
          />
        </Col>
      </Row>

      <Divider style={{ margin: '16px 0' }} />

      <Row gutter={[24, 24]}>
        {/* Period-specific costs */}
        <Col xs={24} sm={8}>
          <Card size="small" type="inner" title="During Loan Period">
            <Statistic
              value={monthly_cost_during_loan || 0}
              formatter={value => formatCurrency(value as number)}
              suffix="/ month"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>

        {monthly_cost_after_loan !== null && (
          <Col xs={24} sm={8}>
            <Card size="small" type="inner" title="After Loan Period">
              <Statistic
                value={monthly_cost_after_loan}
                formatter={value => formatCurrency(value as number)}
                suffix="/ month"
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
        )}

        <Col xs={24} sm={monthly_cost_after_loan !== null ? 8 : 16}>
           <Card size="small" type="inner" title="Value Retention">
            <Statistic
              value={valueRetained}
              formatter={value => `${(value as number).toFixed(1)}%`}
              valueStyle={{
                color: valueRetained > 50 ? '#52c41a' : valueRetained > 30 ? '#fa8c16' : '#ff4d4f'
              }}
            />
          </Card>
        </Col>
      </Row>

      <Divider style={{ margin: '16px 0' }} />

      <Row gutter={[16, 16]}>
        {/* Monthly breakdown */}
        <Col xs={12} sm={6}>
          <Statistic
            title="Monthly Depr."
            value={monthly_depreciation}
            formatter={value => formatCurrency(value as number)}
            valueStyle={{ color: '#ff4d4f', fontSize: '16px' }}
          />
        </Col>
        
        <Col xs={12} sm={6}>
          <Statistic
            title="Avg. Maint."
            value={monthly_maintenance}
            formatter={value => formatCurrency(value as number)}
            prefix={<ToolOutlined />}
            valueStyle={{ color: '#fa8c16', fontSize: '16px' }}
          />
        </Col>
        
        <Col xs={12} sm={6}>
          <Statistic
            title="Loan Payment"
            value={loan_monthly_payment}
            formatter={value => formatCurrency(value as number)}
            prefix={<BankOutlined />}
            valueStyle={{ color: '#1890ff', fontSize: '16px' }}
          />
        </Col>
        
        <Col xs={12} sm={6}>
          <Statistic
            title="Total Interest"
            value={loan_total_interest}
            formatter={value => formatCurrency(value as number)}
            valueStyle={{ color: '#722ed1', fontSize: '16px' }}
          />
        </Col>
      </Row>
    </Card>
  );
};

export default ResultsCard;