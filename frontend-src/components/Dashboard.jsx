import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api.js';
import LeafletMap from './LeafletMap.jsx';

export default function Dashboard() {
  const [boxes, setBoxes] = useState([]);
  const [tubes, setTubes] = useState([]);

  useEffect(() => {
    api.getBoxes().then(setBoxes).catch(() => {});
    api.getTubes().then(setTubes).catch(() => {});
  }, []);

  const navigate = useNavigate();
  const unassigned = tubes.filter(t => !t.box_id).length;
  const mappable = tubes
    .filter(t => t.latitude != null && t.longitude != null)
    .map(t => ({ lat: t.latitude, lng: t.longitude, label: t.barcode + (t.site_name ? ` — ${t.site_name}` : ''), url: `/tubes/${t.id}` }));

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
      </div>
      <div className="stat-grid">
        <Link to="/boxes" className="stat-card">
          <div className="stat-value">{boxes.length}</div>
          <div className="stat-label">Boxes</div>
        </Link>
        <Link to="/tubes" className="stat-card">
          <div className="stat-value">{tubes.length}</div>
          <div className="stat-label">Tubes</div>
        </Link>
        <Link to="/tubes?unassigned=true" className="stat-card">
          <div className="stat-value">{unassigned}</div>
          <div className="stat-label">Unassigned tubes</div>
        </Link>
      </div>

      <LeafletMap points={mappable} height={360} />

      <h2 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12, marginTop: mappable.length ? 24 : 0 }}>Recent boxes</h2>
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Barcode</th><th>Name</th><th className="col-mobile-hide">Location</th><th>Tubes</th></tr></thead>
            <tbody>
              {boxes.slice(0, 5).map(b => (
                <tr key={b.id} style={{ cursor: 'pointer' }} onClick={e => { if (!e.target.closest('a, button')) navigate(`/boxes/${b.id}`); }}>
                  <td><Link to={`/boxes/${b.id}`}><span className="barcode">{b.barcode}</span></Link></td>
                  <td>{b.name || <span style={{ color: 'var(--text2)' }}>—</span>}</td>
                  <td className="col-mobile-hide">{b.location_name || <span style={{ color: 'var(--text2)' }}>—</span>}</td>
                  <td>{b.tube_count}</td>
                </tr>
              ))}
              {boxes.length === 0 && <tr><td colSpan={4} className="empty">No boxes yet</td></tr>}
            </tbody>
          </table>
        </div>
      </div>

      <h2 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12 }}>Recent tubes</h2>
      <div className="card">
        <div className="table-wrap">
          <table>
            <thead><tr><th>Barcode</th><th>Box</th><th>Site</th><th>Type</th><th className="col-mobile-hide">Depth (cm)</th><th className="col-mobile-hide">Date</th></tr></thead>
            <tbody>
              {tubes.slice(0, 8).map(t => (
                <tr key={t.id} style={{ cursor: 'pointer' }} onClick={e => { if (!e.target.closest('a, button')) navigate(`/tubes/${t.id}`); }}>
                  <td><Link to={`/tubes/${t.id}`}><span className="barcode">{t.barcode}</span></Link></td>
                  <td>{t.box_barcode ? <Link to={`/boxes/${t.box_id}`}><span className="barcode">{t.box_barcode}</span></Link> : <span style={{ color: 'var(--text2)' }}>—</span>}</td>
                  <td>{t.site_name || '—'}</td>
                  <td>{t.sample_type || '—'}</td>
                  <td className="col-mobile-hide">{t.depth_cm ?? '—'}</td>
                  <td className="col-mobile-hide">{t.collection_date || '—'}</td>
                </tr>
              ))}
              {tubes.length === 0 && <tr><td colSpan={6} className="empty">No tubes yet</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
