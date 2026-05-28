import { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams, Link } from 'react-router-dom';
import { api } from '../api.js';
import { useToast } from './Toast.jsx';
import BarcodeInput from './BarcodeInput.jsx';
import MapPicker from './MapPicker.jsx';

const EMPTY = {
  barcode: '', box_id: '', collection_date: '', site_name: '',
  latitude: '', longitude: '', sample_type: '', description: '',
  volume_ml: '', weight_g: '', depth_cm: '',
};

export default function TubeForm({ mode }) {
  const { id } = useParams();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const toast = useToast();
  const [form, setForm] = useState({ ...EMPTY, box_id: params.get('box_id') ?? '' });
  const [boxes, setBoxes] = useState([]);
  const [saving, setSaving] = useState(false);
  const [boxMode, setBoxMode] = useState('scan');
  const [showMap, setShowMap] = useState(false);
  const [boxBarcode, setBoxBarcode] = useState('');
  const [creatingBox, setCreatingBox] = useState(false);
  const isEdit = mode === 'edit';

  const boxMatch = boxes.find(b => b.barcode.toLowerCase() === boxBarcode.toLowerCase());
  const boxNotFound = boxBarcode.length > 0 && !boxMatch;

  function handleBoxBarcodeChange(v) {
    setBoxBarcode(v);
    const match = boxes.find(b => b.barcode.toLowerCase() === v.toLowerCase());
    set('box_id', match ? match.id : '');
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
      set('box_id', newBox.id);
      toast(`Box ${boxBarcode} created`);
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setCreatingBox(false);
    }
  }

  useEffect(() => { api.getBoxes().then(setBoxes); }, []);
  useEffect(() => {
    if (isEdit && id) {
      api.getTube(id).then(t => {
        setForm({
          barcode: t.barcode, box_id: t.box_id ?? '', collection_date: t.collection_date ?? '',
          site_name: t.site_name ?? '', latitude: t.latitude ?? '', longitude: t.longitude ?? '',
          sample_type: t.sample_type ?? '', description: t.description ?? '',
          volume_ml: t.volume_ml ?? '', weight_g: t.weight_g ?? '', depth_cm: t.depth_cm ?? '',
        });
        if (t.box_barcode) setBoxBarcode(t.box_barcode);
      });
    }
  }, [isEdit, id]);

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));
  const num = v => v === '' ? null : Number(v);

  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    try {
      const body = {
        ...form,
        box_id: form.box_id === '' ? null : Number(form.box_id),
        latitude: num(form.latitude), longitude: num(form.longitude),
        volume_ml: num(form.volume_ml), weight_g: num(form.weight_g), depth_cm: num(form.depth_cm),
      };
      if (isEdit) {
        await api.updateTube(id, body);
        toast('Tube updated');
        navigate(`/tubes/${id}`);
      } else {
        const tube = await api.createTube(body);
        toast('Tube created');
        navigate(`/tubes/${tube.id}`);
      }
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <div style={{ fontSize: 12, color: 'var(--text2)', marginBottom: 4 }}>
            {isEdit ? <Link to={`/tubes/${id}`}>← Tube</Link> : <Link to="/tubes">← Tubes</Link>}
          </div>
          <h1 className="page-title">{isEdit ? 'Edit tube' : 'New tube'}</h1>
        </div>
      </div>

      <div className="card card-body">
        <form onSubmit={handleSubmit}>
          <div className="form-grid" style={{ marginBottom: 16 }}>
            <div className="field span-2">
              <label>Barcode *</label>
              <BarcodeInput
                value={form.barcode}
                onChange={v => set('barcode', v)}
                placeholder="Scan or type tube barcode"
                autoFocus={!isEdit}
              />
            </div>

            <div className="field">
              <label style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                Box
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={() => boxMode === 'select' ? switchToScan() : setBoxMode('select')}
                >
                  {boxMode === 'select' ? 'Scan barcode' : 'Choose from list'}
                </button>
              </label>
              {boxMode === 'select' ? (
                <select value={form.box_id} onChange={e => set('box_id', e.target.value)}>
                  <option value="">— Unassigned —</option>
                  {boxes.map(b => <option key={b.id} value={b.id}>{b.barcode}{b.name ? ` — ${b.name}` : ''}</option>)}
                </select>
              ) : (
                <>
                  <BarcodeInput
                    value={boxBarcode}
                    onChange={handleBoxBarcodeChange}
                    placeholder="Scan or type box barcode"
                  />
                  {boxMatch && (
                    <p style={{ margin: '6px 0 0', fontSize: 12, color: 'var(--accent)' }}>
                      ✓ {boxMatch.barcode}{boxMatch.name ? ` — ${boxMatch.name}` : ''}
                    </p>
                  )}
                  {boxNotFound && (
                    <p style={{ margin: '6px 0 0', fontSize: 12, color: 'var(--text2)' }}>
                      Box not found.{' '}
                      <button
                        type="button"
                        className="btn btn-secondary btn-sm"
                        onClick={handleCreateBox}
                        disabled={creatingBox}
                      >
                        {creatingBox ? 'Creating…' : `Create "${boxBarcode}"`}
                      </button>
                    </p>
                  )}
                </>
              )}
            </div>

            <div className="field">
              <label>Collection date</label>
              <input type="date" value={form.collection_date} onChange={e => set('collection_date', e.target.value)} />
            </div>

            <div className="field">
              <label>Site name</label>
              <input value={form.site_name} onChange={e => set('site_name', e.target.value)} placeholder="e.g. Lake Tahoe core 3" />
            </div>

            <div className="field">
              <label>Sample type</label>
              <input value={form.sample_type} onChange={e => set('sample_type', e.target.value)} placeholder="e.g. surface, freeze core…" />
            </div>

            <div className="field">
              <label style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                Latitude
                <button type="button" className="btn btn-secondary btn-sm" onClick={() => setShowMap(v => !v)}>
                  {showMap ? 'Hide map' : '📍 Pick on map'}
                </button>
              </label>
              <input type="number" step="any" value={form.latitude} onChange={e => set('latitude', e.target.value)} placeholder="e.g. 39.0968" />
            </div>

            <div className="field">
              <label>Longitude</label>
              <input type="number" step="any" value={form.longitude} onChange={e => set('longitude', e.target.value)} placeholder="e.g. -120.0324" />
            </div>

            {showMap && (
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
              <input type="number" step="any" value={form.depth_cm} onChange={e => set('depth_cm', e.target.value)} placeholder="e.g. 12.5" />
            </div>

            <div className="field">
              <label>Volume (mL)</label>
              <input type="number" step="any" value={form.volume_ml} onChange={e => set('volume_ml', e.target.value)} />
            </div>

            <div className="field">
              <label>Weight (g)</label>
              <input type="number" step="any" value={form.weight_g} onChange={e => set('weight_g', e.target.value)} />
            </div>

            <div className="field span-2">
              <label>Description / notes</label>
              <textarea value={form.description} onChange={e => set('description', e.target.value)} placeholder="Any additional notes…" />
            </div>
          </div>

          <div className="form-actions">
            <button className="btn btn-primary" disabled={saving || !form.barcode}>
              {saving ? 'Saving…' : isEdit ? 'Save changes' : 'Create tube'}
            </button>
            <button type="button" className="btn btn-secondary" onClick={() => navigate(-1)}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  );
}
