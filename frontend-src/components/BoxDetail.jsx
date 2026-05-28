import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../api.js';
import { useToast } from './Toast.jsx';
import BarcodeInput from './BarcodeInput.jsx';
import LeafletMap from './LeafletMap.jsx';

export default function BoxDetail() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const toast = useToast();
  const [box, setBox] = useState(null);
  const [editing, setEditing] = useState(searchParams.get('edit') === '1');
  const [form, setForm] = useState({});
  const [saving, setSaving] = useState(false);
  const [showAssign, setShowAssign] = useState(false);
  const [assignBarcode, setAssignBarcode] = useState('');
  const [unassigned, setUnassigned] = useState([]);
  const [showHistory, setShowHistory] = useState(true);
  const [history, setHistory] = useState(null);

  useEffect(() => {
    api.getBox(id).then(b => { setBox(b); setForm({ barcode: b.barcode, name: b.name ?? '', location: b.location ?? '', notes: b.notes ?? '' }); });
  }, [id]);
  useEffect(() => { api.getBoxHistory(id).then(setHistory); }, [id]);

  useEffect(() => {
    if (showAssign && unassigned.length === 0) {
      api.getTubes().then(tubes => setUnassigned(tubes.filter(t => !t.box_id)));
    }
  }, [showAssign]);

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const assignMatch = assignBarcode
    ? unassigned.find(t => t.barcode.toLowerCase() === assignBarcode.toLowerCase())
    : null;
  const assignNotFound = assignBarcode.length > 0 && !assignMatch;

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);
    try {
      const updated = await api.updateBox(id, form);
      setBox(b => ({ ...b, ...updated }));
      setEditing(false);
      api.getBoxHistory(id).then(setHistory);
      toast('Box updated');
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setSaving(false);
    }
  }

  async function handleEmpty() {
    if (!box.tubes?.length) return;
    if (!confirm(`Unassign all ${box.tubes.length} tube${box.tubes.length !== 1 ? 's' : ''} from this box?`)) return;
    await api.emptyBox(id);
    setBox(b => ({ ...b, tubes: [] }));
    toast('Box emptied');
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
    setUnassigned(us => [...us, box.tubes.find(t => t.id === tubeId)]);
    toast('Tube removed from box');
  }

  async function handleAssign() {
    if (!assignMatch) return;
    await api.updateTube(assignMatch.id, { ...assignMatch, box_id: Number(id) });
    setBox(b => ({ ...b, tubes: [...(b.tubes ?? []), { ...assignMatch, box_id: Number(id) }] }));
    setUnassigned(us => us.filter(t => t.id !== assignMatch.id));
    setAssignBarcode('');
    toast(`Tube ${assignMatch.barcode} added to box`);
  }

  function toggleHistory() {
    setShowHistory(v => !v);
  }

  async function handleRevert(versionId) {
    if (!confirm('Revert this box to the selected version?')) return;
    const updated = await api.revertBox(id, versionId);
    setBox(b => ({ ...b, ...updated }));
    api.getBoxHistory(id).then(setHistory);
    toast('Box reverted');
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
          {editing && (
            <button type="submit" form="box-edit-form" className="btn btn-success" disabled={saving}>Save Changes</button>
          )}
          <button className="btn btn-secondary" onClick={() => setEditing(v => !v)}>
            {editing ? 'Cancel' : 'Edit'}
          </button>
          <button className="btn btn-danger" onClick={handleDelete}>Delete</button>
        </div>
      </div>

      <div className="card card-body" style={{ marginBottom: 24 }}>
        <form id="box-edit-form" onSubmit={handleSave}>
          <div className="form-grid" style={{ marginBottom: 0 }}>
            <div className="field">
              <label>Barcode *</label>
              {editing
                ? <BarcodeInput value={form.barcode} onChange={v => set('barcode', v)} />
                : <span className="barcode">{box.barcode}</span>}
            </div>
            <div className="field">
              <label>Name</label>
              {editing
                ? <input value={form.name} onChange={e => set('name', e.target.value)} />
                : <span>{box.name || '—'}</span>}
            </div>
            <div className="field">
              <label>Location</label>
              {editing
                ? <input value={form.location} onChange={e => set('location', e.target.value)} />
                : <span>{box.location || '—'}</span>}
            </div>
            <div className="field">
              <label>Notes</label>
              {editing
                ? <input value={form.notes} onChange={e => set('notes', e.target.value)} />
                : <span>{box.notes || '—'}</span>}
            </div>
            <div className="field">
              <label>Created (UTC)</label>
              <span>{box.created_at}</span>
            </div>
            <div className="field">
              <label>Updated (UTC)</label>
              <span>{box.updated_at}</span>
            </div>
          </div>
        </form>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <h2 style={{ fontSize: 15, fontWeight: 700 }}>Tubes ({box.tubes?.length ?? 0})</h2>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-secondary btn-sm" onClick={() => setShowAssign(v => !v)}>
            Assign existing
          </button>
          {box.tubes?.length > 0 && (
            <button className="btn btn-danger btn-sm" onClick={handleEmpty}>Empty box</button>
          )}
          <Link to={`/tubes/new?box_id=${id}`} className="btn btn-primary btn-sm">+ New tube</Link>
        </div>
      </div>

      {showAssign && (
        <div className="card card-body" style={{ marginBottom: 16 }}>
          <BarcodeInput
            value={assignBarcode}
            onChange={setAssignBarcode}
            placeholder="Scan or type tube barcode to filter…"
            autoFocus
          />
          {assignMatch && (
            <div style={{ marginTop: 10, display: 'flex', alignItems: 'center', gap: 12 }}>
              <span style={{ fontSize: 13 }}>
                <span className="barcode">{assignMatch.barcode}</span>
                {assignMatch.site_name ? ` — ${assignMatch.site_name}` : ''}
              </span>
              <button className="btn btn-primary btn-sm" onClick={handleAssign}>
                Assign to this box
              </button>
            </div>
          )}
          {assignNotFound && (
            <p style={{ marginTop: 8, fontSize: 12, color: 'var(--text2)' }}>
              No unassigned tube with that barcode.
            </p>
          )}
          {!assignMatch && unassigned.length > 0 && (() => {
            const q = assignBarcode.toLowerCase();
            const filtered = q
              ? unassigned.filter(t =>
                  t.barcode.toLowerCase().includes(q) ||
                  (t.site_name ?? '').toLowerCase().includes(q) ||
                  (t.sample_type ?? '').toLowerCase().includes(q)
                )
              : unassigned;
            return filtered.length > 0 ? (
              <div style={{ marginTop: 12 }}>
                <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text2)', marginBottom: 6 }}>
                  Unassigned tubes {q ? `(${filtered.length} match${filtered.length !== 1 ? 'es' : ''})` : `(${filtered.length})`}
                </div>
                <div style={{ maxHeight: 240, overflowY: 'auto', border: '1px solid var(--border)', borderRadius: 'var(--radius)' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <tbody>
                      {filtered.map(t => (
                        <tr
                          key={t.id}
                          style={{ cursor: 'pointer', borderBottom: '1px solid var(--border)' }}
                          onClick={async () => {
                            await api.updateTube(t.id, { ...t, box_id: Number(id) });
                            setBox(b => ({ ...b, tubes: [...(b.tubes ?? []), { ...t, box_id: Number(id) }] }));
                            setUnassigned(us => us.filter(u => u.id !== t.id));
                            toast(`Tube ${t.barcode} added to box`);
                          }}
                        >
                          <td style={{ padding: '8px 12px' }}><span className="barcode">{t.barcode}</span></td>
                          <td style={{ padding: '8px 12px', color: 'var(--text2)', fontSize: 13 }}>{t.site_name || '—'}</td>
                          <td style={{ padding: '8px 12px', color: 'var(--text2)', fontSize: 13 }}>{t.sample_type || '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : null;
          })()}
          {unassigned.length === 0 && !assignBarcode && (
            <p style={{ marginTop: 10, fontSize: 12, color: 'var(--text2)' }}>No unassigned tubes.</p>
          )}
        </div>
      )}

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
                      <Link to={`/tubes/${t.id}?edit=1`} className="btn btn-secondary btn-sm">Edit</Link>
                      <button className="btn btn-danger btn-sm" onClick={() => handleRemoveTube(t.id)}>Remove</button>
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

      <div style={{ marginTop: 16 }}>
        <button className="btn btn-secondary btn-sm" onClick={toggleHistory}>
          {showHistory ? '▼' : '▶'} Version history{history ? ` (${history.length})` : ''}
        </button>
        {showHistory && (
          <div className="card" style={{ marginTop: 8 }}>
            {history === null && <p style={{ padding: 16, color: 'var(--text2)' }}>Loading…</p>}
            {history?.length === 0 && <p style={{ padding: 16, color: 'var(--text2)' }}>No history yet.</p>}
            {history?.map((v, i) => {
              const prev = history[i + 1];
              const diff = (key) => prev && String(v[key] ?? '') !== String(prev[key] ?? '');
              const f = (label, value, key) => (
                <span>
                  <em style={diff(key) ? { borderColor: 'var(--accent-light)', color: 'var(--accent-light)' } : {}}>{label}</em>{' '}
                  <span style={diff(key) ? { color: 'var(--accent-light)', fontWeight: 600 } : {}}>{value}</span>
                </span>
              );
              return (
                <div key={v.id} style={{ padding: '12px 16px', borderBottom: i < history.length - 1 ? '1px solid var(--border)' : undefined }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12 }}>
                    <div>
                      <div style={{ fontSize: 12, color: 'var(--text2)', marginBottom: 4 }}>
                        {v.changed_at} — <strong>{v.changed_by_username ?? 'unknown'}</strong>
                      </div>
                      <div className="history-fields" style={{ fontSize: 13 }}>
                        {f('barcode', v.barcode, 'barcode')}
                        {f('name', v.name || '—', 'name')}
                        {f('location', v.location || '—', 'location')}
                        {f('notes', v.notes || '—', 'notes')}
                      </div>
                    </div>
                    {i > 0 && (
                      <button className="btn btn-secondary btn-sm" style={{ flexShrink: 0 }} onClick={() => handleRevert(v.id)}>
                        Revert to this
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
