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
import { CalculatorOutlined, ArrowsAltOutlined } from '@ant-design/icons';
import BrandModelForm from '../components/BrandModelForm/BrandModelForm';
import LoanSection from '../components/LoanSection/LoanSection';
import ResultsCard from '../components/ResultsCard/ResultsCard';
import CarValueChart from '../components/Charts/CarValueChart';
import BreakEvenModal from '../components/BreakEvenModal/BreakEvenModal';
import SavedStudies from '../components/SavedStudies/SavedStudies';
import { useEstimate } from '../hooks/useEstimate';
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
  const [breakEvenModalVisible, setBreakEvenModalVisible] = useState(false);
  const [manualPriceMode, setManualPriceMode] = useState(false);
  const [errorBanner, setErrorBanner] = useState<ErrorBanner | null>(null);

  const estimateMutation = useEstimate();

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
        loan_value: values.loan_value,
        bank_rate_percent: values.bank_rate_percent,
        loan_years: values.loan_years,
        shift_types: values.shift_types,
      };

      const response = await estimateMutation.mutateAsync(payload);
      setResults(response);

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

  const handleCompareToRenting = () => {
    if (results) {
      setBreakEvenModalVisible(true);
    }
  };

  const handleLoadStudy = useCallback((data: EstimateRequest) => {
    form.setFieldsValue(data);
    setResults(null);
    setManualPriceMode(false);
    setErrorBanner(null);
  }, [form]);

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

        <Card 
          title={
            <Space>
              <CalculatorOutlined />
              Car Price Estimator
            </Space>
          }
          style={{ marginBottom: 24 }}
        >
          <Row gutter={[24, 24]}>
            <Col xs={24} lg={16}>
              <Form
                form={form}
                layout="vertical"
                requiredMark="optional"
              >
                <Card title="Vehicle Information" size="small" style={{ marginBottom: 16 }}>
                  <BrandModelForm form={form} disabled={estimateMutation.isPending} />
                </Card>

                <LoanSection disabled={estimateMutation.isPending} />

                {manualPriceMode && (
                  <Card title="Manual Price Entry" size="small" style={{ marginBottom: 16 }}>
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

                <Space style={{ width: '100%', justifyContent: 'center' }}>
                  <Button
                    type="primary"
                    size="large"
                    icon={<CalculatorOutlined />}
                    onClick={handleSubmit}
                    loading={estimateMutation.isPending}
                  >
                    Simulate Car Costs
                  </Button>
                  
                  {results && (
                    <Button
                      type="default"
                      size="large"
                      icon={<ArrowsAltOutlined />}
                      onClick={handleCompareToRenting}
                      disabled={estimateMutation.isPending}
                    >
                      Compare to Renting
                    </Button>
                  )}
                </Space>
              </Form>
            </Col>

            <Col xs={24} lg={8}>
              <SavedStudies 
                currentData={isFormValid ? currentFormData : undefined}
                onLoadStudy={handleLoadStudy}
              />
            </Col>
          </Row>
        </Card>

        {results && (
          <div id="results-section">
            <ResultsCard results={results} />
            
            <CarValueChart
              yearValues={results.year_values}
              stdDev={results.price_stddev}
              registrationYear={currentFormData.registration_year}
              purchaseYearIndex={currentFormData.purchase_year_index}
            />
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

        <BreakEvenModal
          visible={breakEvenModalVisible}
          onCancel={() => setBreakEvenModalVisible(false)}
          estimateData={currentFormData}
        />
      </div>
    </div>
  );
};

export default EstimatorPage;
