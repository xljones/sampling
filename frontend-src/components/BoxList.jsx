import { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../api.js';
import { useAuth } from '../AuthContext.jsx';
import { useToast } from './Toast.jsx';
import RelativeTime from './RelativeTime.jsx';
import BarcodeInput from './BarcodeInput.jsx';

export default function BoxList() {
  const { user } = useAuth();
  const ro = user?.is_readonly;
  const [boxes, setBoxes] = useState([]);
  const [locations, setLocations] = useState([]);
  const [filter, setFilter] = useState('');
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ barcode: '', name: '', location_id: '', notes: '' });
  const [saving, setSaving] = useState(false);
  const toast = useToast();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    api.getBoxes().then(setBoxes);
    api.getLocations().then(setLocations);
    const barcode = searchParams.get('barcode');
    if (searchParams.get('add') === '1') {
      setShowAdd(true);
      if (barcode) setForm(f => ({ ...f, barcode }));
    }
  }, [searchParams]);

  const q = filter.toLowerCase();
  const visible = q
    ? boxes.filter(b =>
        b.barcode.toLowerCase().includes(q) ||
        (b.name ?? '').toLowerCase().includes(q) ||
        (b.location_name ?? '').toLowerCase().includes(q) ||
        (b.notes ?? '').toLowerCase().includes(q)
      )
    : boxes;

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  async function handleAdd(e) {
    e.preventDefault();
    setSaving(true);
    try {
      const box = await api.createBox(form);
      toast('Box created');
      navigate(`/boxes/${box.id}`);
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id) {
    if (!confirm('Delete this box? Tubes inside will become unassigned.')) return;
    await api.deleteBox(id);
    setBoxes(b => b.filter(x => x.id !== id));
    toast('Box deleted');
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Boxes</h1>
        <div className="btn-group">
          <a href="/api/export/boxes" className="btn btn-secondary" download>Export CSV</a>
          {!ro && <button className="btn btn-primary" onClick={() => setShowAdd(v => !v)}>+ New box</button>}
        </div>
      </div>

      {showAdd && !ro && (
        <div className="card card-body mb-6">
          <form onSubmit={handleAdd}>
            <div className="form-grid mb-3">
              <div className="field">
                <label>Barcode *</label>
                <BarcodeInput
                  value={form.barcode}
                  onChange={v => set('barcode', v)}
                  placeholder="Scan or type box barcode"
                  autoFocus
                />
              </div>
              <div className="field">
                <label>Name</label>
                <input value={form.name} onChange={e => set('name', e.target.value)} placeholder="e.g. Core A Box 1" />
              </div>
              <div className="field">
                <label>Location</label>
                <select value={form.location_id} onChange={e => set('location_id', e.target.value)}>
                  <option value="">— No location —</option>
                  {locations.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}
                </select>
              </div>
              <div className="field">
                <label>Notes</label>
                <input value={form.notes} onChange={e => set('notes', e.target.value)} />
              </div>
            </div>
            <div className="form-actions">
              <button className="btn btn-success" disabled={saving || !form.barcode}>Save box</button>
              <button type="button" className="btn btn-secondary" onClick={() => setShowAdd(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      <div className="mb-4">
        <input
          type="search"
          value={filter}
          onChange={e => setFilter(e.target.value)}
          placeholder="Filter by barcode, name, location…"
          className="search-input"
        />
      </div>

      <div className="card">
        <div className="table-wrap">
          <table>
            <thead><tr><th>Barcode</th><th>Name</th><th>Location</th><th>Tubes</th><th className="col-mobile-hide">Updated (UTC)</th><th></th></tr></thead>
            <tbody>
              {visible.map(b => (
                <tr
                  key={b.id}
                  className="row-clickable"
                  onClick={e => { if (!e.target.closest('a, button, input')) navigate(`/boxes/${b.id}`); }}
                >
                  <td><Link to={`/boxes/${b.id}`}><span className="barcode">{b.barcode}</span></Link></td>
                  <td>{b.name || '—'}</td>
                  <td>{b.location_name || '—'}</td>
                  <td>{b.tube_count}</td>
                  <td className="col-mobile-hide text-muted"><RelativeTime value={b.updated_at} /></td>
                  <td className="col-shrink">
                    <div className="row-actions">
                      {!ro && <Link to={`/boxes/${b.id}?edit=1`} className="btn btn-secondary btn-sm">Edit</Link>}
                      {!ro && <button className="btn btn-danger btn-sm" onClick={() => handleDelete(b.id)}>Delete</button>}
                    </div>
                  </td>
                </tr>
              ))}
              {visible.length === 0 && <tr><td colSpan={6} className="empty">{filter ? 'No matches' : 'No boxes yet — create one above'}</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
