import React from 'react';
import { Form, InputNumber, Card, Row, Col, Tooltip } from 'antd';
import { InfoCircleOutlined } from '@ant-design/icons';

interface LoanSectionProps {
  disabled?: boolean;
}

const LoanSection: React.FC<LoanSectionProps> = ({ disabled = false }) => {
  return (
    <Card 
      title="Loan Information" 
      size="small" 
      style={{ marginBottom: 16 }}
      type="inner"
    >
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={8}>
          <Form.Item
            name="loan_value"
            label={
              <span>
                Loan Amount{' '}
                <Tooltip title="The amount you plan to finance through a loan">
                  <InfoCircleOutlined />
                </Tooltip>
              </span>
            }
            initialValue={0}
            rules={[
              { required: true, message: 'Please enter loan amount' },
              { type: 'number', min: 0, message: 'Loan amount must be positive' }
            ]}
          >
            <InputNumber
              placeholder="€0"
              style={{ width: '100%' }}
              min={0}
              max={200000}
              step={1000}
              formatter={value => `€ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
              parser={value => value!.replace(/€\s?|(,*)/g, '') as any}
              disabled={disabled}
              aria-label="Loan amount in euros"
            />
          </Form.Item>
        </Col>
        
        <Col xs={24} sm={8}>
          <Form.Item
            name="bank_rate_percent"
            label={
              <span>
                Interest Rate{' '}
                <Tooltip title="Annual interest rate offered by your bank">
                  <InfoCircleOutlined />
                </Tooltip>
              </span>
            }
            initialValue={5.5}
            rules={[
              { required: true, message: 'Please enter interest rate' },
              { type: 'number', min: 0, max: 30, message: 'Rate must be between 0% and 30%' }
            ]}
          >
            <InputNumber
              placeholder="5.5"
              style={{ width: '100%' }}
              min={0}
              max={30}
              step={0.1}
              formatter={value => `${value}%`}
              parser={value => value!.replace('%', '') as any}
              disabled={disabled}
              aria-label="Annual interest rate percentage"
            />
          </Form.Item>
        </Col>
        
        <Col xs={24} sm={8}>
          <Form.Item
            name="loan_years"
            label={
              <span>
                Loan Term{' '}
                <Tooltip title="Number of years to repay the loan">
                  <InfoCircleOutlined />
                </Tooltip>
              </span>
            }
            initialValue={5}
            rules={[
              { required: true, message: 'Please enter loan term' },
              { type: 'number', min: 1, max: 10, message: 'Term must be between 1 and 10 years' }
            ]}
          >
            <InputNumber
              placeholder="5"
              style={{ width: '100%' }}
              min={1}
              max={10}
              step={1}
              formatter={value => `${value} years`}
              parser={value => value!.replace(' years', '') as any}
              disabled={disabled}
              aria-label="Loan term in years"
            />
          </Form.Item>
        </Col>
        
        <Col xs={24}>
          <Form.Item
            name="monthly_maintenance"
            label={
              <span>
                Monthly Maintenance{' '}
                <Tooltip title="Expected monthly cost for maintenance, insurance, and other recurring expenses">
                  <InfoCircleOutlined />
                </Tooltip>
              </span>
            }
            initialValue={120}
            rules={[
              { required: true, message: 'Please enter monthly maintenance cost' },
              { type: 'number', min: 0, message: 'Maintenance cost must be positive' }
            ]}
          >
            <InputNumber
              placeholder="€120"
              style={{ width: '100%' }}
              min={0}
              max={2000}
              step={10}
              formatter={value => `€ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
              parser={value => value!.replace(/€\s?|(,*)/g, '') as any}
              disabled={disabled}
              aria-label="Monthly maintenance cost in euros"
            />
          </Form.Item>
        </Col>
      </Row>
    </Card>
  );
};

export default LoanSection;