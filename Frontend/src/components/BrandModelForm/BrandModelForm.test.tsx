import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '../../test/test-utils';
import userEvent from '@testing-library/user-event';
import { Form } from 'antd';
import BrandModelForm from './BrandModelForm';
import { server } from '../../test/msw/server';
import { errorHandlers } from '../../test/msw/handlers';

// Mock component wrapper
const TestWrapper = ({ disabled = false }) => {
  const [form] = Form.useForm();
  return (
    <Form form={form}>
      <BrandModelForm form={form} disabled={disabled} />
    </Form>
  );
};

describe('BrandModelForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders all form fields correctly', () => {
    render(<TestWrapper />);
    
    expect(screen.getByLabelText(/car brand/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/car model/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/car details/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/registration year/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/ownership period/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/purchase year/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/zip code/i)).toBeInTheDocument();
    expect(screen.getByText('Transmission')).toBeInTheDocument();
  });

  it('loads brands and enables autocomplete', async () => {
    render(<TestWrapper />);
    
    const brandInput = screen.getByLabelText(/car brand/i);
    
    // Start typing to trigger autocomplete
    await userEvent.type(brandInput, 'bmw');
    
    await waitFor(() => {
      expect(screen.getByText('bmw')).toBeInTheDocument();
    });
  });

  it('loads models when brand is selected', async () => {
    const user = userEvent.setup();
    render(<TestWrapper />);
    
    const brandInput = screen.getByLabelText(/car brand/i);
    
    // Type and select brand
    await user.type(brandInput, 'bmw');
    await waitFor(() => {
      expect(screen.getByText('bmw')).toBeInTheDocument();
    });
    
    await user.click(screen.getByText('bmw'));
    
    // Check if model dropdown becomes enabled
    const modelSelect = screen.getByLabelText(/car model/i);
    expect(modelSelect).not.toBeDisabled();
  });

  it('debounces brand search input', async () => {
    const user = userEvent.setup();
    render(<TestWrapper />);
    
    const brandInput = screen.getByLabelText(/car brand/i);
    
    // Type quickly
    await user.type(brandInput, 'audi');
    
    // Should not immediately show results due to debounce
    expect(screen.queryByText('audi')).not.toBeInTheDocument();
    
    // Wait for debounce period
    await waitFor(() => {
      expect(screen.getByText('audi')).toBeInTheDocument();
    }, { timeout: 500 });
  });

  it('enables manual mode when API fails', async () => {
    // Override handlers to return 503
    server.use(errorHandlers.brands503);
    
    render(<TestWrapper />);
    
    await waitFor(() => {
      const brandInput = screen.getByLabelText(/car brand/i);
      expect(brandInput.getAttribute('placeholder')).toBe('Enter brand manually');
    });
  });

  it('disables all inputs when disabled prop is true', () => {
    render(<TestWrapper disabled />);
    
    const brandInput = screen.getByLabelText(/car brand/i);
    const modelInput = screen.getByLabelText(/car model/i);
    const detailsInput = screen.getByLabelText(/car details/i);
    
    expect(brandInput).toBeDisabled();
    expect(modelInput).toBeDisabled();
    expect(detailsInput).toBeDisabled();
  });

  it('shows validation errors for required fields', async () => {
    const [form] = Form.useForm();
    render(
      <Form form={form}>
        <BrandModelForm form={form} />
      </Form>
    );
    
    // Try to validate form without filling required fields
    try {
      await form.validateFields();
    } catch (errors) {
      expect(errors.errorFields).toHaveLength(4); // brand, model, zip_code, shift_types
    }
  });
});