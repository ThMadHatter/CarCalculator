import { useMutation } from '@tanstack/react-query';
import { breakEvenAnalysis } from '../api/endpoints';
import { BreakEvenAnalysisRequest, BreakEvenAnalysisResponse, ApiError } from '../types/api';

export const useBreakEvenAnalysis = () => {
  return useMutation<BreakEvenAnalysisResponse, ApiError, BreakEvenAnalysisRequest>({
    mutationFn: breakEvenAnalysis,
  });
};
