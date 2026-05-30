import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../api.js';
import { useAuth } from '../AuthContext.jsx';
import { useToast } from './Toast.jsx';
import BarcodeInput from './BarcodeInput.jsx';
import CoordCard from './CoordCard.jsx';

export default function TubeDetail() {
  const { user } = useAuth();
  const ro = user?.is_readonly;
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const toast = useToast();
  const [tube, setTube] = useState(null);
  const [editing, setEditing] = useState(searchParams.get('edit') === '1');
  const [form, setForm] = useState({});
  const [saving, setSaving] = useState(false);
  const [boxes, setBoxes] = useState([]);
  const [cores, setCores] = useState([]);
  const [boxMode, setBoxMode] = useState('scan');
  const [coreMode, setCoreMode] = useState('scan');
  const [boxBarcode, setBoxBarcode] = useState('');
  const [coreBarcode, setCoreBarcode] = useState('');
  const [creatingBox, setCreatingBox] = useState(false);
  const [showHistory, setShowHistory] = useState(true);
  const [history, setHistory] = useState(null);

  useEffect(() => {
    api.getTube(id).then(t => {
      setTube(t);
      if (searchParams.get('edit') === '1') {
        setForm({
          barcode: t.barcode, box_id: t.box_id ?? '', core_id: t.core_id ?? '',
          sample_date: t.sample_date ?? '', site_name: t.site_name ?? '',
          latitude: t.latitude ?? '', longitude: t.longitude ?? '',
          sample_type: t.sample_type ?? '', description: t.description ?? '',
          volume_ml: t.volume_ml ?? '', weight_g: t.weight_g ?? '', depth_cm: t.depth_cm ?? '',
        });
        setBoxBarcode(t.box_barcode ?? '');
        setCoreBarcode(t.core_barcode ?? '');
      }
    });
  }, [id, searchParams]);
  useEffect(() => { api.getTubeHistory(id).then(setHistory); }, [id]);
  useEffect(() => {
    if (editing) {
      api.getBoxes().then(setBoxes);
      api.getCores().then(setCores);
    }
  }, [editing]);

  const boxMatch = boxes.find(b => b.barcode.toLowerCase() === boxBarcode.toLowerCase());
  const boxNotFound = boxBarcode.length > 0 && !boxMatch;
  const coreMatch = cores.find(c => c.barcode.toLowerCase() === coreBarcode.toLowerCase());
  const selectedCore = coreMatch || (form.core_id ? cores.find(c => String(c.id) === String(form.core_id)) : null);
  const coreNotFound = coreBarcode.length > 0 && !coreMatch;

  function startEditing() {
    setForm({
      barcode: tube.barcode, box_id: tube.box_id ?? '', core_id: tube.core_id ?? '',
      sample_date: tube.sample_date ?? '', site_name: tube.site_name ?? '',
      latitude: tube.latitude ?? '', longitude: tube.longitude ?? '',
      sample_type: tube.sample_type ?? '', description: tube.description ?? '',
      volume_ml: tube.volume_ml ?? '', weight_g: tube.weight_g ?? '', depth_cm: tube.depth_cm ?? '',
    });
    setBoxBarcode(tube.box_barcode ?? '');
    setCoreBarcode(tube.core_barcode ?? '');
    setBoxMode('scan');
    setCoreMode('scan');
    setEditing(true);
  }

  function cancelEditing() {
    setEditing(false);
  }

  function handleBoxBarcodeChange(v) {
    setBoxBarcode(v);
    const match = boxes.find(b => b.barcode.toLowerCase() === v.toLowerCase());
    setForm(f => ({ ...f, box_id: match ? match.id : '' }));
  }

  function handleCoreBarcodeChange(v) {
    setCoreBarcode(v);
    const match = cores.find(c => c.barcode.toLowerCase() === v.toLowerCase());
    setForm(f => ({ ...f, core_id: match ? match.id : '' }));
  }

  function switchToScan() {
    const selected = boxes.find(b => String(b.id) === String(form.box_id));
    setBoxBarcode(selected?.barcode ?? '');
    setBoxMode('scan');
  }

  function switchCoreToScan() {
    const selected = cores.find(c => String(c.id) === String(form.core_id));
    setCoreBarcode(selected?.barcode ?? '');
    setCoreMode('scan');
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
        core_id: form.core_id === '' ? null : Number(form.core_id),
        latitude: num(form.latitude), longitude: num(form.longitude),
        volume_ml: num(form.volume_ml), weight_g: num(form.weight_g), depth_cm: num(form.depth_cm),
      };
      const updated = await api.updateTube(id, body);
      setTube(t => ({ ...t, ...updated }));
      setEditing(false);
        api.getTubeHistory(id).then(setHistory);
      toast('Tube updated');
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setSaving(false);
    }
  }

  async function handleClear() {
    if (!confirm(`Clear all details from tube ${tube.barcode}? The tube and its box/core assignment will be kept, but all sample data will be permanently erased.`)) return;
    const updated = await api.updateTube(id, {
      barcode: tube.barcode,
      box_id: tube.box_id,
      core_id: tube.core_id,
      sample_date: null, site_name: null,
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

  if (!tube) return <p className="loading">Loading…</p>;

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  // Returns { value, inherited } — tube's own value takes precedence; null falls back to core.
  function res(tubeVal, coreVal) {
    if (tubeVal != null) return { value: tubeVal, inherited: false };
    if (tube.core_id && coreVal != null) return { value: coreVal, inherited: true };
    return { value: null, inherited: false };
  }

  const r = {
    site_name:       res(tube.site_name,       tube.core_site_name),
    latitude:        res(tube.latitude,         tube.core_latitude),
    longitude:       res(tube.longitude,        tube.core_longitude),
    sample_date:     res(tube.sample_date,       null),
    sample_type:     res(tube.sample_type,      tube.core_sample_type),
  };
  const inheritedFrom = tube.core_barcode
    ? `From core: ${tube.core_barcode}${tube.core_name ? ` — ${tube.core_name}` : ''}`
    : 'Inherited from core';

  const depthPct = (tube.core_total_depth != null && tube.depth_cm != null)
    ? Math.min(100, (tube.depth_cm / tube.core_total_depth) * 100) : null;

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="back-link">
            <Link to={searchParams.get('from') ?? '/tubes'}>← {searchParams.get('from')?.startsWith('/boxes/') ? `Box ${tube.box_barcode}` : 'Tubes'}</Link>
          </div>
          <h1 className="page-title"><span className="barcode barcode-lg">{tube.barcode}</span></h1>
        </div>
        <div className="btn-group">
          {editing && (
            <button type="submit" form="tube-edit-form" className="btn btn-success" disabled={saving || !form.barcode}>
              {saving ? 'Saving…' : 'Save changes'}
            </button>
          )}
          {!ro && (
            <button className="btn btn-secondary" onClick={editing ? cancelEditing : startEditing}>
              {editing ? 'Cancel' : 'Edit'}
            </button>
          )}
          {!ro && <button className="btn btn-danger" onClick={handleClear}>Clear</button>}
          {!ro && <button className="btn btn-danger" onClick={handleDelete}>Delete</button>}
        </div>
      </div>

      <div className="card card-body mb-4">
        <form id="tube-edit-form" onSubmit={handleSave}>
          <div className={editing ? 'form-grid mb-3' : 'form-grid'}>

            <div className="field span-2">
              <label>Barcode *</label>
              {editing
                ? <BarcodeInput value={form.barcode} onChange={v => set('barcode', v)} />
                : <span className="barcode">{tube.barcode}</span>}
            </div>

            <div className="field">
              <label className={editing ? 'field-label-row' : ''}>
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
                      <p className="form-hint accent">
                        ✓ {boxMatch.barcode}{boxMatch.name ? ` — ${boxMatch.name}` : ''}
                      </p>
                    )}
                    {boxNotFound && (
                      <p className="form-hint muted">
                        Box not found.{' '}
                        <button type="button" className="btn btn-secondary btn-sm" onClick={handleCreateBox} disabled={creatingBox}>
                          {creatingBox ? 'Creating…' : `Create "${boxBarcode}"`}
                        </button>
                      </p>
                    )}
                  </>
                )
              ) : (
                tube.box_id ? (
                  <>
                    <Link to={`/boxes/${tube.box_id}`}>
                      <span className="barcode">{tube.box_barcode}</span>{tube.box_name ? ` — ${tube.box_name}` : ''}
                    </Link>
                    {tube.box_location_name && (
                      <div className="meta">{tube.box_location_name}</div>
                    )}
                  </>
                ) : <span>—</span>
              )}
            </div>

            <div className="field">
              <label className={editing ? 'field-label-row' : ''}>
                Core
                {editing && (
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    onClick={() => coreMode === 'select' ? switchCoreToScan() : setCoreMode('select')}
                  >
                    {coreMode === 'select' ? 'Scan barcode' : 'Choose from list'}
                  </button>
                )}
              </label>
              {editing ? (
                <>
                  {coreMode === 'select' ? (
                    <select value={form.core_id} onChange={e => set('core_id', e.target.value)}>
                      <option value="">— None —</option>
                      {cores.map(c => <option key={c.id} value={c.id}>{c.barcode}{c.name ? ` — ${c.name}` : ''}</option>)}
                    </select>
                  ) : (
                    <>
                      <BarcodeInput value={coreBarcode} onChange={handleCoreBarcodeChange} placeholder="Scan or type core barcode" />
                      {coreMatch && <p className="form-hint accent">✓ {coreMatch.barcode}{coreMatch.name ? ` — ${coreMatch.name}` : ''}</p>}
                      {coreNotFound && <p className="form-hint muted">Core not found.</p>}
                    </>
                  )}
                </>
              ) : (
                tube.core_id ? (
                  <>
                    <Link to={`/cores/${tube.core_id}`}>
                      <span className="barcode">{tube.core_barcode}</span>{tube.core_name ? ` — ${tube.core_name}` : ''}
                    </Link>
                    {tube.core_location_name && (
                      <div className="meta">{tube.core_location_name}</div>
                    )}
                  </>
                ) : <span>—</span>
              )}
            </div>

            <div className="field">
              <label>Sample date</label>
              {editing ? (
                <input type="date" value={form.sample_date} onChange={e => set('sample_date', e.target.value)} />
              ) : (
                <span>{r.sample_date.value || '—'}</span>
              )}
            </div>

            <div className="field">
              <label className={editing ? 'field-label-row' : ''}>
                Site name
                {!editing && r.site_name.inherited && <span className="badge badge-inherited" data-tooltip={inheritedFrom}>inherited</span>}
              </label>
              {editing ? (
                <>
                  <input value={form.site_name} onChange={e => set('site_name', e.target.value)} placeholder="e.g. Lake Tahoe core 3" />
                  {!form.site_name && selectedCore?.site_name && (
                    <p className="form-hint muted">Inherits from core: {selectedCore.site_name}</p>
                  )}
                </>
              ) : (
                <span>{r.site_name.value || '—'}</span>
              )}
            </div>

            <div className="field">
              <label className={editing ? 'field-label-row' : ''}>
                Sample type
                {!editing && r.sample_type.inherited && <span className="badge badge-inherited" data-tooltip={inheritedFrom}>inherited</span>}
              </label>
              {editing ? (
                <>
                  <input value={form.sample_type} onChange={e => set('sample_type', e.target.value)} placeholder="e.g. surface, freeze core…" />
                  {!form.sample_type && selectedCore?.sample_type && (
                    <p className="form-hint muted">Inherits from core: {selectedCore.sample_type}</p>
                  )}
                </>
              ) : (
                <span>{r.sample_type.value || '—'}</span>
              )}
            </div>

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
                : <span className="pre-wrap">{tube.description || '—'}</span>}
            </div>

            {!editing && tube.core_id && tube.depth_cm != null && (
              <div className="field span-2">
                <label>Position in core</label>
                <div className="core-depth-ends">
                  <span>Top (0 cm)</span>
                  <span>{tube.core_total_depth != null ? `Bottom (${tube.core_total_depth} cm)` : 'Bottom'}</span>
                </div>
                <div className="core-depth-track">
                  {depthPct != null && <div className="core-depth-fill" style={{ width: `${depthPct}%` }} />}
                  <div className="core-depth-marker" style={{ left: depthPct != null ? `${depthPct}%` : '0%' }} />
                </div>
                <div className="core-depth-label">{tube.depth_cm} cm depth</div>
              </div>
            )}

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

      <CoordCard
        editing={editing}
        lat={editing ? form.latitude : r.latitude.value}
        lng={editing ? form.longitude : r.longitude.value}
        onChange={(lat, lng) => { set('latitude', lat); set('longitude', lng); }}
        mapLabel={tube.barcode}
        latBadge={!editing && r.latitude.inherited && <span className="badge badge-inherited" data-tooltip={inheritedFrom}>inherited</span>}
        lngBadge={!editing && r.longitude.inherited && <span className="badge badge-inherited" data-tooltip={inheritedFrom}>inherited</span>}
        latHint={!form.latitude && selectedCore?.latitude != null ? `Inherits from core: ${selectedCore.latitude}` : null}
        lngHint={!form.longitude && selectedCore?.longitude != null ? `Inherits from core: ${selectedCore.longitude}` : null}
      />

      <div className="mt-4">
        <button className="btn btn-secondary btn-sm" onClick={toggleHistory}>
          {showHistory ? '▼' : '▶'} Version history{history ? ` (${history.length})` : ''}
        </button>
        {showHistory && (
          <div className="card mt-2">
            {history === null && <p className="card-message">Loading…</p>}
            {history?.length === 0 && <p className="card-message">No history yet.</p>}
            {history?.map((v, i) => {
              const prev = history[i + 1];
              const diff = (key) => prev && String(v[key] ?? '') !== String(prev[key] ?? '');
              const f = (label, value, key) => (
                <span>
                  <em className={diff(key) ? 'diff' : ''}>{label}</em>{' '}
                  <span className={diff(key) ? 'diff-value' : ''}>{value}</span>
                </span>
              );
              return (
                <div key={v.id} className="history-entry">
                  <div className="history-row">
                    <div>
                      <div className="history-meta">
                        {v.changed_at} — <strong>{v.changed_by_username ?? 'unknown'}</strong>
                      </div>
                      <div className="history-fields">
                        {f('barcode', v.barcode, 'barcode')}
                        {f('box', v.box_barcode || '—', 'box_id')}
                        {f('core', v.core_barcode || '—', 'core_id')}
                        {f('sampled', v.sample_date || '—', 'sample_date')}
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
                      <button className="btn btn-secondary btn-sm flex-shrink-0" onClick={() => handleRevert(v.id)}>
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
