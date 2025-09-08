import { useQuery } from '@tanstack/react-query';
import { getModels } from '../api/endpoints';

const CACHE_TTL = parseInt(import.meta.env.VITE_CACHE_TTL_MODELS || '5') * 60 * 1000; // minutes to ms

export const useModels = (brand: string) => {
  return useQuery({
    queryKey: ['models', brand],
    queryFn: () => getModels(brand),
    enabled: !!brand,
    staleTime: CACHE_TTL,
    cacheTime: CACHE_TTL,
    retry: false, // We handle retries in the API client
  });
};