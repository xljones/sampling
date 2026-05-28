import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { api } from '../api.js';
import { useToast } from './Toast.jsx';

export default function TubeDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const [tube, setTube] = useState(null);

  useEffect(() => { api.getTube(id).then(setTube); }, [id]);

  async function handleDelete() {
    if (!confirm('Delete this tube?')) return;
    await api.deleteTube(id);
    toast('Tube deleted');
    navigate('/tubes');
  }

  if (!tube) return <p style={{ color: 'var(--text2)', padding: 32 }}>Loading…</p>;

  const fields = [
    ['Barcode', <span key="barcode" className="barcode">{tube.barcode}</span>],
    ['Box', tube.box_barcode ? <Link to={`/boxes/${tube.box_id}`}><span className="barcode">{tube.box_barcode}</span>{tube.box_name ? ` — ${tube.box_name}` : ''}</Link> : '—'],
    ['Collection date', tube.collection_date || '—'],
    ['Site', tube.site_name || '—'],
    ['Sample type', tube.sample_type || '—'],
    ['Depth in core', tube.depth_cm != null ? `${tube.depth_cm} cm` : '—'],
    ['Volume', tube.volume_ml != null ? `${tube.volume_ml} mL` : '—'],
    ['Weight', tube.weight_g != null ? `${tube.weight_g} g` : '—'],
    ['Latitude', tube.latitude ?? '—'],
    ['Longitude', tube.longitude ?? '—'],
    ['Description', tube.description || '—'],
    ['Created', tube.created_at?.slice(0, 10)],
    ['Updated', tube.updated_at?.slice(0, 10)],
  ];

  return (
    <div>
      <div className="page-header">
        <div>
          <div style={{ fontSize: 12, color: 'var(--text2)', marginBottom: 4 }}><Link to="/tubes">← Tubes</Link></div>
          <h1 className="page-title"><span className="barcode" style={{ fontSize: 18 }}>{tube.barcode}</span></h1>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <Link to={`/tubes/${id}/edit`} className="btn btn-secondary">Edit</Link>
          <button className="btn btn-danger" onClick={handleDelete}>Delete</button>
        </div>
      </div>

      <div className="card card-body">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px 24px' }}>
          {fields.map(([label, value]) => (
            <div key={label}>
              <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text2)', marginBottom: 2 }}>{label}</div>
              <div>{value}</div>
            </div>
          ))}
        </div>
      </div>

      {tube.latitude != null && tube.longitude != null && (
        <div className="card" style={{ marginTop: 16, overflow: 'hidden' }}>
          <iframe
            title="Sample location"
            width="100%"
            height="320"
            style={{ display: 'block', border: 0 }}
            src={`https://www.openstreetmap.org/export/embed.html?bbox=${tube.longitude - 0.05},${tube.latitude - 0.05},${tube.longitude + 0.05},${tube.latitude + 0.05}&layer=mapnik&marker=${tube.latitude},${tube.longitude}`}
          />
          <div style={{ padding: '6px 12px', fontSize: 11, color: 'var(--text2)', borderTop: '1px solid var(--border)' }}>
            <a
              href={`https://www.openstreetmap.org/?mlat=${tube.latitude}&mlon=${tube.longitude}#map=13/${tube.latitude}/${tube.longitude}`}
              target="_blank"
              rel="noreferrer"
            >
              View on OpenStreetMap ↗
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
