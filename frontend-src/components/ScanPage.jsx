import { useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api.js';
import BarcodeInput from './BarcodeInput.jsx';

export default function ScanPage() {
  const [barcode, setBarcode] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const lookup = useCallback(async (code) => {
    const b = (code ?? barcode).trim();
    if (!b) return;
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const data = await api.scan(b);
      setResult(data);
    } catch {
      setError(`No record found for barcode: ${b}`);
    } finally {
      setLoading(false);
    }
  }, [barcode]);

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Scan barcode</h1>
      </div>

      <div className="card card-body" style={{ maxWidth: 520, marginBottom: 24 }}>
        <p style={{ fontSize: 13, color: 'var(--text2)', marginBottom: 12 }}>
          Scan or type any barcode to look up a box or tube.
        </p>
        <BarcodeInput
          value={barcode}
          onChange={setBarcode}
          onSubmit={lookup}
          placeholder="Scan or type barcode…"
          autoFocus
        />
        <button
          className="btn btn-primary"
          style={{ marginTop: 10 }}
          onClick={() => lookup()}
          disabled={loading || !barcode.trim()}
        >
          {loading ? 'Looking up…' : 'Look up'}
        </button>
      </div>

      {error && (
        <div style={{ color: 'var(--danger)', background: '#fff0f0', border: '1px solid #f5c0c0', borderRadius: 'var(--radius)', padding: '12px 16px', maxWidth: 520 }}>
          {error}
          <div style={{ marginTop: 10, display: 'flex', gap: 8 }}>
            <Link to={`/boxes/new`} className="btn btn-secondary btn-sm">Register as box</Link>
            <Link to={`/tubes/new`} className="btn btn-secondary btn-sm">Register as tube</Link>
          </div>
        </div>
      )}

      {result && (
        <div className="card card-body" style={{ maxWidth: 520 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
            <span className={`badge ${result.type === 'box' ? 'badge-box' : 'badge-tube'}`}>
              {result.type}
            </span>
            <span className="barcode" style={{ fontSize: 14 }}>{result.data.barcode}</span>
          </div>

          {result.type === 'box' && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
              <Field label="Name" value={result.data.name} />
              <Field label="Location" value={result.data.location} />
              <Field label="Notes" value={result.data.notes} />
              <Field label="Created" value={result.data.created_at?.slice(0,10)} />
            </div>
          )}

          {result.type === 'tube' && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
              <Field label="Box" value={result.data.box_barcode} />
              <Field label="Site" value={result.data.site_name} />
              <Field label="Type" value={result.data.sample_type} />
              <Field label="Depth (cm)" value={result.data.depth_cm} />
              <Field label="Volume (mL)" value={result.data.volume_ml} />
              <Field label="Weight (g)" value={result.data.weight_g} />
              <Field label="Date" value={result.data.collection_date} />
              <Field label="Description" value={result.data.description} />
            </div>
          )}

          <div style={{ marginTop: 14 }}>
            <Link
              to={result.type === 'box' ? `/boxes/${result.data.id}` : `/tubes/${result.data.id}`}
              className="btn btn-primary btn-sm"
            >
              Open →
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

function Field({ label, value }) {
  return (
    <div>
      <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text2)', marginBottom: 2 }}>{label}</div>
      <div>{value ?? '—'}</div>
    </div>
  );
}
