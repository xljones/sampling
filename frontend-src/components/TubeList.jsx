import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api } from '../api.js';
import { useToast } from './Toast.jsx';

export default function TubeList() {
  const [tubes, setTubes] = useState([]);
  const [filter, setFilter] = useState('');
  const [searchParams, setSearchParams] = useSearchParams();
  const toast = useToast();

  const unassignedOnly = searchParams.get('unassigned') === 'true';

  useEffect(() => { api.getTubes().then(setTubes); }, []);

  const q = filter.toLowerCase();
  const visible = tubes
    .filter(t => !unassignedOnly || !t.box_id)
    .filter(t => !q || (
      t.barcode.toLowerCase().includes(q) ||
      (t.site_name ?? '').toLowerCase().includes(q) ||
      (t.sample_type ?? '').toLowerCase().includes(q) ||
      (t.box_barcode ?? '').toLowerCase().includes(q)
    ));

  async function handleDelete(id) {
    if (!confirm('Delete this tube?')) return;
    await api.deleteTube(id);
    setTubes(t => t.filter(x => x.id !== id));
    toast('Tube deleted');
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">{unassignedOnly ? 'Unassigned tubes' : 'Tubes'}</h1>
        <div style={{ display: 'flex', gap: 8 }}>
          <a href="/api/export/tubes" className="btn btn-secondary" download>Export CSV</a>
          <Link to="/tubes/new" className="btn btn-primary">+ New tube</Link>
        </div>
      </div>

      <div style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
        <input
          type="search"
          value={filter}
          onChange={e => setFilter(e.target.value)}
          placeholder="Filter by barcode, site, type…"
          style={{ width: '100%', maxWidth: 360, padding: '8px 10px', border: '1px solid var(--border)', borderRadius: 'var(--radius)', fontSize: 13 }}
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

      <div className="card">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Barcode</th><th>Box</th><th>Site</th><th>Type</th>
                <th>Depth (cm)</th><th>Collected</th><th></th>
              </tr>
            </thead>
            <tbody>
              {visible.map(t => (
                <tr key={t.id}>
                  <td><Link to={`/tubes/${t.id}`}><span className="barcode">{t.barcode}</span></Link></td>
                  <td>{t.box_barcode ? <Link to={`/boxes/${t.box_id}`}><span className="barcode">{t.box_barcode}</span></Link> : <span style={{ color: 'var(--text2)' }}>—</span>}</td>
                  <td>{t.site_name || '—'}</td>
                  <td>{t.sample_type || '—'}</td>
                  <td>{t.depth_cm ?? '—'}</td>
                  <td>{t.collection_date || '—'}</td>
                  <td>
                    <div className="row-actions">
                      <Link to={`/tubes/${t.id}`} className="btn btn-secondary btn-sm">View</Link>
                      <Link to={`/tubes/${t.id}?edit=1`} className="btn btn-secondary btn-sm">Edit</Link>
                      <button className="btn btn-danger btn-sm" onClick={() => handleDelete(t.id)}>Delete</button>
                    </div>
                  </td>
                </tr>
              ))}
              {visible.length === 0 && <tr><td colSpan={7} className="empty">{filter ? 'No matches' : 'No tubes yet'}</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
