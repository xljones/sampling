import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { api } from '../api.js';
import { useToast } from './Toast.jsx';
import BarcodeInput from './BarcodeInput.jsx';
import LeafletMap from './LeafletMap.jsx';

export default function BoxDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const [box, setBox] = useState(null);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.getBox(id).then(b => { setBox(b); setForm({ barcode: b.barcode, name: b.name ?? '', location: b.location ?? '', notes: b.notes ?? '' }); });
  }, [id]);

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);
    try {
      const updated = await api.updateBox(id, form);
      setBox(b => ({ ...b, ...updated }));
      setEditing(false);
      toast('Box updated');
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    if (!confirm('Delete this box? Tubes will become unassigned.')) return;
    await api.deleteBox(id);
    toast('Box deleted');
    navigate('/boxes');
  }

  async function handleRemoveTube(tubeId) {
    await api.updateTube(tubeId, { ...box.tubes.find(t => t.id === tubeId), box_id: null });
    setBox(b => ({ ...b, tubes: b.tubes.filter(t => t.id !== tubeId) }));
    toast('Tube removed from box');
  }

  if (!box) return <p style={{ color: 'var(--text2)', padding: 32 }}>Loading…</p>;

  return (
    <div>
      <div className="page-header">
        <div>
          <div style={{ fontSize: 12, color: 'var(--text2)', marginBottom: 4 }}><Link to="/boxes">← Boxes</Link></div>
          <h1 className="page-title">{box.name || <span className="barcode">{box.barcode}</span>}</h1>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-secondary" onClick={() => setEditing(v => !v)}>Edit</button>
          <button className="btn btn-danger" onClick={handleDelete}>Delete</button>
        </div>
      </div>

      {editing ? (
        <div className="card card-body" style={{ marginBottom: 24 }}>
          <form onSubmit={handleSave}>
            <div className="form-grid" style={{ marginBottom: 12 }}>
              <div className="field">
                <label>Barcode *</label>
                <BarcodeInput value={form.barcode} onChange={v => set('barcode', v)} />
              </div>
              <div className="field">
                <label>Name</label>
                <input value={form.name} onChange={e => set('name', e.target.value)} />
              </div>
              <div className="field">
                <label>Location</label>
                <input value={form.location} onChange={e => set('location', e.target.value)} />
              </div>
              <div className="field">
                <label>Notes</label>
                <input value={form.notes} onChange={e => set('notes', e.target.value)} />
              </div>
            </div>
            <div className="form-actions">
              <button className="btn btn-primary" disabled={saving}>Save</button>
              <button type="button" className="btn btn-secondary" onClick={() => setEditing(false)}>Cancel</button>
            </div>
          </form>
        </div>
      ) : (
        <div className="card card-body" style={{ marginBottom: 24, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <div><span style={{ color: 'var(--text2)', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Barcode</span><br /><span className="barcode">{box.barcode}</span></div>
          <div><span style={{ color: 'var(--text2)', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Location</span><br />{box.location || '—'}</div>
          <div><span style={{ color: 'var(--text2)', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Notes</span><br />{box.notes || '—'}</div>
          <div><span style={{ color: 'var(--text2)', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Created</span><br />{box.created_at?.slice(0, 10)}</div>
        </div>
      )}

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <h2 style={{ fontSize: 15, fontWeight: 700 }}>Tubes ({box.tubes?.length ?? 0})</h2>
        <Link to={`/tubes/new?box_id=${id}`} className="btn btn-primary btn-sm">+ Add tube</Link>
      </div>
      <div className="card">
        <div className="table-wrap">
          <table>
            <thead><tr><th>Barcode</th><th>Site</th><th>Type</th><th>Depth (cm)</th><th>Date</th><th></th></tr></thead>
            <tbody>
              {box.tubes?.map(t => (
                <tr key={t.id}>
                  <td><Link to={`/tubes/${t.id}`}><span className="barcode">{t.barcode}</span></Link></td>
                  <td>{t.site_name || '—'}</td>
                  <td>{t.sample_type || '—'}</td>
                  <td>{t.depth_cm ?? '—'}</td>
                  <td>{t.collection_date || '—'}</td>
                  <td>
                    <div className="row-actions">
                      <Link to={`/tubes/${t.id}`} className="btn btn-secondary btn-sm">View</Link>
                      <button className="btn btn-secondary btn-sm" onClick={() => handleRemoveTube(t.id)}>Remove</button>
                    </div>
                  </td>
                </tr>
              ))}
              {(box.tubes?.length ?? 0) === 0 && <tr><td colSpan={6} className="empty">No tubes in this box</td></tr>}
            </tbody>
          </table>
        </div>
      </div>

      <LeafletMap
        points={(box.tubes ?? [])
          .filter(t => t.latitude != null && t.longitude != null)
          .map(t => ({ lat: t.latitude, lng: t.longitude, label: t.barcode + (t.site_name ? ` — ${t.site_name}` : ''), url: `/tubes/${t.id}` }))}
      />
    </div>
  );
}
