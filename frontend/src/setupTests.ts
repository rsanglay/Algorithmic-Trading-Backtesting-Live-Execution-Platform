import '@testing-library/jest-dom';
import 'whatwg-fetch';

import { server } from './test/msw/server';

// Establish API mocking before all tests.
beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }));

// Reset any request handlers that we may add during the tests,
// so they don't affect other tests.
afterEach(() => server.resetHandlers());

// Clean up once the tests are done.
afterAll(() => server.close());
