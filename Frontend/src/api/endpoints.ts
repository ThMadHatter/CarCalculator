import { AxiosResponse } from 'axios';
import apiClient from './client';
import { 
  BrandsResponse, 
  ModelsResponse, 
  EstimateRequest, 
  EstimateResponse,
  BreakEvenRequest,
  BreakEvenResponse
} from '../types/api';

// Retry configuration
const retryConfig = {
  retries: 2,
  retryDelay: (retryCount: number) => Math.pow(2, retryCount) * 1000, // exponential backoff
};

export const getBrands = async (): Promise<BrandsResponse> => {
  let lastError;
  
  for (let i = 0; i <= retryConfig.retries; i++) {
    try {
      const response: AxiosResponse<BrandsResponse> = await apiClient.get('/api/brands');
      return response.data;
    } catch (error) {
      lastError = error;
      if (i < retryConfig.retries) {
        await new Promise(resolve => setTimeout(resolve, retryConfig.retryDelay(i)));
      }
    }
  }
  
  throw lastError;
};

export const getModels = async (brand: string): Promise<ModelsResponse> => {
  if (!brand) {
    throw new Error('Brand parameter is required');
  }

  let lastError;
  
  for (let i = 0; i <= retryConfig.retries; i++) {
    try {
      const response: AxiosResponse<ModelsResponse> = await apiClient.get('/api/models', {
        params: { brand }
      });
      return response.data;
    } catch (error) {
      lastError = error;
      if (i < retryConfig.retries) {
        await new Promise(resolve => setTimeout(resolve, retryConfig.retryDelay(i)));
      }
    }
  }
  
  throw lastError;
};

export const estimate = async (payload: EstimateRequest): Promise<EstimateResponse> => {
  const response: AxiosResponse<EstimateResponse> = await apiClient.post('/api/estimate', payload);
  return response.data;
};

export const breakEven = async (payload: BreakEvenRequest): Promise<BreakEvenResponse> => {
  const response: AxiosResponse<BreakEvenResponse> = await apiClient.post('/api/break_even', payload);
  return response.data;
};