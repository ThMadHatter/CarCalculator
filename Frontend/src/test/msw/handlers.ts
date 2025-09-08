import { http, HttpResponse } from 'msw';

const baseUrl = 'http://localhost:8000';

export const handlers = [
  // GET /api/brands - Success
  http.get(`${baseUrl}/api/brands`, () => {
    return HttpResponse.json({
      brands: ['bmw', 'audi', 'fiat', 'toyota', 'mercedes', 'volkswagen']
    });
  }),

  // GET /api/models - Success
  http.get(`${baseUrl}/api/models`, ({ request }) => {
    const url = new URL(request.url);
    const brand = url.searchParams.get('brand');
    
    if (!brand) {
      return HttpResponse.json(
        { error: 'Brand parameter is required' },
        { status: 400 }
      );
    }

    const modelsMap: Record<string, string[]> = {
      bmw: ['320i', 'x3', 'i3', 'x5', 'm3'],
      audi: ['a3', 'a4', 'q5', 'tt', 's4'],
      fiat: ['500', 'panda', 'tipo', '500x'],
      toyota: ['corolla', 'rav4', 'prius', 'camry'],
      mercedes: ['c-class', 'e-class', 'gle', 'a-class'],
      volkswagen: ['golf', 'polo', 'tiguan', 'passat']
    };

    return HttpResponse.json({
      brand,
      models: modelsMap[brand.toLowerCase()] || []
    });
  }),

  // POST /api/estimate - Success
  http.post(`${baseUrl}/api/estimate`, async ({ request }) => {
    const body = await request.json();
    
    return HttpResponse.json({
      purchase_price: 30000.0,
      estimated_final_value: 12000.0,
      monthly_depreciation: 200.0,
      monthly_maintenance: (body as any).monthly_maintenance || 120.0,
      loan_monthly_payment: 95.0,
      loan_total_interest: 700.0,
      total_monthly_cost: 415.0,
      year_values: [30000, 28000, 25000, 22000, 19000, 16000, 15000, 14000, 13000, 12000]
    });
  }),

  // POST /api/break_even - Success
  http.post(`${baseUrl}/api/break_even`, async ({ request }) => {
    const body = await request.json();
    const { years = 5 } = body as any;
    const months = years * 12;
    
    return HttpResponse.json({
      months_to_break_even: 36,
      buy_monthly_series: Array(months).fill(420),
      rent_monthly_series: Array(months).fill(400),
      message: null
    });
  })
];

// Error handlers for testing
export const errorHandlers = {
  brands503: http.get(`${baseUrl}/api/brands`, () => {
    return HttpResponse.json(
      { error: 'Service temporarily unavailable' },
      { status: 503 }
    );
  }),

  models503: http.get(`${baseUrl}/api/models`, () => {
    return HttpResponse.json(
      { error: 'Service temporarily unavailable' },
      { status: 503 }
    );
  }),

  estimate422: http.post(`${baseUrl}/api/estimate`, () => {
    return HttpResponse.json(
      {
        error: 'Validation failed',
        details: {
          brand: ['Brand is required'],
          registration_year: ['Year must be between 2000 and 2030']
        }
      },
      { status: 422 }
    );
  }),

  estimate503: http.post(`${baseUrl}/api/estimate`, () => {
    return HttpResponse.json(
      { error: 'Service temporarily unavailable' },
      { status: 503 }
    );
  }),

  breakEven500: http.post(`${baseUrl}/api/break_even`, () => {
    return HttpResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  })
};