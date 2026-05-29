import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api.js';
import { useAuth } from '../AuthContext.jsx';
import { useToast } from './Toast.jsx';

export default function LocationList() {
  const { user } = useAuth();
  const ro = user?.is_readonly;
  const [locations, setLocations] = useState([]);
  const [showAdd, setShowAdd] = useState(false);
  const [newName, setNewName] = useState('');
  const [saving, setSaving] = useState(false);
  const [editId, setEditId] = useState(null);
  const [editName, setEditName] = useState('');
  const toast = useToast();
  const navigate = useNavigate();

  useEffect(() => { api.getLocations().then(setLocations); }, []);

  async function handleAdd(e) {
    e.preventDefault();
    if (!newName.trim()) return;
    setSaving(true);
    try {
      const loc = await api.createLocation({ name: newName.trim() });
      setLocations(ls => [...ls, loc].sort((a, b) => a.name.localeCompare(b.name)));
      setNewName('');
      setShowAdd(false);
      toast('Location created');
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setSaving(false);
    }
  }

  function startEdit(loc) {
    setEditId(loc.id);
    setEditName(loc.name);
  }

  async function handleEdit(e) {
    e.preventDefault();
    if (!editName.trim()) return;
    setSaving(true);
    try {
      const updated = await api.updateLocation(editId, { name: editName.trim() });
      setLocations(ls => ls.map(l => l.id === editId ? { ...l, ...updated } : l).sort((a, b) => a.name.localeCompare(b.name)));
      setEditId(null);
      toast('Location renamed');
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(loc) {
    if (!confirm(`Delete location "${loc.name}"?`)) return;
    try {
      await api.deleteLocation(loc.id);
      setLocations(ls => ls.filter(l => l.id !== loc.id));
      toast('Location deleted');
    } catch (err) {
      toast(err.message, 'error');
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Locations</h1>
        {!ro && <button className="btn btn-primary" onClick={() => setShowAdd(v => !v)}>+ New location</button>}
      </div>

      {showAdd && (
        <div className="card card-body mb-6">
          <form onSubmit={handleAdd} className="inline-form">
            <input
              value={newName}
              onChange={e => setNewName(e.target.value)}
              placeholder="Location name, e.g. Oslo – Cold Store"
              autoFocus
              className="barcode-input"
            />
            <button className="btn btn-success" disabled={saving || !newName.trim()}>Save</button>
            <button type="button" className="btn btn-secondary" onClick={() => { setShowAdd(false); setNewName(''); }}>Cancel</button>
          </form>
        </div>
      )}

      <div className="card">
        <div className="table-wrap">
          <table>
            <thead><tr><th>Name</th><th>Boxes</th><th></th></tr></thead>
            <tbody>
              {locations.map(loc => (
                <tr
                  key={loc.id}
                  className={editId === loc.id ? '' : 'row-clickable'}
                  onClick={e => { if (editId === loc.id || e.target.closest('a, button, input, form')) return; navigate(`/locations/${loc.id}`); }}
                >
                  {editId === loc.id ? (
                    <td colSpan={3}>
                      <form onSubmit={handleEdit} className="inline-form">
                        <input value={editName} onChange={e => setEditName(e.target.value)} autoFocus className="input-sm" />
                        <button className="btn btn-success btn-sm" disabled={saving || !editName.trim()}>Save</button>
                        <button type="button" className="btn btn-secondary btn-sm" onClick={() => setEditId(null)}>Cancel</button>
                      </form>
                    </td>
                  ) : (
                    <>
                      <td>{loc.name}</td>
                      <td className="text-muted">{loc.box_count}</td>
                      <td className="col-shrink">
                        {!ro && (
                          <div className="row-actions">
                            <button className="btn btn-secondary btn-sm" onClick={() => startEdit(loc)}>Rename</button>
                            <button className="btn btn-danger btn-sm" onClick={() => handleDelete(loc)}>Delete</button>
                          </div>
                        )}
                      </td>
                    </>
                  )}
                </tr>
              ))}
              {locations.length === 0 && <tr><td colSpan={3} className="empty">No locations yet</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
