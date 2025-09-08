import { useQuery } from '@tanstack/react-query';
import { getBrands } from '../api/endpoints';

const CACHE_TTL = parseInt(import.meta.env.VITE_CACHE_TTL_BRANDS || '10') * 60 * 1000; // minutes to ms

export const useBrands = () => {
  return useQuery({
    queryKey: ['brands'],
    queryFn: getBrands,
    staleTime: CACHE_TTL,
    cacheTime: CACHE_TTL,
    retry: false, // We handle retries in the API client
  });
};