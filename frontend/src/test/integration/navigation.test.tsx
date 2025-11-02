/**
 * Integration tests for Phase 2 navigation.
 * 
 * Tests core user flows against real backend API:
 * - Project selection → Overview
 * - Overview → Tracing
 * - Tracing → Trace Detail
 * - Sidebar navigation
 * 
 * Following ADR-007: Simplified testing approach for MVP
 * Using real APIs, not mocks.
 */

import { describe, it, expect, beforeAll } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { App } from '../../app';
import { theme } from '../../theme';
import { storeApiKey } from '../../features/auth/utils/auth-storage';

// Test wrapper with all providers
function TestWrapper({ children }: { children: React.ReactNode }) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false, // Don't retry in tests
        staleTime: 0,
      },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

describe('Phase 2 Navigation Integration Tests', () => {
  beforeAll(() => {
    // Set up auth
    storeApiKey('dev-api-key-change-in-production');
  });

  it('should navigate from projects list to project overview', async () => {
    const user = userEvent.setup();
    
    render(<App />, { wrapper: TestWrapper });

    // Wait for projects list to load
    await waitFor(() => {
      expect(screen.getByText('Projects')).toBeInTheDocument();
    });

    // Should show project cards
    const projectCards = await screen.findAllByText(/Open Project/i);
    expect(projectCards.length).toBeGreaterThan(0);

    // Click first project
    await user.click(projectCards[0]);

    // Should navigate to project overview
    await waitFor(() => {
      expect(screen.getByText('Quick Actions')).toBeInTheDocument();
    });
  });

  it('should show sidebar navigation in project workspace', async () => {
    const user = userEvent.setup();
    
    render(<App />, { wrapper: TestWrapper });

    // Navigate to a project
    await waitFor(() => screen.findAllByText(/Open Project/i));
    const openButtons = await screen.findAllByText(/Open Project/i);
    await user.click(openButtons[0]);

    // Wait for sidebar to appear
    await waitFor(() => {
      // Sidebar menu items
      expect(screen.getByText('Overview')).toBeInTheDocument();
      expect(screen.getByText('Tracing')).toBeInTheDocument();
      expect(screen.getByText('Configuration')).toBeInTheDocument();
    });

    // Analytics and Graphs should be disabled
    const analytics = screen.getByText('Analytics');
    const graphs = screen.getByText('Graphs');
    
    // Check if parent ListItemButton is disabled
    expect(analytics.closest('button')).toBeDisabled();
    expect(graphs.closest('button')).toBeDisabled();
  });

  it('should navigate from overview to tracing', async () => {
    const user = userEvent.setup();
    
    render(<App />, { wrapper: TestWrapper });

    // Navigate to project
    await waitFor(() => screen.findAllByText(/Open Project/i));
    const openButtons = await screen.findAllByText(/Open Project/i);
    await user.click(openButtons[0]);

    // Wait for overview to load
    await waitFor(() => {
      expect(screen.getByText('Quick Actions')).toBeInTheDocument();
    });

    // Click "Go to Tracing" button
    const tracingButton = screen.getByText('Go to Tracing');
    await user.click(tracingButton);

    // Should navigate to tracing page
    await waitFor(() => {
      expect(screen.getByText('Traces')).toBeInTheDocument();
    });
  });

  it('should navigate to configuration page', async () => {
    const user = userEvent.setup();
    
    render(<App />, { wrapper: TestWrapper });

    // Navigate to project
    await waitFor(() => screen.findAllByText(/Open Project/i));
    const openButtons = await screen.findAllByText(/Open Project/i);
    await user.click(openButtons[0]);

    // Click Configuration in sidebar
    await waitFor(() => screen.getByText('Configuration'));
    const configLink = screen.getByText('Configuration');
    await user.click(configLink);

    // Should show config page
    await waitFor(() => {
      expect(screen.getByText(/Full configuration UI coming in Phase 4/i)).toBeInTheDocument();
    });
  });

  it('should maintain breadcrumb navigation', async () => {
    const user = userEvent.setup();
    
    render(<App />, { wrapper: TestWrapper });

    // Navigate to project
    await waitFor(() => screen.findAllByText(/Open Project/i));
    const openButtons = await screen.findAllByText(/Open Project/i);
    await user.click(openButtons[0]);

    // Go to tracing
    await waitFor(() => screen.getByText('Tracing'));
    await user.click(screen.getByText('Tracing'));

    // Wait for breadcrumbs
    await waitFor(() => {
      const breadcrumbs = screen.getAllByText(/Projects|Tracing/);
      expect(breadcrumbs.length).toBeGreaterThan(0);
    });

    // Click "Projects" in breadcrumb to go back
    const projectsBreadcrumb = screen.getAllByText('Projects')[0];
    await user.click(projectsBreadcrumb);

    // Should return to projects list
    await waitFor(() => {
      expect(screen.getByText(/New Project/i)).toBeInTheDocument();
    });
  });
});

