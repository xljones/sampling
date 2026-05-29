import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import TubeList from './TubeList';

vi.mock('../api.js', () => ({
  api: {
    getBoxes: vi.fn().mockResolvedValue([]),
    getTubes: vi.fn().mockResolvedValue([
      { id: 1, barcode: 'T001', box_id: 1, box_barcode: 'BOX001', site_name: 'Site A', sample_type: 'core', depth_cm: 10, sample_date: '2024-01-01' },
      { id: 2, barcode: 'T002', box_id: null, box_barcode: null, site_name: 'Site B', sample_type: null, depth_cm: null, sample_date: null },
    ]),
  },
}));

vi.mock('../AuthContext.jsx', () => ({ useAuth: () => ({ user: { is_readonly: false } }) }));
vi.mock('./Toast.jsx', () => ({ useToast: () => vi.fn() }));

function renderAt(path) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes><Route path="/tubes" element={<TubeList />} /></Routes>
    </MemoryRouter>
  );
}

describe('TubeList', () => {
  it('shows all tubes by default', async () => {
    renderAt('/tubes');
    await waitFor(() => {
      expect(screen.getByText('T001')).toBeInTheDocument();
      expect(screen.getByText('T002')).toBeInTheDocument();
    });
  });

  it('shows "Tubes" heading by default', async () => {
    renderAt('/tubes');
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Tubes' })).toBeInTheDocument();
    });
  });

  it('filters to unassigned tubes when ?unassigned=true', async () => {
    renderAt('/tubes?unassigned=true');
    await waitFor(() => {
      expect(screen.queryByText('T001')).not.toBeInTheDocument();
      expect(screen.getByText('T002')).toBeInTheDocument();
    });
  });

  it('shows "Unassigned tubes" heading when filtered', async () => {
    renderAt('/tubes?unassigned=true');
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Unassigned tubes' })).toBeInTheDocument();
    });
  });

  it('shows "Unassigned only ✕" chip when filtered', async () => {
    renderAt('/tubes?unassigned=true');
    await waitFor(() => {
      expect(screen.getByText(/Unassigned only/)).toBeInTheDocument();
    });
  });

  it('filters by text search', async () => {
    renderAt('/tubes');
    await waitFor(() => screen.getByText('T001'));
    fireEvent.change(screen.getByPlaceholderText(/filter/i), { target: { value: 'Site A' } });
    expect(screen.getByText('T001')).toBeInTheDocument();
    expect(screen.queryByText('T002')).not.toBeInTheDocument();
  });
});
