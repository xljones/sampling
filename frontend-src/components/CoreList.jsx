import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api.js';
import { useAuth } from '../AuthContext.jsx';
import { useToast } from './Toast.jsx';
import BarcodeInput from './BarcodeInput.jsx';

export default function CoreList() {
  const { user } = useAuth();
  const ro = user?.is_readonly;
  const navigate = useNavigate();
  const toast = useToast();
  const [cores, setCores] = useState(null);
  const [adding, setAdding] = useState(false);
  const [newBarcode, setNewBarcode] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => { api.getCores().then(setCores); }, []);

  async function handleCreate(e) {
    e.preventDefault();
    if (!newBarcode.trim()) return;
    setCreating(true);
    try {
      const core = await api.createCore({ barcode: newBarcode.trim() });
      toast(`Core ${core.barcode} created`);
      navigate(`/cores/${core.id}`);
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setCreating(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Cores</h1>
        {!ro && (
          <button className="btn btn-primary" onClick={() => setAdding(v => !v)}>
            {adding ? 'Cancel' : '+ New core'}
          </button>
        )}
      </div>

      {adding && (
        <div className="card card-body mw-md mb-4">
          <form onSubmit={handleCreate}>
            <label className="mb-2 fw-600">New core barcode</label>
            <BarcodeInput
              value={newBarcode}
              onChange={setNewBarcode}
              placeholder="Scan or type barcode"
              autoFocus
            />
            <div className="btn-group mt-3">
              <button className="btn btn-success" disabled={creating || !newBarcode.trim()}>
                {creating ? 'Creating…' : 'Create core'}
              </button>
              <button type="button" className="btn btn-secondary" onClick={() => setAdding(false)}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="card">
        {cores === null && <p className="card-message">Loading…</p>}
        {cores?.length === 0 && <p className="card-message">No cores yet.</p>}
        {cores?.length > 0 && (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Barcode</th>
                  <th>Name</th>
                  <th>Source site</th>
                  <th>Collected</th>
                  <th>Type</th>
                  <th>Storage</th>
                  <th>Tubes</th>
                </tr>
              </thead>
              <tbody>
                {cores.map(c => (
                  <tr key={c.id} className="row-clickable" onClick={() => navigate(`/cores/${c.id}`)}>
                    <td>
                      <Link to={`/cores/${c.id}`} onClick={e => e.stopPropagation()}>
                        <span className="barcode">{c.barcode}</span>
                      </Link>
                    </td>
                    <td>{c.name || '—'}</td>
                    <td>{c.site_name || '—'}</td>
                    <td>{c.collection_date || '—'}</td>
                    <td>{c.sample_type || '—'}</td>
                    <td>{c.location_name || '—'}</td>
                    <td>{c.tube_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
