import { useMutation } from '@tanstack/react-query';
import { breakEven } from '../api/endpoints';
import { BreakEvenRequest } from '../types/api';

export const useBreakEven = () => {
  return useMutation({
    mutationFn: (payload: BreakEvenRequest) => breakEven(payload),
  });
};