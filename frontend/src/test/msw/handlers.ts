import { rest } from 'msw';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const handlers = [
  rest.get(`${API_BASE_URL}/api/v1/auth/me`, (_req, res, ctx) =>
    res(
      ctx.status(200),
      ctx.json({
        id: '00000000-0000-0000-0000-000000000001',
        email: 'jane.doe@example.com',
        username: 'janedoe',
        full_name: 'Jane Doe',
        is_active: true,
        is_verified: true,
        is_superuser: false,
        dashboard_preferences: {
          widgets: ['metrics', 'performance_chart'],
          default_timeframe: '1M',
        },
        trading_preferences: {
          default_currency: 'USD',
          default_exchange: 'US',
        },
      })
    )
  ),

  rest.get(`${API_BASE_URL}/api/v1/market-data/categories`, (_req, res, ctx) =>
    res(
      ctx.status(200),
      ctx.json({
        categories: [
          { id: 'stocks', name: 'Stocks', description: 'Individual company stocks' },
          { id: 'etfs', name: 'ETFs', description: 'Exchange Traded Funds' },
        ],
      })
    )
  ),
];
