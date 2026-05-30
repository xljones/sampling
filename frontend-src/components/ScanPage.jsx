import { useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api.js';
import BarcodeInput from './BarcodeInput.jsx';
import RelativeTime from './RelativeTime.jsx';

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

      <div className="card card-body mw-md mb-6">
        <p className="text-muted mb-3">Scan or type any barcode to look up a box or tube.</p>
        <BarcodeInput
          value={barcode}
          onChange={setBarcode}
          onSubmit={lookup}
          placeholder="Scan or type barcode…"
          autoFocus
        />
        <button
          className="btn btn-primary mt-3"
          onClick={() => lookup()}
          disabled={loading || !barcode.trim()}
        >
          {loading ? 'Looking up…' : 'Look up'}
        </button>
      </div>

      {error && (
        <div className="alert-error mw-md">
          {error}
          <div className="btn-group mt-3">
            <Link to={`/boxes?add=1&barcode=${encodeURIComponent(barcode.trim())}`} className="btn btn-secondary btn-sm">Register as box</Link>
            <Link to={`/tubes/new?barcode=${encodeURIComponent(barcode.trim())}`} className="btn btn-secondary btn-sm">Register as tube</Link>
          </div>
        </div>
      )}

      {result && (
        <div className="card card-body mw-md">
          <div className="scan-badge-row">
            <span className={`badge ${result.type === 'box' ? 'badge-box' : result.type === 'core' ? 'badge-core' : 'badge-tube'}`}>
              {result.type}
            </span>
            <span className="barcode">{result.data.barcode}</span>
          </div>

          {result.type === 'box' && (
            <div className="scan-result-grid">
              <Field label="Name" value={result.data.name} />
              <Field label="Location" value={result.data.location} />
              <Field label="Notes" value={result.data.notes} />
              <Field label="Created" value={<RelativeTime value={result.data.created_at} />} />
            </div>
          )}

          {result.type === 'tube' && (
            <div className="scan-result-grid">
              <Field label="Box" value={result.data.box_barcode} />
              <Field label="Core" value={result.data.core_barcode} />
              <Field label="Site" value={result.data.site_name} />
              <Field label="Type" value={result.data.sample_type} />
              <Field label="Depth (cm)" value={result.data.depth_cm} />
              <Field label="Volume (mL)" value={result.data.volume_ml} />
              <Field label="Weight (g)" value={result.data.weight_g} />
              <Field label="Date" value={result.data.sample_date} />
              <Field label="Description" value={result.data.description} />
            </div>
          )}

          {result.type === 'core' && (
            <div className="scan-result-grid">
              <Field label="Name" value={result.data.name} />
              <Field label="Site" value={result.data.site_name} />
              <Field label="Type" value={result.data.sample_type} />
              <Field label="Collector" value={result.data.collector} />
              <Field label="Storage" value={result.data.location_name} />
              <Field label="Date" value={result.data.collection_date} />
            </div>
          )}

          <div className="mt-4">
            <Link
              to={result.type === 'box' ? `/boxes/${result.data.id}` : result.type === 'core' ? `/cores/${result.data.id}` : `/tubes/${result.data.id}`}
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
      <div className="scan-field-label">{label}</div>
      <div>{value ?? '—'}</div>
    </div>
  );
}
