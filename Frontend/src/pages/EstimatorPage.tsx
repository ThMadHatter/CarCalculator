import React, { useState, useCallback } from 'react';
import { 
  Form, 
  Button, 
  Card, 
  Row, 
  Col, 
  Space, 
  Spin, 
  notification,
  Input,
  InputNumber,
  Alert
} from 'antd';
import { CalculatorOutlined, InfoCircleOutlined } from '@ant-design/icons';
import BrandModelForm from '../components/BrandModelForm/BrandModelForm';
import LoanSection from '../components/LoanSection/LoanSection';
import ResultsCard from '../components/ResultsCard/ResultsCard';
import CarValueChart from '../components/Charts/CarValueChart';
import BreakEvenChart from '../components/Charts/BreakEvenChart';
import { useEstimate } from '../hooks/useEstimate';
import { useBreakEvenAnalysis } from '../hooks/useBreakEvenAnalysis';
import { EstimateRequest, EstimateResponse } from '../types/api';
import { formatCurrency } from '../utils/numbers';

type ErrorBanner = {
  type: 'error' | 'warning' | 'info' | 'success';
  message: string;
  description?: string;
};

const EstimatorPage: React.FC = () => {
  const [form] = Form.useForm();
  const [results, setResults] = useState<EstimateResponse | null>(null);
  const [breakEvenResults, setBreakEvenResults] = useState<any>(null);
  const [manualPriceMode, setManualPriceMode] = useState(false);
  const [errorBanner, setErrorBanner] = useState<ErrorBanner | null>(null);

  const estimateMutation = useEstimate();
  const breakEvenMutation = useBreakEvenAnalysis();

  const handleSubmit = async () => {
    try {
      setErrorBanner(null);
      setResults(null);

      const values = await form.validateFields();
      const payload: EstimateRequest = {
        brand: values.brand,
        model: values.model,
        details: values.details || '',
        zip_code: values.zip_code,
        registration_year: values.registration_year,
        number_of_years: values.number_of_years,
        purchase_year_index: values.purchase_year_index,
        monthly_maintenance: values.monthly_maintenance,
        inflation_rate: values.apply_inflation ? values.inflation_rate : 0,
        extend_missing_values: values.extend_missing_values,
        loan_value: values.loan_value,
        bank_rate_percent: values.bank_rate_percent,
        loan_years: values.loan_years,
        shift_types: values.shift_types,
      };

      const response = await estimateMutation.mutateAsync(payload);
      setResults(response);

      // Perform break-even analysis automatically
      const breakEvenPayload = {
        brand: payload.brand,
        model: payload.model,
        details: payload.details,
        zip_code: payload.zip_code,
        monthly_maintenance: payload.monthly_maintenance,
        inflation_rate: values.apply_inflation ? values.inflation_rate : 0,
        extend_missing_values: payload.extend_missing_values,
        rent_monthly_cost: values.rent_monthly_cost || 400,
        loan_value: payload.loan_value,
        bank_rate_percent: payload.bank_rate_percent,
        loan_years: payload.loan_years,
        max_years: Math.round(payload.number_of_years * 1.5),
        shift_types: payload.shift_types
      };

      try {
        const beResponse = await breakEvenMutation.mutateAsync(breakEvenPayload);
        setBreakEvenResults(beResponse);
      } catch (error) {
        console.error('Break-even analysis failed:', error);
      }

      if (response.warning) {
        notification.warning({
          message: 'Warning',
          description: response.warning,
          duration: 10,
        });
      }
      
      if (response.adjusted_number_of_years) {
        form.setFieldsValue({ number_of_years: response.adjusted_number_of_years });
      }

      document.getElementById('results-section')?.scrollIntoView({ 
        behavior: 'smooth' 
      });
      
    } catch (error: any) {
      if (error?.response?.status === 422) {
        const validationErrors = error.response.data?.details || {};
        const formErrors = Object.entries(validationErrors).map(([field, messages]: [string, any]) => ({
          name: [field],
          errors: Array.isArray(messages) ? messages : [messages]
        }));
        
        form.setFields(formErrors);
        notification.error({
          message: 'Validation Error',
          description: 'Please check the highlighted fields and try again.',
        });

      } else if (error?.response?.status === 503) {
        setManualPriceMode(true);
        notification.warning({
          message: 'Service Temporarily Unavailable',
          description: 'Price data is currently unavailable. You can enter a manual purchase price below.',
        });

      } else {
        notification.error({
          message: 'Request Failed',
          description: error?.message || 'An unexpected error occurred.',
        });
      }
    }
  };

  const currentFormData = form.getFieldsValue() as EstimateRequest;
  const isFormValid = currentFormData.brand && currentFormData.model && 
                     currentFormData.zip_code && currentFormData.registration_year;

  return (
    <div style={{ padding: '24px', backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        {errorBanner && (
          <div style={{ marginBottom: 16 }}>
            <Alert
              message={errorBanner.message}
              description={errorBanner.description}
              type={errorBanner.type}
              showIcon
              closable
              onClose={() => setErrorBanner(null)}
            />
          </div>
        )}

        <Form
          form={form}
          layout="vertical"
          requiredMark="optional"
          initialValues={{
            rent_monthly_cost: 400
          }}
        >
          <Row gutter={[24, 24]}>
            <Col xs={24} lg={12}>
              <Card title="Vehicle Information" size="small" style={{ height: '100%' }}>
                <BrandModelForm form={form} disabled={estimateMutation.isPending} />
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card title="Financial Parameters" size="small" style={{ height: '100%' }}>
                <LoanSection disabled={estimateMutation.isPending} />
                <Form.Item
                  name="rent_monthly_cost"
                  label={
                    <span>
                      Monthly Rent Cost{' '}
                      <Tooltip title="Monthly cost of renting a similar car for comparison">
                        <InfoCircleOutlined />
                      </Tooltip>
                    </span>
                  }
                  rules={[
                    { required: true, message: 'Please enter monthly rent cost' },
                    { type: 'number', min: 0, message: 'Rent cost must be positive' }
                  ]}
                >
                  <InputNumber
                    placeholder="€400"
                    style={{ width: '100%' }}
                    min={0}
                    max={5000}
                    step={50}
                    formatter={value => `€ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                    parser={value => value!.replace(/€\s?|(,*)/g, '') as any}
                    disabled={estimateMutation.isPending}
                  />
                </Form.Item>
              </Card>
            </Col>
          </Row>

          {manualPriceMode && (
            <Card title="Manual Price Entry" size="small" style={{ marginTop: 16 }}>
              <Alert
                message="Service Unavailable"
                description="Since price data is temporarily unavailable, please enter the purchase price manually."
                type="warning"
                showIcon
                style={{ marginBottom: 16 }}
              />
              <Form.Item
                name="manual_purchase_price"
                label="Purchase Price"
                rules={[
                  { required: true, message: 'Please enter purchase price' },
                  { type: 'number', min: 1000, message: 'Price must be at least €1,000' }
                ]}
              >
                <InputNumber
                  placeholder="€30,000"
                  style={{ width: '100%' }}
                  min={1000}
                  max={500000}
                  step={1000}
                  formatter={value => `€ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                  parser={value => value!.replace(/€\s?|(,*)/g, '') as any}
                  disabled={estimateMutation.isPending}
                />
              </Form.Item>
            </Card>
          )}

          <div style={{ textAlign: 'center', marginTop: 24, marginBottom: 24 }}>
            <Button
              type="primary"
              size="large"
              icon={<CalculatorOutlined />}
              onClick={handleSubmit}
              loading={estimateMutation.isPending}
              style={{ minWidth: 200 }}
            >
              Simulate Car Costs
            </Button>
          </div>
        </Form>

        {results && (
          <div id="results-section">
            <ResultsCard results={results} />
            
            <Row gutter={[16, 16]}>
              <Col xs={24} lg={12}>
                <CarValueChart
                  yearValues={results.year_values}
                  stdDev={results.price_stddev}
                  isSimulated={results.is_simulated}
                  registrationYear={currentFormData.registration_year}
                  purchaseYearIndex={currentFormData.purchase_year_index}
                />
              </Col>
              <Col xs={24} lg={12}>
                {breakEvenResults && (
                  <BreakEvenChart data={breakEvenResults} />
                )}
              </Col>
            </Row>
          </div>
        )}

        {estimateMutation.isPending && results && (
          <Card style={{ textAlign: 'center', marginTop: 16 }}>
            <Spin size="large" />
            <div style={{ marginTop: 16 }}>
              Calculating updated estimates...
            </div>
          </Card>
        )}

      </div>
    </div>
  );
};

export default EstimatorPage;
