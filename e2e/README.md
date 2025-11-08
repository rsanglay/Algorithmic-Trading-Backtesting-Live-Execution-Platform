# End-to-End Testing

This directory contains the Playwright end-to-end test suite for the Algorithmic Trading Platform.

## 📦 Installation

```bash
cd e2e
npm install
npx playwright install
```

## 🚀 Running Tests

```bash
# Run the full suite in headless mode
npm test

# Run a single browser instance in headed mode
npm run test:headed

# Launch the Playwright UI test runner
npm run test:ui

# Generate selectors by recording a session
npm run codegen
```

## 🌐 Test Environment

The Playwright configuration starts the frontend development server automatically:
- Frontend command: `npm run start --prefix ../frontend`
- Base URL: `http://localhost:4000`

To test against a deployed environment, set the `E2E_BASE_URL` environment variable:

```bash
E2E_BASE_URL="https://your-app.vercel.app" npm test
```

## 🧪 Test Structure

- `tests/auth.spec.ts` — smoke tests for authentication screens
- Add new files under `tests/` to expand coverage (e.g., `dashboard.spec.ts`, `market-data.spec.ts`)

## ✅ Best Practices

- Keep tests isolated and idempotent
- Use seeded data or dedicated test accounts
- Prefer data-testids for complex UI selectors
- Capture traces/snapshots for easier debugging (`trace: 'on-first-retry'` is enabled)
