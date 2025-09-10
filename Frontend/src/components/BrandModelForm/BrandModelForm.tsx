import React, { useState, useEffect, useCallback } from 'react';
import { Form, AutoComplete, Select, Input, Checkbox, Row, Col, Tooltip } from 'antd';
import { InfoCircleOutlined } from '@ant-design/icons';
import { useBrands } from '../../hooks/useBrands';
import { useModels } from '../../hooks/useModels';
import { generateYearOptions, getCurrentYear } from '../../utils/date';

const { Option } = Select;

interface BrandModelFormProps {
  form: any;
  disabled?: boolean;
}

// Debounce hook
const useDebounce = (value: string, delay: number) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

const BrandModelForm: React.FC<BrandModelFormProps> = ({ form, disabled = false }) => {
  const [brandSearch, setBrandSearch] = useState('');
  const [selectedBrand, setSelectedBrand] = useState('');
  const [manualMode, setManualMode] = useState(false);
  
  const debouncedBrandSearch = useDebounce(brandSearch, 300);
  
  const { data: brandsData, isError: brandsError } = useBrands();
  const { data: modelsData, isError: modelsError } = useModels(selectedBrand);
  
  // Enable manual mode if API fails
  useEffect(() => {
    if (brandsError || modelsError) {
      setManualMode(true);
    }
  }, [brandsError, modelsError]);

  const brands = brandsData?.brands || [];
  const models = modelsData?.models || [];

  // Filter brands for autocomplete
  const filteredBrands = brands.filter(brand =>
    brand.toLowerCase().includes(debouncedBrandSearch.toLowerCase())
  );

  const handleBrandSelect = useCallback((value: string) => {
    setSelectedBrand(value);
    form.setFieldsValue({ brand: value, model: undefined });
  }, [form]);

  const handleBrandChange = useCallback((value: string) => {
    setBrandSearch(value);
    if (!value) {
      setSelectedBrand('');
      form.setFieldsValue({ model: undefined });
    }
  }, [form]);

  const yearOptions = generateYearOptions();
  const shiftTypeOptions = [
    { label: 'Manual', value: 'M' },
    { label: 'Automatic', value: 'A' },
    { label: 'Semi-automatic', value: 'S' },
  ];

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12}>
          <Form.Item
            name="brand"
            label="Brand"
            rules={[{ required: true, message: 'Please select a brand' }]}
          >
            {manualMode ? (
              <Input
                placeholder="Enter brand manually"
                disabled={disabled}
                aria-label="Car brand"
              />
            ) : (
              <AutoComplete
                placeholder="Search for a brand..."
                disabled={disabled}
                filterOption={false}
                onSearch={handleBrandChange}
                onSelect={handleBrandSelect}
                aria-label="Car brand autocomplete"
                options={filteredBrands.map(brand => ({ value: brand, label: brand }))}
              />
            )}
          </Form.Item>
        </Col>
        
        <Col xs={24} sm={12}>
          <Form.Item
            name="model"
            label="Model"
            rules={[{ required: true, message: 'Please select a model' }]}
          >
            {manualMode ? (
              <Input
                placeholder="Enter model manually"
                disabled={disabled}
                aria-label="Car model"
              />
            ) : (
              <Select
                placeholder="Select a model"
                disabled={disabled || !selectedBrand}
                showSearch
                aria-label="Car model"
                notFoundContent={selectedBrand ? "No models found" : "Please select a brand first"}
              >
                {models.map(model => (
                  <Option key={model} value={model}>
                    {model}
                  </Option>
                ))}
              </Select>
            )}
          </Form.Item>
        </Col>
        
        <Col xs={24}>
          <Form.Item
            name="details"
            label={
              <span>
                Details{' '}
                <Tooltip title="Additional information about trim, options, or special features">
                  <InfoCircleOutlined />
                </Tooltip>
              </span>
            }
          >
            <Input
              placeholder="e.g., Sport package, leather seats..."
              disabled={disabled}
              aria-label="Car details and options"
            />
          </Form.Item>
        </Col>
        
        <Col xs={24} sm={8}>
          <Form.Item
            name="registration_year"
            label={
              <span>
                Registration Year{' '}
                <Tooltip title="The year when the car was first registered">
                  <InfoCircleOutlined />
                </Tooltip>
              </span>
            }
            initialValue={getCurrentYear()}
            rules={[{ required: true, message: 'Please select registration year' }]}
          >
            <Select
              placeholder="Select year"
              disabled={disabled}
              aria-label="Car registration year"
            >
              {yearOptions.map(year => (
                <Option key={year.value} value={year.value}>
                  {year.label}
                </Option>
              ))}
            </Select>
          </Form.Item>
        </Col>
        
        <Col xs={24} sm={8}>
          <Form.Item
            name="number_of_years"
            label={
              <span>
                Ownership Period{' '}
                <Tooltip title="How many years you plan to own the car">
                  <InfoCircleOutlined />
                </Tooltip>
              </span>
            }
            initialValue={10}
            rules={[
              { required: true, message: 'Please enter ownership period' },
              { type: 'number', min: 1, max: 30, message: 'Must be between 1 and 30 years' }
            ]}
          >
            <Select
              placeholder="Years"
              disabled={disabled}
              aria-label="Ownership period in years"
            >
              {Array.from({ length: 30 }, (_, i) => i + 1).map(year => (
                <Option key={year} value={year}>
                  {year} year{year > 1 ? 's' : ''}
                </Option>
              ))}
            </Select>
          </Form.Item>
        </Col>
        
        <Col xs={24} sm={8}>
          <Form.Item
            name="purchase_year_index"
            label={
              <span>
                Vehicle Age{' '}
                <Tooltip title="Age of the vehicle at the time of purchase (0 = brand new, 1 = 1 year old, etc.)">
                  <InfoCircleOutlined />
                </Tooltip>
              </span>
            }
            initialValue={0}
            rules={[
              { required: true, message: 'Please enter purchase year' },
              { type: 'number', min: 0, message: 'Must be at least 0' }
            ]}
          >
            <Select
              placeholder="Select purchase timing"
              disabled={disabled}
              aria-label="Purchase year index"
            >
              {Array.from({ length: 20 }, (_, i) => (
                <Option key={i} value={i}>
                  {i === 0
                    ? 'Brand new'
                    : `${i} year${i > 1 ? 's' : ''} old`}
                </Option>
              ))}
            </Select>
          </Form.Item>
        </Col>
        
        <Col xs={24} sm={12}>
          <Form.Item
            name="zip_code"
            label={
              <span>
                Location{' '}
                <Tooltip title="ZIP code or city for regional pricing">
                  <InfoCircleOutlined />
                </Tooltip>
              </span>
            }
            rules={[{ required: true, message: 'Please enter your location' }]}
          >
            <Input
              placeholder="e.g., 10139-torino"
              disabled={disabled}
              aria-label="ZIP code or location"
            />
          </Form.Item>
        </Col>
        
        <Col xs={24} sm={12}>
          <Form.Item
            name="shift_types"
            label="Transmission"
            initialValue={['M']}
            rules={[{ required: true, message: 'Please select at least one transmission type' }]}
          >
            <Checkbox.Group
              options={shiftTypeOptions}
              disabled={disabled}
            />
          </Form.Item>
        </Col>
      </Row>
    </div>
  );
};

export default BrandModelForm;