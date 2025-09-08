import { describe, it, expect } from 'vitest';
import { render, screen } from '../../test/test-utils';
import userEvent from '@testing-library/user-event';
import { Form } from 'antd';
import LoanSection from './LoanSection';

const TestWrapper = ({ disabled = false }) => {
  const [form] = Form.useForm();
  return (
    <Form form={form}>
      <LoanSection disabled={disabled} />
    </Form>
  );
};

describe('LoanSection', () => {
  it('renders all loan form fields', () => {
    render(<TestWrapper />);
    
    expect(screen.getByLabelText(/loan amount/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/interest rate/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/loan term/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/monthly maintenance/i)).toBeInTheDocument();
  });

  it('has correct default values', () => {
    render(<TestWrapper />);
    
    expect(screen.getByDisplayValue('€ 0')).toBeInTheDocument();
    expect(screen.getByDisplayValue('5.5%')).toBeInTheDocument();
    expect(screen.getByDisplayValue('5 years')).toBeInTheDocument();
    expect(screen.getByDisplayValue('€ 120')).toBeInTheDocument();
  });

  it('formats currency inputs correctly', async () => {
    const user = userEvent.setup();
    render(<TestWrapper />);
    
    const loanAmountInput = screen.getByLabelText(/loan amount/i);
    
    await user.clear(loanAmountInput);
    await user.type(loanAmountInput, '25000');
    
    expect(screen.getByDisplayValue('€ 25,000')).toBeInTheDocument();
  });

  it('formats percentage inputs correctly', async () => {
    const user = userEvent.setup();
    render(<TestWrapper />);
    
    const interestRateInput = screen.getByLabelText(/interest rate/i);
    
    await user.clear(interestRateInput);
    await user.type(interestRateInput, '3.5');
    
    expect(screen.getByDisplayValue('3.5%')).toBeInTheDocument();
  });

  it('disables all inputs when disabled prop is true', () => {
    render(<TestWrapper disabled />);
    
    const loanAmountInput = screen.getByLabelText(/loan amount/i);
    const interestRateInput = screen.getByLabelText(/interest rate/i);
    const loanTermInput = screen.getByLabelText(/loan term/i);
    const maintenanceInput = screen.getByLabelText(/monthly maintenance/i);
    
    expect(loanAmountInput).toBeDisabled();
    expect(interestRateInput).toBeDisabled();
    expect(loanTermInput).toBeDisabled();
    expect(maintenanceInput).toBeDisabled();
  });

  it('shows validation errors for invalid inputs', async () => {
    const [form] = Form.useForm();
    render(
      <Form form={form}>
        <LoanSection />
      </Form>
    );
    
    // Set invalid values
    form.setFieldsValue({
      loan_value: -1000,
      bank_rate_percent: 35,
      loan_years: 15,
    });
    
    try {
      await form.validateFields();
    } catch (errors) {
      const errorFields = errors.errorFields || [];
      expect(errorFields.some((field: any) => 
        field.name[0] === 'loan_value' && field.errors[0].includes('positive')
      )).toBe(true);
      expect(errorFields.some((field: any) => 
        field.name[0] === 'bank_rate_percent' && field.errors[0].includes('between 0% and 30%')
      )).toBe(true);
      expect(errorFields.some((field: any) => 
        field.name[0] === 'loan_years' && field.errors[0].includes('between 1 and 10 years')
      )).toBe(true);
    }
  });
});