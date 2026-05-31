import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api.js';
import { useAuth } from '../AuthContext.jsx';
import { useToast } from './Toast.jsx';
import BarcodeInput from './BarcodeInput.jsx';
import ExportDropdown from './ExportDropdown.jsx';


export default function CoreList() {
  const { user } = useAuth();
  const ro = user?.is_readonly;
  const navigate = useNavigate();
  const toast = useToast();
  const [cores, setCores] = useState(null);
  const [filter, setFilter] = useState('');
  const [adding, setAdding] = useState(false);
  const [newBarcode, setNewBarcode] = useState('');
  const [creating, setCreating] = useState(false);
  const [withSubData, setWithSubData] = useState(true);

  useEffect(() => { api.getCores().then(setCores); }, []);

  const q = filter.toLowerCase();
  const anyFilter = !!q;

  function _coreExportUrl(withSubData, format, filtered) {
    const p = new URLSearchParams();
    if (!withSubData) p.set('flat', '1');
    if (format && format !== 'csv') p.set('format', format);
    if (filtered) p.set('ids', filtered.map(c => c.id).join(','));
    const qs = p.toString();
    return qs ? `/api/export/cores?${qs}` : '/api/export/cores';
  }

  const visible = cores
    ? cores.filter(c => !q || (
        c.barcode.toLowerCase().includes(q) ||
        (c.name ?? '').toLowerCase().includes(q) ||
        (c.site_name ?? '').toLowerCase().includes(q) ||
        (c.location_name ?? '').toLowerCase().includes(q) ||
        (c.sample_type ?? '').toLowerCase().includes(q)
      ))
    : [];

  async function handleCreate(e) {
    e.preventDefault();
    if (!newBarcode.trim()) return;
    setCreating(true);
    try {
      const core = await api.createCore({ barcode: newBarcode.trim() });
      toast(`Core ${core.barcode} created`);
      navigate(`/cores/${core.id}`);
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setCreating(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Cores</h1>
        <div className="btn-group">
          <ExportDropdown
            label={anyFilter ? `Export (${visible.length} rows)` : 'Export'}
            disabled={visible.length === 0}
            options={[
              { type: 'checkbox', label: 'Include boxes & tubes', checked: withSubData, onChange: () => setWithSubData(v => !v) },
              { divider: true },
              { label: 'Comma separated values (.csv)', onClick: () => { window.location.href = _coreExportUrl(withSubData, 'csv', anyFilter ? visible : null); } },
              { label: 'Tab separated values (.tsv)', onClick: () => { window.location.href = _coreExportUrl(withSubData, 'tsv', anyFilter ? visible : null); } },
              { label: 'JSON (.json)', onClick: () => { window.location.href = _coreExportUrl(withSubData, 'json', anyFilter ? visible : null); } },
              { label: 'GeoJSON (.geojson)', note: 'Core locations only — sub-data not included', onClick: () => { window.location.href = _coreExportUrl(false, 'geojson', anyFilter ? visible : null); } },
              { label: 'Excel (.xlsx)', note: 'Cores, boxes & tubes', onClick: () => { window.location.href = _coreExportUrl(false, 'xlsx', anyFilter ? visible : null); } },
            ]}
          />
          {!ro && (
            <button className="btn btn-primary" onClick={() => setAdding(v => !v)}>
              {adding ? 'Cancel' : '+ New core'}
            </button>
          )}
        </div>
      </div>

      {adding && (
        <div className="card card-body mw-md mb-4">
          <form onSubmit={handleCreate}>
            <label className="mb-2 fw-600">New core barcode</label>
            <BarcodeInput
              value={newBarcode}
              onChange={setNewBarcode}
              placeholder="Scan or type barcode"
              autoFocus
            />
            <div className="btn-group mt-3">
              <button className="btn btn-success" disabled={creating || !newBarcode.trim()}>
                {creating ? 'Creating…' : 'Create core'}
              </button>
              <button type="button" className="btn btn-secondary" onClick={() => setAdding(false)}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="mb-4">
        <input
          type="search"
          value={filter}
          onChange={e => setFilter(e.target.value)}
          placeholder="Filter by barcode, name, site, location, type…"
          className="search-input"
        />
      </div>

      <div className="card">
        {cores === null && <p className="card-message">Loading…</p>}
        {cores?.length === 0 && <p className="card-message">No cores yet.</p>}
        {cores?.length > 0 && (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Barcode</th>
                  <th>Name</th>
                  <th>Source site</th>
                  <th>Collected</th>
                  <th>Type</th>
                  <th>Storage</th>
                  <th>Tubes</th>
                  <th>Boxes</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {visible.map(c => (
                  <tr key={c.id} className="row-clickable" onClick={() => navigate(`/cores/${c.id}`)}>
                    <td>
                      <Link to={`/cores/${c.id}`} onClick={e => e.stopPropagation()}>
                        <span className="barcode">{c.barcode}</span>
                      </Link>
                    </td>
                    <td>{c.name || '—'}</td>
                    <td>{c.site_name || '—'}</td>
                    <td>{c.collection_date || '—'}</td>
                    <td>{c.sample_type || '—'}</td>
                    <td>{c.location_name || '—'}</td>
                    <td>{c.tube_count}</td>
                    <td>{c.box_count || '—'}</td>
                    <td>
                      <div className="row-actions">
                        {!ro && <Link to={`/cores/${c.id}?edit=1`} className="btn btn-secondary btn-sm">Edit</Link>}
                      </div>
                    </td>
                  </tr>
                ))}
                {visible.length === 0 && q && (
                  <tr><td colSpan={9} className="empty">No matches</td></tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
