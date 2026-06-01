import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api.js';
import LeafletMap from './LeafletMap.jsx';
import { SkeletonRows } from './Skeleton.jsx';

export default function Dashboard() {
  const [boxes, setBoxes] = useState(null);
  const [tubes, setTubes] = useState(null);
  const [cores, setCores] = useState(null);

  useEffect(() => {
    api.getBoxes().then(setBoxes).catch(() => {});
    api.getTubes().then(setTubes).catch(() => {});
    api.getCores().then(setCores).catch(() => {});
  }, []);

  const navigate = useNavigate();
  const unassigned = tubes ? tubes.filter(t => !t.box_id).length : null;

  const CORE_COLOR = '#f97316';
  const TUBE_COLOR = '#3b82f6';
  const TUBE_OWN_COLOR = '#22c55e';

  const mappable = [
    ...(cores ?? [])
      .filter(c => c.latitude != null && c.longitude != null)
      .map(c => ({ lat: c.latitude, lng: c.longitude, label: c.barcode + (c.site_name ? ` — ${c.site_name}` : ''), url: `/cores/${c.id}`, color: CORE_COLOR })),
    ...(tubes ?? [])
      .filter(t => t.core_id == null && t.latitude != null && t.longitude != null)
      .map(t => ({ lat: t.latitude, lng: t.longitude, label: t.barcode + (t.site_name ? ` — ${t.site_name}` : ''), url: `/tubes/${t.id}`, color: TUBE_COLOR })),
    ...(tubes ?? [])
      .filter(t => t.core_id != null && t.latitude != null && t.longitude != null)
      .map(t => ({ lat: t.latitude, lng: t.longitude, label: t.barcode + (t.site_name ? ` — ${t.site_name}` : ''), url: `/tubes/${t.id}`, color: TUBE_OWN_COLOR })),
  ];

  const legend = [
    ...((cores ?? []).some(c => c.latitude != null) ? [{ color: CORE_COLOR, label: 'Cores' }] : []),
    ...((tubes ?? []).some(t => t.core_id == null && t.latitude != null) ? [{ color: TUBE_COLOR, label: 'Tubes (no core)' }] : []),
    ...((tubes ?? []).some(t => t.core_id != null && t.latitude != null) ? [{ color: TUBE_OWN_COLOR, label: 'Tubes (own coords)' }] : []),
  ];

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
      </div>
      <div className="stat-grid">
        <Link to="/cores" className="stat-card">
          <div className="stat-value">{cores === null ? <span className="skeleton-line" style={{ width: 48, height: 34, display: 'inline-block' }} /> : cores.length}</div>
          <div className="stat-label">Cores</div>
        </Link>
        <Link to="/boxes" className="stat-card">
          <div className="stat-value">{boxes === null ? <span className="skeleton-line" style={{ width: 48, height: 34, display: 'inline-block' }} /> : boxes.length}</div>
          <div className="stat-label">Boxes</div>
        </Link>
        <Link to="/tubes" className="stat-card">
          <div className="stat-value">{tubes === null ? <span className="skeleton-line" style={{ width: 48, height: 34, display: 'inline-block' }} /> : tubes.length}</div>
          <div className="stat-label">Tubes</div>
        </Link>
        <Link to="/tubes?unassigned=true" className="stat-card">
          <div className="stat-value">{unassigned === null ? <span className="skeleton-line" style={{ width: 48, height: 34, display: 'inline-block' }} /> : unassigned}</div>
          <div className="stat-label">Unassigned tubes</div>
        </Link>
      </div>

      <LeafletMap points={mappable} height={360} legend={legend} />

      <h2 className={`section-title mb-3${mappable.length ? ' mt-6' : ''}`}>Recent cores</h2>
      <div className="card mb-6">
        <div className="table-wrap">
          <table>
            <thead><tr><th>Barcode</th><th>Name</th><th>Site</th><th className="col-mobile-hide">Type</th><th>Tubes</th></tr></thead>
            <tbody>
              {cores === null
                ? <SkeletonRows cols={['90px', '30%', '25%', '20%', '40px']} rows={3} />
                : cores.slice(0, 5).map(c => (
                  <tr key={c.id} className="row-clickable" onClick={e => { if (!e.target.closest('a, button')) navigate(`/cores/${c.id}`); }}>
                    <td><Link to={`/cores/${c.id}`}><span className="barcode">{c.barcode}</span></Link></td>
                    <td>{c.name || <span className="text-muted">—</span>}</td>
                    <td>{c.site_name || <span className="text-muted">—</span>}</td>
                    <td className="col-mobile-hide">{c.sample_type || <span className="text-muted">—</span>}</td>
                    <td>{c.tube_count}</td>
                  </tr>
                ))
              }
              {cores !== null && cores.length === 0 && <tr><td colSpan={5} className="empty">No cores yet</td></tr>}
            </tbody>
          </table>
        </div>
      </div>

      <h2 className="section-title mb-3">Recent boxes</h2>
      <div className="card mb-6">
        <div className="table-wrap">
          <table>
            <thead><tr><th>Barcode</th><th>Name</th><th className="col-mobile-hide">Storage location</th><th>Tubes</th></tr></thead>
            <tbody>
              {boxes === null
                ? <SkeletonRows cols={['90px', '40%', '30%', '40px']} rows={3} />
                : boxes.slice(0, 5).map(b => (
                  <tr key={b.id} className="row-clickable" onClick={e => { if (!e.target.closest('a, button')) navigate(`/boxes/${b.id}`); }}>
                    <td><Link to={`/boxes/${b.id}`}><span className="barcode">{b.barcode}</span></Link></td>
                    <td>{b.name || <span className="text-muted">—</span>}</td>
                    <td className="col-mobile-hide">{b.location_name || <span className="text-muted">—</span>}</td>
                    <td>{b.tube_count}</td>
                  </tr>
                ))
              }
              {boxes !== null && boxes.length === 0 && <tr><td colSpan={4} className="empty">No boxes yet</td></tr>}
            </tbody>
          </table>
        </div>
      </div>

      <h2 className="section-title mb-3">Recent tubes</h2>
      <div className="card">
        <div className="table-wrap">
          <table>
            <thead><tr><th>Barcode</th><th>Box</th><th>Site</th><th>Type</th><th className="col-mobile-hide">Depth (cm)</th><th className="col-mobile-hide">Date</th></tr></thead>
            <tbody>
              {tubes === null
                ? <SkeletonRows cols={['90px', '80px', '30%', '20%', '50px', '90px']} rows={3} />
                : tubes.slice(0, 8).map(t => (
                  <tr key={t.id} className="row-clickable" onClick={e => { if (!e.target.closest('a, button')) navigate(`/tubes/${t.id}`); }}>
                    <td><Link to={`/tubes/${t.id}`}><span className="barcode">{t.barcode}</span></Link></td>
                    <td>{t.box_barcode ? <Link to={`/boxes/${t.box_id}`}><span className="barcode">{t.box_barcode}</span></Link> : <span className="text-muted">—</span>}</td>
                    <td>{t.site_name || '—'}</td>
                    <td>{t.sample_type || '—'}</td>
                    <td className="col-mobile-hide">{t.depth_cm ?? '—'}</td>
                    <td className="col-mobile-hide">{t.sample_date || '—'}</td>
                  </tr>
                ))
              }
              {tubes !== null && tubes.length === 0 && <tr><td colSpan={6} className="empty">No tubes yet</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
