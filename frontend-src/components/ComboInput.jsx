import { useState, useRef, useCallback, lazy, Suspense, useEffect } from 'react';

const CameraScanner = lazy(() => import('./CameraScanner.jsx'));

export default function ComboInput({ value, onChange, options = [], placeholder, autoFocus }) {
  const [open, setOpen] = useState(false);
  const [cameraOpen, setCameraOpen] = useState(false);
  const inputRef = useRef(null);
  const wrapRef = useRef(null);

  const filtered = value
    ? options.filter(opt => {
        const label = opt.barcode + (opt.name ? ` — ${opt.name}` : '');
        return label.toLowerCase().includes(value.toLowerCase());
      })
    : options;

  const handleScan = useCallback((barcode) => {
    onChange(barcode);
    setCameraOpen(false);
    setOpen(false);
  }, [onChange]);

  useEffect(() => {
    function onOutside(e) {
      if (wrapRef.current && !wrapRef.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener('mousedown', onOutside);
    return () => document.removeEventListener('mousedown', onOutside);
  }, []);

  return (
    <div className="camera-wrap">
      <div className="combo-wrap" ref={wrapRef}>
        <div className="inline-form-sm">
          <input
            ref={inputRef}
            type="text"
            value={value}
            onChange={e => { onChange(e.target.value); setOpen(true); }}
            onFocus={() => { if (value) setOpen(true); }}
            onKeyDown={e => { if (e.key === 'Escape') setOpen(false); }}
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
        {open && filtered.length > 0 && (
          <ul className="combo-dropdown">
            {filtered.map(opt => (
              <li key={opt.id}>
                <button
                  type="button"
                  className="combo-option"
                  onMouseDown={e => {
                    e.preventDefault();
                    onChange(opt.barcode);
                    setOpen(false);
                    inputRef.current?.focus();
                  }}
                >
                  {opt.barcode}{opt.name ? ` — ${opt.name}` : ''}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
      {cameraOpen && (
        <Suspense fallback={<p className="text-muted text-sm">Loading camera…</p>}>
          <CameraScanner onScan={handleScan} onClose={() => setCameraOpen(false)} />
        </Suspense>
      )}
    </div>
  );
}
