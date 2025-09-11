import React, { useState } from 'react';
import { Modal, Form, InputNumber, Button, Alert, Spin, Space } from 'antd';
import { CalculatorOutlined } from '@ant-design/icons';
import { useBreakEvenAnalysis } from '../../hooks/useBreakEvenAnalysis';
import { EstimateRequest, BreakEvenAnalysisResponse } from '../../types/api';
import BreakEvenChart from '../Charts/BreakEvenChart';

interface BreakEvenModalProps {
  visible: boolean;
  onCancel: () => void;
  estimateData: EstimateRequest;
}

const BreakEvenModal: React.FC<BreakEvenModalProps> = ({ 
  visible, 
  onCancel, 
  estimateData 
}) => {
  const [form] = Form.useForm();
  const [results, setResults] = useState<BreakEvenAnalysisResponse | null>(null);
  const breakEvenMutation = useBreakEvenAnalysis();

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      const payload = {
        brand: estimateData.brand,
        model: estimateData.model,
        details: estimateData.details,
        zip_code: estimateData.zip_code,
        monthly_maintenance: estimateData.monthly_maintenance,
        rent_monthly_cost: values.rent_monthly_cost,
        max_years: values.years,
        shift_types: estimateData.shift_types
      };
      
      const response = await breakEvenMutation.mutateAsync(payload);
      setResults(response);
    } catch (error) {
      console.error('Break-even analysis failed:', error);
    }
  };

  const handleCancel = () => {
    setResults(null);
    form.resetFields();
    onCancel();
  };

  return (
    <Modal
      title={
        <Space>
          <CalculatorOutlined />
          Break-Even Analysis: Buying vs Renting
        </Space>
      }
      open={visible}
      onCancel={handleCancel}
      width={800}
      footer={null}
    >
      <Spin spinning={breakEvenMutation.isPending}>
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            rent_monthly_cost: 400,
            years: 5,
          }}
        >
          <div style={{ marginBottom: 16 }}>
            <Alert
              message="Compare the total cost of ownership"
              description="Enter the monthly rent cost to see when buying becomes more cost-effective than renting."
              type="info"
              showIcon
            />
          </div>

          <Form.Item
            name="rent_monthly_cost"
            label="Monthly Rent Cost"
            rules={[
              { required: true, message: 'Please enter monthly rent cost' },
              { type: 'number', min: 1, message: 'Rent cost must be positive' }
            ]}
          >
            <InputNumber
              placeholder="€400"
              style={{ width: '100%' }}
              min={1}
              max={5000}
              step={50}
              formatter={value => `€ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
              parser={value => value!.replace(/€\s?|(,*)/g, '') as any}
              aria-label="Monthly rent cost in euros"
            />
          </Form.Item>

          <Form.Item
            name="years"
            label="Analysis Period"
            rules={[
              { required: true, message: 'Please enter analysis period' },
              { type: 'number', min: 1, max: 20, message: 'Period must be between 1 and 20 years' }
            ]}
          >
            <InputNumber
              placeholder="5"
              style={{ width: '100%' }}
              min={1}
              max={20}
              step={1}
              formatter={value => `${value} years`}
              parser={value => value!.replace(' years', '') as any}
              aria-label="Analysis period in years"
            />
          </Form.Item>

          <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
            <Button onClick={handleCancel}>
              Cancel
            </Button>
            <Button 
              type="primary" 
              onClick={handleSubmit}
              loading={breakEvenMutation.isPending}
              icon={<CalculatorOutlined />}
            >
              Analyze Break-Even Point
            </Button>
          </Space>
        </Form>

        {breakEvenMutation.isError && (
          <Alert
            message="Analysis Failed"
            description="Unable to perform break-even analysis. Please check your inputs and try again."
            type="error"
            style={{ marginTop: 16 }}
          />
        )}

        {results && (
          <div style={{ marginTop: 24 }}>
            <BreakEvenChart
              data={results}
            />
          </div>
        )}
      </Spin>
    </Modal>
  );
};

export default BreakEvenModal;