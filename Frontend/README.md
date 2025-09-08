# Car Price Estimator

A comprehensive React + TypeScript web application for estimating car ownership costs, comparing buying vs renting options, and performing break-even analysis. Built with modern technologies including Ant Design, React Query, Recharts, and comprehensive testing with MSW.

## 🚀 Features

### Core Functionality
- **Smart Brand/Model Selection**: Debounced autocomplete with fallback to manual entry
- **Comprehensive Cost Analysis**: Including depreciation, maintenance, loan calculations
- **Interactive Charts**: Car value over time with purchase year highlighting
- **Break-Even Analysis**: Compare total cost of ownership vs renting with visual charts
- **Study Management**: Save, load, export, and import analysis studies
- **Offline Resilience**: Automatic fallback to manual entry when APIs are unavailable

### Technical Excellence
- **TypeScript**: Fully typed with comprehensive interfaces
- **Responsive Design**: Mobile-first approach with Ant Design components
- **Accessibility**: ARIA labels, keyboard navigation, proper contrast ratios
- **Error Handling**: User-friendly error messages with 503/422 error mapping
- **Caching**: React Query with configurable TTL for optimal performance
- **Testing**: Comprehensive unit and integration tests with MSW mocking

## 📋 Prerequisites

- Node.js 18+ and npm
- A running FastAPI backend server (see API endpoints below)

## 🛠️ Installation & Setup

1. **Clone and install dependencies**:
```bash
git clone <repository-url>
cd car-price-estimator
npm install
```

2. **Configure environment variables**:
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Cache Configuration (minutes)
VITE_CACHE_TTL_BRANDS=10
VITE_CACHE_TTL_MODELS=5
```

3. **Start development server**:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## 🧪 Testing

### Run all tests
```bash
npm test
```

### Run tests with UI (recommended for development)
```bash
npm run test:ui
```

### Run with coverage
```bash
npm run test:coverage
```

### Test Structure
- **Unit Tests**: Individual component testing with MSW mocking
- **Integration Tests**: Full user flows with realistic API interactions
- **MSW Handlers**: Comprehensive mock API responses for success and error cases

## 🏗️ Build & Deployment

### Development build
```bash
npm run build
npm run preview
```

### Production deployment
The application can be deployed to any static hosting service (Netlify, Vercel, etc.):

```bash
npm run build
# Upload dist/ folder to your hosting service
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend API base URL |
| `VITE_CACHE_TTL_BRANDS` | `10` | Brand cache TTL in minutes |
| `VITE_CACHE_TTL_MODELS` | `5` | Model cache TTL in minutes |

### API Endpoints

The application expects the following FastAPI backend endpoints:

#### GET /api/brands
Returns available car brands
```json
{ "brands": ["bmw", "audi", "fiat", "toyota"] }
```

#### GET /api/models?brand={brand}
Returns models for a specific brand
```json
{ "brand": "bmw", "models": ["320i", "x3", "i3"] }
```

#### POST /api/estimate
Calculates car ownership costs
```json
{
  "purchase_price": 30000.0,
  "estimated_final_value": 12000.0,
  "monthly_depreciation": 200.0,
  "monthly_maintenance": 120.0,
  "loan_monthly_payment": 95.0,
  "loan_total_interest": 700.0,
  "total_monthly_cost": 415.0,
  "year_values": [30000, 28000, 25000, ...]
}
```

#### POST /api/break_even
Compares buying vs renting costs
```json
{
  "months_to_break_even": 36,
  "buy_monthly_series": [420, 420, ...],
  "rent_monthly_series": [400, 400, ...],
  "message": null
}
```

## 📁 Project Structure

```
src/
├── api/              # API client and endpoints
│   ├── client.ts     # Axios configuration with interceptors
│   └── endpoints.ts  # Typed API wrappers
├── components/       # Reusable UI components
│   ├── BrandModelForm/
│   ├── LoanSection/
│   ├── ResultsCard/
│   ├── Charts/
│   ├── BreakEvenModal/
│   └── SavedStudies/
├── hooks/           # React Query hooks
│   ├── useBrands.ts
│   ├── useModels.ts
│   ├── useEstimate.ts
│   └── useBreakEven.ts
├── pages/           # Main application pages
│   └── EstimatorPage.tsx
├── test/            # Testing utilities and mocks
│   ├── msw/         # Mock Service Worker handlers
│   ├── setup.ts     # Test configuration
│   └── test-utils.tsx
├── types/           # TypeScript type definitions
│   └── api.ts
└── utils/           # Utility functions
    ├── numbers.ts   # Currency/number formatting
    ├── date.ts      # Date utilities
    └── storage.ts   # LocalStorage management
```

## 🎯 Key Features Deep Dive

### Smart Form Handling
- **Debounced Search**: Brand autocomplete with 300ms debounce
- **Progressive Loading**: Models load automatically after brand selection
- **Validation**: Client-side validation with server error mapping
- **Fallback Mode**: Manual entry when APIs are unavailable

### Error Resilience
- **503 Handling**: Friendly messages with manual price entry option
- **422 Validation**: Maps backend field errors to form fields
- **Network Retry**: Automatic retry with exponential backoff
- **Offline Support**: Graceful degradation to manual entry

### Data Management
- **Smart Caching**: React Query with configurable TTL
- **Local Storage**: Save and restore analysis studies
- **Export/Import**: JSON-based study backup and sharing
- **Real-time Updates**: Automatic re-validation and fresh data

### Accessibility
- **ARIA Labels**: Comprehensive screen reader support
- **Keyboard Navigation**: Full keyboard accessibility
- **Focus Management**: Proper focus trap in modals
- **Color Contrast**: WCAG AA compliant color schemes

## 🤝 Development

### Code Standards
- **TypeScript**: Strict mode with comprehensive typing
- **ESLint**: Enforced code quality and consistency
- **Prettier**: Automated code formatting
- **Testing**: Minimum 80% code coverage requirement

### Component Architecture
- **Single Responsibility**: Each component has one clear purpose
- **Composition**: Reusable components with clear props interfaces
- **State Management**: Local state + React Query for server state
- **Error Boundaries**: Graceful error handling throughout the app

### Performance Optimizations
- **Code Splitting**: Lazy-loaded components where appropriate
- **Memoization**: React.memo for expensive components
- **Caching**: Aggressive caching with smart invalidation
- **Bundle Size**: Optimized imports and tree-shaking

## 📊 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Verify `VITE_API_BASE_URL` in `.env`
   - Ensure backend server is running
   - Check CORS configuration on backend

2. **Charts Not Rendering**
   - Clear browser cache
   - Verify Recharts version compatibility
   - Check console for JavaScript errors

3. **Tests Failing**
   - Run `npm install` to ensure all dependencies
   - Verify MSW handlers match actual API responses
   - Check test environment configuration

## 📝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes with tests
4. Run the test suite: `npm test`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.