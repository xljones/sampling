import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import TubeForm from './TubeForm';
import { FormMode } from '../constants.js';

vi.mock('../api.js', () => ({
  api: {
    getBoxes: vi.fn().mockResolvedValue([
      { id: 1, barcode: 'BOX001', name: 'Shelf A' },
      { id: 2, barcode: 'BOX002', name: null },
    ]),
    getCores: vi.fn().mockResolvedValue([]),
    getTube: vi.fn(),
    createTube: vi.fn().mockResolvedValue({ id: 99, barcode: 'TUBE001' }),
    updateTube: vi.fn().mockResolvedValue({ id: 99, barcode: 'TUBE001' }),
    createBox: vi.fn().mockResolvedValue({ id: 3, barcode: 'NEW-BOX', name: null }),
  },
}));

vi.mock('./Toast.jsx', () => ({ useToast: () => vi.fn() }));
vi.mock('./MapPicker.jsx', () => ({ default: () => <div data-testid="map-picker" /> }));
vi.mock('./BarcodeInput.jsx', () => ({
  default: ({ value, onChange, placeholder }) => (
    <input
      value={value}
      onChange={e => onChange(e.target.value)}
      placeholder={placeholder}
      data-testid={placeholder?.includes('box') ? 'box-barcode-input' : 'tube-barcode-input'}
    />
  ),
}));

function renderNew(path = '/tubes/new') {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/tubes/new" element={<TubeForm mode={FormMode.CREATE} />} />
        <Route path="/tubes/:id/edit" element={<TubeForm mode={FormMode.EDIT} />} />
      </Routes>
    </MemoryRouter>
  );
}

describe('TubeForm — box scan mode', () => {
  it('defaults to scan mode — shows barcode input, not dropdown', async () => {
    renderNew();
    await waitFor(() => {
      expect(screen.getByTestId('box-barcode-input')).toBeInTheDocument();
      expect(screen.queryByRole('combobox')).not.toBeInTheDocument();
    });
  });

  it('switches to dropdown when "Choose from list" is clicked', async () => {
    renderNew();
    await waitFor(() => screen.getByTestId('box-barcode-input'));
    fireEvent.click(screen.getAllByText('Choose from list')[0]);
    expect(screen.getByRole('combobox')).toBeInTheDocument();
    expect(screen.queryByTestId('box-barcode-input')).not.toBeInTheDocument();
  });

  it('shows match confirmation for known box barcode', async () => {
    renderNew();
    await waitFor(() => screen.getByTestId('box-barcode-input'));
    fireEvent.change(screen.getByTestId('box-barcode-input'), { target: { value: 'BOX001' } });
    await waitFor(() => {
      expect(screen.getByText(/✓.*BOX001/)).toBeInTheDocument();
    });
  });

  it('shows create button for unknown barcode', async () => {
    renderNew();
    await waitFor(() => screen.getByTestId('box-barcode-input'));
    fireEvent.change(screen.getByTestId('box-barcode-input'), { target: { value: 'UNKNOWN' } });
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /create "UNKNOWN"/i })).toBeInTheDocument();
    });
  });

  it('prefills box barcode when box_id query param is provided', async () => {
    renderNew('/tubes/new?box_id=1');
    await waitFor(() => {
      expect(screen.getByTestId('box-barcode-input')).toHaveValue('BOX001');
    });
  });
});

describe('TubeForm — map picker', () => {
  it('map picker is always visible', async () => {
    renderNew();
    await waitFor(() => expect(screen.getByTestId('map-picker')).toBeInTheDocument());
  });
});
