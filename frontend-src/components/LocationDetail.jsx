import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { api } from '../api.js';

export default function LocationDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loc, setLoc] = useState(null);

  useEffect(() => { api.getLocation(id).then(setLoc); }, [id]);

  if (!loc) return <p style={{ color: 'var(--text2)', padding: 32 }}>Loading…</p>;

  return (
    <div>
      <div className="page-header">
        <div>
          <div style={{ fontSize: 12, color: 'var(--text2)', marginBottom: 4 }}>
            <Link to="/locations">← Locations</Link>
          </div>
          <h1 className="page-title">{loc.name}</h1>
        </div>
      </div>

      <div className="card">
        <div className="table-wrap">
          <table>
            <thead><tr><th>Barcode</th><th>Name</th><th>Tubes</th><th>Notes</th></tr></thead>
            <tbody>
              {loc.boxes.map(b => (
                <tr key={b.id} style={{ cursor: 'pointer' }} onClick={() => navigate(`/boxes/${b.id}`)}>
                  <td><Link to={`/boxes/${b.id}`} onClick={e => e.stopPropagation()}><span className="barcode">{b.barcode}</span></Link></td>
                  <td>{b.name || '—'}</td>
                  <td>{b.tube_count}</td>
                  <td style={{ color: 'var(--text2)', fontSize: 13 }}>{b.notes || '—'}</td>
                </tr>
              ))}
              {loc.boxes.length === 0 && (
                <tr><td colSpan={4} className="empty">No boxes at this location</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
