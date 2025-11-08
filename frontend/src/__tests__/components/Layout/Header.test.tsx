import React from 'react';
import { screen, waitFor } from '@testing-library/react';

import Header from '../../../components/Layout/Header';
import { renderWithProviders } from '../../../test/test-utils';

describe('Header Component', () => {
  beforeEach(() => {
    localStorage.setItem('token', 'test-token');
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('displays the authenticated user name and email', async () => {
    renderWithProviders(<Header onMenuClick={() => undefined} />);

    await waitFor(() => expect(screen.getByText(/jane doe/i)).toBeInTheDocument());
    expect(screen.getByText(/jane.doe@example.com/i)).toBeInTheDocument();
  });
});
