import { useState, useRef, useCallback, lazy, Suspense } from 'react';

const CameraScanner = lazy(() => import('./CameraScanner.jsx'));

export default function BarcodeInput({ value, onChange, onSubmit, placeholder = 'Scan or type barcode…', autoFocus }) {
  const [cameraOpen, setCameraOpen] = useState(false);
  const inputRef = useRef(null);

  const handleScan = useCallback((barcode) => {
    onChange(barcode);
    setCameraOpen(false);
    if (onSubmit) onSubmit(barcode);
    else setTimeout(() => inputRef.current?.focus(), 50);
  }, [onChange, onSubmit]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <div style={{ display: 'flex', gap: 6 }}>
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={e => onChange(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && onSubmit) { e.preventDefault(); onSubmit(value); } }}
          placeholder={placeholder}
          autoFocus={autoFocus}
          style={{ flex: 1, padding: '8px 10px', border: '1px solid var(--border)', borderRadius: 'var(--radius)', fontSize: 13 }}
        />
        <button
          type="button"
          className="btn btn-secondary"
          onClick={() => setCameraOpen(v => !v)}
          title="Open camera scanner"
        >
          📷
        </button>
      </div>
      {cameraOpen && (
        <Suspense fallback={<p style={{ fontSize: 13, color: 'var(--text2)' }}>Loading camera…</p>}>
          <CameraScanner onScan={handleScan} onClose={() => setCameraOpen(false)} />
        </Suspense>
      )}
    </div>
  );
}
