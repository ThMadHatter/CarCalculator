export interface Brand {
  name: string;
}

export interface BrandsResponse {
  brands: string[];
}

export interface ModelsResponse {
  brand: string;
  models: string[];
}

export interface EstimateRequest {
  brand: string;
  model: string;
  details: string;
  zip_code: string;
  registration_year: number;
  number_of_years: number;
  purchase_year_index: number;
  monthly_maintenance: number;
  loan_value: number;
  bank_rate_percent: number;
  loan_years: number;
  shift_types: string[];
}

export interface EstimateResponse {
  purchase_price: number;
  estimated_final_value: number;
  monthly_depreciation: number;
  monthly_maintenance: number;
  loan_monthly_payment: number;
  loan_total_interest: number;
  total_monthly_cost: number;
  year_values: number[];
  warning?: string;
  price_stddev?: number[];
  adjusted_number_of_years?: number;
}

export interface BreakEvenRequest {
  estimate: EstimateRequest;
  rent_monthly_cost: number;
  years: number;
}

export interface BreakEvenResponse {
  months_to_break_even: number | null;
  buy_monthly_series: number[];
  rent_monthly_series: number[];
  message: string | null;
}

export interface ApiError {
  error: string;
  details?: Record<string, string[]>;
}

export interface SavedStudy {
  id: string;
  name: string;
  data: EstimateRequest;
  createdAt: string;
}
