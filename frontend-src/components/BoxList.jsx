import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api.js';
import { useToast } from './Toast.jsx';
import BarcodeInput from './BarcodeInput.jsx';

export default function BoxList() {
  const [boxes, setBoxes] = useState([]);
  const [filter, setFilter] = useState('');
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ barcode: '', name: '', location: '', notes: '' });
  const [saving, setSaving] = useState(false);
  const toast = useToast();
  const navigate = useNavigate();

  useEffect(() => { api.getBoxes().then(setBoxes); }, []);

  const q = filter.toLowerCase();
  const visible = q
    ? boxes.filter(b =>
        b.barcode.toLowerCase().includes(q) ||
        (b.name ?? '').toLowerCase().includes(q) ||
        (b.location ?? '').toLowerCase().includes(q)
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
        <div style={{ display: 'flex', gap: 8 }}>
          <a href="/api/export/boxes" className="btn btn-secondary" download>Export CSV</a>
          <button className="btn btn-primary" onClick={() => setShowAdd(v => !v)}>+ New box</button>
        </div>
      </div>

      {showAdd && (
        <div className="card card-body" style={{ marginBottom: 24 }}>
          <form onSubmit={handleAdd}>
            <div className="form-grid" style={{ marginBottom: 12 }}>
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
                <label>Location / storage</label>
                <input value={form.location} onChange={e => set('location', e.target.value)} placeholder="e.g. Freezer 2, shelf 3" />
              </div>
              <div className="field">
                <label>Notes</label>
                <input value={form.notes} onChange={e => set('notes', e.target.value)} />
              </div>
            </div>
            <div className="form-actions">
              <button className="btn btn-primary" disabled={saving || !form.barcode}>Save box</button>
              <button type="button" className="btn btn-secondary" onClick={() => setShowAdd(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      <div style={{ marginBottom: 16 }}>
        <input
          type="search"
          value={filter}
          onChange={e => setFilter(e.target.value)}
          placeholder="Filter by barcode, name, location…"
          style={{ width: '100%', maxWidth: 360, padding: '8px 10px', border: '1px solid var(--border)', borderRadius: 'var(--radius)', fontSize: 13 }}
        />
      </div>

      <div className="card">
        <div className="table-wrap">
          <table>
            <thead><tr><th>Barcode</th><th>Name</th><th>Location</th><th>Tubes</th><th>Created</th><th></th></tr></thead>
            <tbody>
              {visible.map(b => (
                <tr key={b.id}>
                  <td><Link to={`/boxes/${b.id}`}><span className="barcode">{b.barcode}</span></Link></td>
                  <td>{b.name || '—'}</td>
                  <td>{b.location || '—'}</td>
                  <td>{b.tube_count}</td>
                  <td style={{ color: 'var(--text2)' }}>{b.created_at?.slice(0, 10)}</td>
                  <td>
                    <div className="row-actions">
                      <Link to={`/boxes/${b.id}`} className="btn btn-secondary btn-sm">View</Link>
                      <button className="btn btn-danger btn-sm" onClick={() => handleDelete(b.id)}>Delete</button>
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
