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
    <div className="camera-wrap">
      <div className="inline-form-sm">
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={e => onChange(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && onSubmit) { e.preventDefault(); onSubmit(value); } }}
          placeholder={placeholder}
          autoFocus={autoFocus}
          autoComplete="off"
          data-1p-ignore
          className="barcode-input"
        />
        <button
          type="button"
          className="btn btn-secondary"
          onClick={() => setCameraOpen(v => !v)}
          title="Open camera scanner"
        >
          <img src="/camera.svg" width="16" height="16" alt="" />
        </button>
      </div>
      {cameraOpen && (
        <Suspense fallback={<p className="text-muted text-sm">Loading camera…</p>}>
          <CameraScanner onScan={handleScan} onClose={() => setCameraOpen(false)} />
        </Suspense>
      )}
    </div>
  );
}
