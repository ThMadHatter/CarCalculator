import { useMutation } from '@tanstack/react-query';
import { estimate } from '../api/endpoints';
import { EstimateRequest } from '../types/api';

export const useEstimate = () => {
  return useMutation({
    mutationFn: (payload: EstimateRequest) => estimate(payload),
  });
};