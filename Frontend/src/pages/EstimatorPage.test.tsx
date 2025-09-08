import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '../test/test-utils';
import userEvent from '@testing-library/user-event';
import EstimatorPage from './EstimatorPage';
import { server } from '../test/msw/server';
import { errorHandlers } from '../test/msw/handlers';

// Mock console.error to avoid noise in tests
const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

describe('EstimatorPage', () => {
  afterEach(() => {
    consoleSpy.mockClear();
  });

  it('renders the main form and components', async () => {
    render(<EstimatorPage />);
    
    expect(screen.getByText('Car Price Estimator')).toBeInTheDocument();
    expect(screen.getByText('Vehicle Information')).toBeInTheDocument();
    expect(screen.getByText('Loan Information')).toBeInTheDocument();
    expect(screen.getByText('Saved Studies')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /simulate car costs/i })).toBeInTheDocument();
  });

  it('performs successful estimation flow', async () => {
    const user = userEvent.setup();
    render(<EstimatorPage />);
    
    // Fill out the form
    const brandInput = screen.getByLabelText(/car brand/i);
    await user.type(brandInput, 'bmw');
    await waitFor(() => screen.getByText('bmw'));
    await user.click(screen.getByText('bmw'));
    
    // Wait for models to load and select one
    await waitFor(() => {
      const modelSelect = screen.getByLabelText(/car model/i);
      expect(modelSelect).not.toBeDisabled();
    });
    
    await user.click(screen.getByLabelText(/car model/i));
    await waitFor(() => screen.getByText('320i'));
    await user.click(screen.getByText('320i'));
    
    // Fill location
    const locationInput = screen.getByLabelText(/zip code/i);
    await user.type(locationInput, '10139-torino');
    
    // Submit form
    const simulateButton = screen.getByRole('button', { name: /simulate car costs/i });
    await user.click(simulateButton);
    
    // Wait for results
    await waitFor(() => {
      expect(screen.getByText('Cost Analysis Results')).toBeInTheDocument();
    });
    
    expect(screen.getByText('Purchase Price')).toBeInTheDocument();
    expect(screen.getByText('Car Value Over Time')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /compare to renting/i })).toBeInTheDocument();
  });

  it('handles API errors and shows manual price mode', async () => {
    server.use(errorHandlers.estimate503);
    
    const user = userEvent.setup();
    render(<EstimatorPage />);
    
    // Fill and submit form
    const brandInput = screen.getByLabelText(/car brand/i);
    await user.type(brandInput, 'bmw');
    await waitFor(() => screen.getByText('bmw'));
    await user.click(screen.getByText('bmw'));
    
    const locationInput = screen.getByLabelText(/zip code/i);
    await user.type(locationInput, '10139-torino');
    
    const simulateButton = screen.getByRole('button', { name: /simulate car costs/i });
    await user.click(simulateButton);
    
    // Should show manual price mode
    await waitFor(() => {
      expect(screen.getByText('Manual Price Entry')).toBeInTheDocument();
    });
  });

  it('opens break-even modal when results exist', async () => {
    const user = userEvent.setup();
    render(<EstimatorPage />);
    
    // First get results
    const brandInput = screen.getByLabelText(/car brand/i);
    await user.type(brandInput, 'bmw');
    await waitFor(() => screen.getByText('bmw'));
    await user.click(screen.getByText('bmw'));
    
    const locationInput = screen.getByLabelText(/zip code/i);
    await user.type(locationInput, '10139-torino');
    
    const simulateButton = screen.getByRole('button', { name: /simulate car costs/i });
    await user.click(simulateButton);
    
    await waitFor(() => {
      expect(screen.getByText('Cost Analysis Results')).toBeInTheDocument();
    });
    
    // Click compare to renting
    const compareButton = screen.getByRole('button', { name: /compare to renting/i });
    await user.click(compareButton);
    
    // Modal should open
    expect(screen.getByText('Break-Even Analysis: Buying vs Renting')).toBeInTheDocument();
  });

  it('handles validation errors correctly', async () => {
    server.use(errorHandlers.estimate422);
    
    const user = userEvent.setup();
    render(<EstimatorPage />);
    
    // Submit form without required fields
    const simulateButton = screen.getByRole('button', { name: /simulate car costs/i });
    await user.click(simulateButton);
    
    // Should show validation errors
    await waitFor(() => {
      expect(screen.getByText('Please select a brand')).toBeInTheDocument();
    });
  });
});