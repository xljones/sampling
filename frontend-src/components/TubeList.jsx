import { useState, useEffect } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { api } from '../api.js';
import { useAuth } from '../AuthContext.jsx';
import { useToast } from './Toast.jsx';
import BarcodeInput from './BarcodeInput.jsx';

export default function TubeList() {
  const { user } = useAuth();
  const ro = user?.is_readonly;
  const [tubes, setTubes] = useState([]);
  const [filter, setFilter] = useState('');
  const [searchParams, setSearchParams] = useSearchParams();
  const toast = useToast();
  const [selected, setSelected] = useState(new Set());
  const [boxes, setBoxes] = useState([]);
  const [assignBarcode, setAssignBarcode] = useState('');
  const [assignBoxId, setAssignBoxId] = useState('');
  const [assignMode, setAssignMode] = useState('scan');
  const [assigning, setAssigning] = useState(false);

  const navigate = useNavigate();
  const unassignedOnly = searchParams.get('unassigned') === 'true';

  useEffect(() => { api.getTubes().then(setTubes); }, []);
  useEffect(() => { api.getBoxes().then(setBoxes); }, []);

  const q = filter.toLowerCase();
  const visible = tubes
    .filter(t => !unassignedOnly || !t.box_id)
    .filter(t => !q || (
      t.barcode.toLowerCase().includes(q) ||
      (t.site_name ?? '').toLowerCase().includes(q) ||
      (t.sample_type ?? '').toLowerCase().includes(q) ||
      (t.box_barcode ?? '').toLowerCase().includes(q) ||
      (t.box_name ?? '').toLowerCase().includes(q) ||
      (t.description ?? '').toLowerCase().includes(q) ||
      (t.collection_date ?? '').toLowerCase().includes(q) ||
      (t.volume_ml != null ? String(t.volume_ml) : '').includes(q) ||
      (t.weight_g != null ? String(t.weight_g) : '').includes(q) ||
      (t.depth_cm != null ? String(t.depth_cm) : '').includes(q) ||
      (t.latitude != null ? String(t.latitude) : '').includes(q) ||
      (t.longitude != null ? String(t.longitude) : '').includes(q)
    ));

  const allVisibleSelected = visible.length > 0 && visible.every(t => selected.has(t.id));

  function toggleAll() {
    if (allVisibleSelected) {
      setSelected(s => { const n = new Set(s); visible.forEach(t => n.delete(t.id)); return n; });
    } else {
      setSelected(s => { const n = new Set(s); visible.forEach(t => n.add(t.id)); return n; });
    }
  }

  function toggleOne(id) {
    setSelected(s => { const n = new Set(s); n.has(id) ? n.delete(id) : n.add(id); return n; });
  }

  async function handleDelete(id) {
    if (!confirm('Delete this tube?')) return;
    await api.deleteTube(id);
    setTubes(t => t.filter(x => x.id !== id));
    setSelected(s => { const n = new Set(s); n.delete(id); return n; });
    toast('Tube deleted');
  }

  const boxMatch = assignMode === 'scan'
    ? (assignBarcode ? boxes.find(b => b.barcode.toLowerCase() === assignBarcode.toLowerCase()) : null)
    : (assignBoxId ? boxes.find(b => String(b.id) === assignBoxId) : null);

  async function handleBulkAssign() {
    if (!boxMatch) return;
    setAssigning(true);
    try {
      const ids = [...selected];
      await api.bulkAssignTubes(ids, boxMatch.id);
      setTubes(ts => ts.map(t => selected.has(t.id)
        ? { ...t, box_id: boxMatch.id, box_barcode: boxMatch.barcode, box_name: boxMatch.name, box_location_name: boxMatch.location_name }
        : t
      ));
      toast(`${ids.length} tube${ids.length !== 1 ? 's' : ''} assigned to ${boxMatch.barcode}`);
      setSelected(new Set());
      setAssignBarcode('');
      setAssignBoxId('');
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setAssigning(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">{unassignedOnly ? 'Unassigned tubes' : 'Tubes'}</h1>
        <div className="btn-group">
          <a href="/api/export/tubes" className="btn btn-secondary" download>Export CSV</a>
          {!ro && <Link to="/tubes/new" className="btn btn-primary">+ New tube</Link>}
        </div>
      </div>

      <div className="filter-bar">
        <input
          type="search"
          value={filter}
          onChange={e => setFilter(e.target.value)}
          placeholder="Filter by barcode, site, type…"
          className="search-input"
        />
        {unassignedOnly && (
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => setSearchParams({})}
          >
            Unassigned only ✕
          </button>
        )}
      </div>

      {selected.size > 0 && !ro && (
        <div className="card card-body mb-4 assign-bar">
          <span className="text-sm fw-600">{selected.size} tube{selected.size !== 1 ? 's' : ''} selected</span>
          <div className="assign-input-group">
            {assignMode === 'scan' ? (
              <>
                <BarcodeInput
                  value={assignBarcode}
                  onChange={setAssignBarcode}
                  placeholder="Scan or type box barcode…"
                />
                {assignBarcode && !boxMatch && (
                  <span className="meta">Box not found</span>
                )}
              </>
            ) : (
              <select
                value={assignBoxId}
                onChange={e => setAssignBoxId(e.target.value)}
                className="select-sm"
              >
                <option value="">— Select a box —</option>
                {boxes.map(b => <option key={b.id} value={b.id}>{b.barcode}{b.name ? ` — ${b.name}` : ''}</option>)}
              </select>
            )}
            <button
              className="btn btn-secondary btn-sm flex-shrink-0"
              onClick={() => {
                if (assignMode === 'scan') { setAssignMode('select'); setAssignBarcode(''); }
                else { setAssignMode('scan'); setAssignBoxId(''); }
              }}
            >
              {assignMode === 'scan' ? 'Choose from list' : 'Scan barcode'}
            </button>
            {boxMatch && (
              <button className="btn btn-success btn-sm flex-shrink-0" onClick={handleBulkAssign} disabled={assigning}>
                {assigning ? 'Assigning…' : `Assign to ${boxMatch.barcode}`}
              </button>
            )}
          </div>
          <button className="btn btn-secondary btn-sm" onClick={() => { setSelected(new Set()); setAssignBarcode(''); setAssignBoxId(''); setAssignMode('scan'); }}>
            Clear selection
          </button>
        </div>
      )}

      <div className="card">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                {!ro && (
                  <th className="col-checkbox">
                    <input type="checkbox" checked={allVisibleSelected} onChange={toggleAll} />
                  </th>
                )}
                <th>Barcode</th><th>Box</th><th>Site</th><th>Type</th>
                <th className="col-mobile-hide">Depth (cm)</th><th className="col-mobile-hide">Collected</th><th></th>
              </tr>
            </thead>
            <tbody>
              {visible.map(t => (
                <tr
                  key={t.id}
                  className={`row-clickable${selected.has(t.id) ? ' row-selected' : ''}`}
                  onClick={e => { if (!e.target.closest('a, button, input')) navigate(`/tubes/${t.id}`); }}
                >
                  {!ro && (
                    <td className="col-checkbox" onClick={e => e.stopPropagation()}>
                      <input type="checkbox" checked={selected.has(t.id)} onChange={() => toggleOne(t.id)} />
                    </td>
                  )}
                  <td><Link to={`/tubes/${t.id}`}><span className="barcode">{t.barcode}</span></Link></td>
                  <td>{t.box_barcode ? <Link to={`/boxes/${t.box_id}`}><span className="barcode">{t.box_barcode}</span></Link> : <span className="text-muted">—</span>}</td>
                  <td>{t.site_name || '—'}</td>
                  <td>{t.sample_type || '—'}</td>
                  <td className="col-mobile-hide">{t.depth_cm ?? '—'}</td>
                  <td className="col-mobile-hide">{t.collection_date || '—'}</td>
                  <td>
                    <div className="row-actions">
                      {!ro && <Link to={`/tubes/${t.id}?edit=1`} className="btn btn-secondary btn-sm">Edit</Link>}
                      {!ro && <button className="btn btn-danger btn-sm" onClick={() => handleDelete(t.id)}>Delete</button>}
                    </div>
                  </td>
                </tr>
              ))}
              {visible.length === 0 && <tr><td colSpan={ro ? 7 : 8} className="empty">{filter ? 'No matches' : 'No tubes yet'}</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
