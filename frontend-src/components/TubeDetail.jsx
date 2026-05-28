import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../api.js';
import { useToast } from './Toast.jsx';
import BarcodeInput from './BarcodeInput.jsx';
import MapPicker from './MapPicker.jsx';
import LeafletMap from './LeafletMap.jsx';

export default function TubeDetail() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const toast = useToast();
  const [tube, setTube] = useState(null);
  const [editing, setEditing] = useState(searchParams.get('edit') === '1');
  const [form, setForm] = useState({});
  const [saving, setSaving] = useState(false);
  const [boxes, setBoxes] = useState([]);
  const [boxMode, setBoxMode] = useState('scan');
  const [boxBarcode, setBoxBarcode] = useState('');
  const [creatingBox, setCreatingBox] = useState(false);
  const [showMap, setShowMap] = useState(false);
  const [showHistory, setShowHistory] = useState(true);
  const [history, setHistory] = useState(null);

  useEffect(() => {
    api.getTube(id).then(t => {
      setTube(t);
      if (searchParams.get('edit') === '1') {
        setForm({
          barcode: t.barcode, box_id: t.box_id ?? '',
          collection_date: t.collection_date ?? '', site_name: t.site_name ?? '',
          latitude: t.latitude ?? '', longitude: t.longitude ?? '',
          sample_type: t.sample_type ?? '', description: t.description ?? '',
          volume_ml: t.volume_ml ?? '', weight_g: t.weight_g ?? '', depth_cm: t.depth_cm ?? '',
        });
        setBoxBarcode(t.box_barcode ?? '');
      }
    });
  }, [id]);
  useEffect(() => { api.getTubeHistory(id).then(setHistory); }, [id]);
  useEffect(() => { if (editing) api.getBoxes().then(setBoxes); }, [editing]);

  const boxMatch = boxes.find(b => b.barcode.toLowerCase() === boxBarcode.toLowerCase());
  const boxNotFound = boxBarcode.length > 0 && !boxMatch;

  function startEditing() {
    setForm({
      barcode: tube.barcode, box_id: tube.box_id ?? '',
      collection_date: tube.collection_date ?? '', site_name: tube.site_name ?? '',
      latitude: tube.latitude ?? '', longitude: tube.longitude ?? '',
      sample_type: tube.sample_type ?? '', description: tube.description ?? '',
      volume_ml: tube.volume_ml ?? '', weight_g: tube.weight_g ?? '', depth_cm: tube.depth_cm ?? '',
    });
    setBoxBarcode(tube.box_barcode ?? '');
    setBoxMode('scan');
    setShowMap(false);
    setEditing(true);
  }

  function cancelEditing() {
    setEditing(false);
    setShowMap(false);
  }

  function handleBoxBarcodeChange(v) {
    setBoxBarcode(v);
    const match = boxes.find(b => b.barcode.toLowerCase() === v.toLowerCase());
    setForm(f => ({ ...f, box_id: match ? match.id : '' }));
  }

  function switchToScan() {
    const selected = boxes.find(b => String(b.id) === String(form.box_id));
    setBoxBarcode(selected?.barcode ?? '');
    setBoxMode('scan');
  }

  async function handleCreateBox() {
    setCreatingBox(true);
    try {
      const newBox = await api.createBox({ barcode: boxBarcode });
      setBoxes(bs => [...bs, newBox]);
      setForm(f => ({ ...f, box_id: newBox.id }));
      toast(`Box ${boxBarcode} created`);
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setCreatingBox(false);
    }
  }

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);
    try {
      const num = v => v === '' ? null : Number(v);
      const body = {
        ...form,
        box_id: form.box_id === '' ? null : Number(form.box_id),
        latitude: num(form.latitude), longitude: num(form.longitude),
        volume_ml: num(form.volume_ml), weight_g: num(form.weight_g), depth_cm: num(form.depth_cm),
      };
      const updated = await api.updateTube(id, body);
      setTube(t => ({ ...t, ...updated }));
      setEditing(false);
      setShowMap(false);
      api.getTubeHistory(id).then(setHistory);
      toast('Tube updated');
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setSaving(false);
    }
  }

  async function handleClear() {
    if (!confirm(`Clear all details from tube ${tube.barcode}? The tube and its box assignment will be kept, but all sample data will be permanently erased.`)) return;
    const updated = await api.updateTube(id, {
      barcode: tube.barcode,
      box_id: tube.box_id,
      collection_date: null, site_name: null,
      latitude: null, longitude: null,
      sample_type: null, description: null,
      volume_ml: null, weight_g: null, depth_cm: null,
    });
    setTube(t => ({ ...t, ...updated }));
    api.getTubeHistory(id).then(setHistory);
    toast('Tube cleared');
  }

  async function handleDelete() {
    if (!confirm('Delete this tube?')) return;
    await api.deleteTube(id);
    toast('Tube deleted');
    navigate('/tubes');
  }

  function toggleHistory() {
    setShowHistory(v => !v);
  }

  async function handleRevert(versionId) {
    if (!confirm('Revert this tube to the selected version?')) return;
    const updated = await api.revertTube(id, versionId);
    setTube(t => ({ ...t, ...updated }));
    api.getTubeHistory(id).then(setHistory);
    toast('Tube reverted');
  }

  if (!tube) return <p style={{ color: 'var(--text2)', padding: 32 }}>Loading…</p>;

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  return (
    <div>
      <div className="page-header">
        <div>
          <div style={{ fontSize: 12, color: 'var(--text2)', marginBottom: 4 }}><Link to="/tubes">← Tubes</Link></div>
          <h1 className="page-title"><span className="barcode" style={{ fontSize: 18 }}>{tube.barcode}</span></h1>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {editing && (
            <button type="submit" form="tube-edit-form" className="btn btn-success" disabled={saving || !form.barcode}>
              {saving ? 'Saving…' : 'Save changes'}
            </button>
          )}
          <button className="btn btn-secondary" onClick={editing ? cancelEditing : startEditing}>
            {editing ? 'Cancel' : 'Edit'}
          </button>
          <button className="btn btn-danger" onClick={handleClear}>Clear</button>
          <button className="btn btn-danger" onClick={handleDelete}>Delete</button>
        </div>
      </div>

      <div className="card card-body" style={{ marginBottom: 16 }}>
        <form id="tube-edit-form" onSubmit={handleSave}>
          <div className="form-grid" style={{ marginBottom: editing ? 12 : 0 }}>

            <div className="field span-2">
              <label>Barcode *</label>
              {editing
                ? <BarcodeInput value={form.barcode} onChange={v => set('barcode', v)} />
                : <span className="barcode">{tube.barcode}</span>}
            </div>

            <div className="field">
              <label style={editing ? { display: 'flex', justifyContent: 'space-between', alignItems: 'center' } : {}}>
                Box
                {editing && (
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    onClick={() => boxMode === 'select' ? switchToScan() : setBoxMode('select')}
                  >
                    {boxMode === 'select' ? 'Scan barcode' : 'Choose from list'}
                  </button>
                )}
              </label>
              {editing ? (
                boxMode === 'select' ? (
                  <select value={form.box_id} onChange={e => set('box_id', e.target.value)}>
                    <option value="">— Unassigned —</option>
                    {boxes.map(b => <option key={b.id} value={b.id}>{b.barcode}{b.name ? ` — ${b.name}` : ''}</option>)}
                  </select>
                ) : (
                  <>
                    <BarcodeInput value={boxBarcode} onChange={handleBoxBarcodeChange} placeholder="Scan or type box barcode" />
                    {boxMatch && (
                      <p style={{ margin: '6px 0 0', fontSize: 12, color: 'var(--accent)' }}>
                        ✓ {boxMatch.barcode}{boxMatch.name ? ` — ${boxMatch.name}` : ''}
                      </p>
                    )}
                    {boxNotFound && (
                      <p style={{ margin: '6px 0 0', fontSize: 12, color: 'var(--text2)' }}>
                        Box not found.{' '}
                        <button type="button" className="btn btn-secondary btn-sm" onClick={handleCreateBox} disabled={creatingBox}>
                          {creatingBox ? 'Creating…' : `Create "${boxBarcode}"`}
                        </button>
                      </p>
                    )}
                  </>
                )
              ) : (
                tube.box_id
                  ? <Link to={`/boxes/${tube.box_id}`}><span className="barcode">{tube.box_barcode}</span>{tube.box_name ? ` — ${tube.box_name}` : ''}</Link>
                  : <span>—</span>
              )}
            </div>

            <div className="field">
              <label>Collection date</label>
              {editing
                ? <input type="date" value={form.collection_date} onChange={e => set('collection_date', e.target.value)} />
                : <span>{tube.collection_date || '—'}</span>}
            </div>

            <div className="field">
              <label>Site name</label>
              {editing
                ? <input value={form.site_name} onChange={e => set('site_name', e.target.value)} placeholder="e.g. Lake Tahoe core 3" />
                : <span>{tube.site_name || '—'}</span>}
            </div>

            <div className="field">
              <label>Sample type</label>
              {editing
                ? <input value={form.sample_type} onChange={e => set('sample_type', e.target.value)} placeholder="e.g. surface, freeze core…" />
                : <span>{tube.sample_type || '—'}</span>}
            </div>

            <div className="field">
              <label style={editing ? { display: 'flex', justifyContent: 'space-between', alignItems: 'center' } : {}}>
                Latitude
                {editing && (
                  <button type="button" className="btn btn-secondary btn-sm" onClick={() => setShowMap(v => !v)}>
                    {showMap ? 'Hide map' : '📍 Pick on map'}
                  </button>
                )}
              </label>
              {editing
                ? <input type="number" step="any" value={form.latitude} onChange={e => set('latitude', e.target.value)} placeholder="e.g. 39.0968" />
                : <span>{tube.latitude ?? '—'}</span>}
            </div>

            <div className="field">
              <label>Longitude</label>
              {editing
                ? <input type="number" step="any" value={form.longitude} onChange={e => set('longitude', e.target.value)} placeholder="e.g. -120.0324" />
                : <span>{tube.longitude ?? '—'}</span>}
            </div>

            {editing && showMap && (
              <div className="field span-2">
                <MapPicker
                  lat={form.latitude !== '' ? Number(form.latitude) : null}
                  lng={form.longitude !== '' ? Number(form.longitude) : null}
                  onChange={(lat, lng) => { set('latitude', lat); set('longitude', lng); }}
                />
              </div>
            )}

            <div className="field">
              <label>Depth in core (cm)</label>
              {editing
                ? <input type="number" step="any" value={form.depth_cm} onChange={e => set('depth_cm', e.target.value)} placeholder="e.g. 12.5" />
                : <span>{tube.depth_cm != null ? `${tube.depth_cm} cm` : '—'}</span>}
            </div>

            <div className="field">
              <label>Volume (mL)</label>
              {editing
                ? <input type="number" step="any" value={form.volume_ml} onChange={e => set('volume_ml', e.target.value)} />
                : <span>{tube.volume_ml != null ? `${tube.volume_ml} mL` : '—'}</span>}
            </div>

            <div className="field">
              <label>Weight (g)</label>
              {editing
                ? <input type="number" step="any" value={form.weight_g} onChange={e => set('weight_g', e.target.value)} />
                : <span>{tube.weight_g != null ? `${tube.weight_g} g` : '—'}</span>}
            </div>

            <div className="field" />

            <div className="field span-2">
              <label>Description / notes</label>
              {editing
                ? <textarea value={form.description} onChange={e => set('description', e.target.value)} placeholder="Any additional notes…" />
                : <span style={{ whiteSpace: 'pre-wrap' }}>{tube.description || '—'}</span>}
            </div>

            <div className="field">
              <label>Created (UTC)</label>
              <span>{tube.created_at}</span>
            </div>

            <div className="field">
              <label>Updated (UTC)</label>
              <span>{tube.updated_at}</span>
            </div>

          </div>
        </form>
      </div>

      {tube.latitude != null && tube.longitude != null && (
        <LeafletMap points={[{ lat: tube.latitude, lng: tube.longitude, label: tube.barcode }]} />
      )}

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
                        {f('box', v.box_barcode || '—', 'box_id')}
                        {f('collected', v.collection_date || '—', 'collection_date')}
                        {f('site', v.site_name || '—', 'site_name')}
                        {f('type', v.sample_type || '—', 'sample_type')}
                        {f('depth', v.depth_cm != null ? `${v.depth_cm} cm` : '—', 'depth_cm')}
                        {f('vol', v.volume_ml != null ? `${v.volume_ml} mL` : '—', 'volume_ml')}
                        {f('weight', v.weight_g != null ? `${v.weight_g} g` : '—', 'weight_g')}
                        {f('lat', v.latitude ?? '—', 'latitude')}
                        {f('lng', v.longitude ?? '—', 'longitude')}
                        {f('description', v.description || '—', 'description')}
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
