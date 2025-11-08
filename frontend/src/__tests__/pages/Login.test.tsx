import React from 'react';
import { screen } from '@testing-library/react';

import { renderWithProviders } from '../../test/test-utils';
import Login from '../../pages/Auth/Login';

describe('Login Page', () => {
  it('renders the login form fields', () => {
    renderWithProviders(<Login />, { route: '/login' });

    expect(
      screen.getByRole('heading', { name: /sign in to your account/i })
    ).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/username or email/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });
});
