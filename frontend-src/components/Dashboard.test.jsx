import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import Dashboard from './Dashboard';

vi.mock('../api.js', () => ({
  api: {
    getBoxes: vi.fn().mockResolvedValue([
      { id: 1, barcode: 'BOX001', name: 'Shelf A', location: null, tube_count: 2 },
    ]),
    getTubes: vi.fn().mockResolvedValue([
      { id: 1, barcode: 'T001', box_id: 1, box_barcode: null, site_name: null, sample_type: null, depth_cm: null, sample_date: null, latitude: null, longitude: null },
      { id: 2, barcode: 'T002', box_id: null, box_barcode: null, site_name: null, sample_type: null, depth_cm: null, sample_date: null, latitude: null, longitude: null },
    ]),
  },
}));

vi.mock('./LeafletMap.jsx', () => ({ default: () => null }));

function renderDashboard() {
  return render(<MemoryRouter><Dashboard /></MemoryRouter>);
}

describe('Dashboard', () => {
  it('renders all three stat card labels', async () => {
    renderDashboard();
    await waitFor(() => {
      expect(screen.getByText('Boxes')).toBeInTheDocument();
      expect(screen.getByText('Unassigned tubes')).toBeInTheDocument();
    });
  });

  it('boxes stat card links to /boxes', async () => {
    renderDashboard();
    await waitFor(() => {
      const link = screen.getByText('Boxes').closest('a');
      expect(link).toHaveAttribute('href', '/boxes');
    });
  });

  it('tubes stat card links to /tubes', async () => {
    renderDashboard();
    await waitFor(() => {
      // target the stat-label specifically
      const label = screen.getAllByText('Tubes').find(el => el.classList.contains('stat-label'));
      const link = label.closest('a');
      expect(link).toHaveAttribute('href', '/tubes');
    });
  });

  it('unassigned stat card links to /tubes?unassigned=true', async () => {
    renderDashboard();
    await waitFor(() => {
      const link = screen.getByText('Unassigned tubes').closest('a');
      expect(link).toHaveAttribute('href', '/tubes?unassigned=true');
    });
  });

  it('shows correct unassigned count', async () => {
    renderDashboard();
    await waitFor(() => {
      const card = screen.getByText('Unassigned tubes').closest('a');
      expect(card).toHaveTextContent('1');
    });
  });

  it('renders recent boxes section', async () => {
    renderDashboard();
    await waitFor(() => {
      expect(screen.getByText('Recent boxes')).toBeInTheDocument();
    });
  });
});
