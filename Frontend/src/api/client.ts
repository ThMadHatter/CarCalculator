import axios from 'axios';
import { notification } from 'antd';

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL,
  timeout: 1000000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add any auth headers here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for global error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    const status = error.response?.status;
    const message = error.response?.data?.error || error.message;

    // Map 503 to friendly message
    if (status === 503) {
      notification.warning({
        message: 'Service Temporarily Unavailable',
        description: 'Price data temporarily unavailable — try again later or enter manual price.',
        duration: 5,
      });
    } else if (status === 500) {
      notification.error({
        message: 'Unexpected Error',
        description: 'Unexpected error — try again later.',
        duration: 5,
      });
    } else if (status >= 400 && status < 500 && status !== 422) {
      notification.error({
        message: 'Request Error',
        description: message,
        duration: 5,
      });
    }

    console.error('API Error:', {
      status,
      message,
      url: error.config?.url,
      method: error.config?.method,
    });

    return Promise.reject(error);
  }
);

export default apiClient;