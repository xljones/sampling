import { useEffect, useRef, useState } from 'react';
import { BrowserMultiFormatReader } from '@zxing/browser';

export default function CameraScanner({ onScan, onClose }) {
  const videoRef = useRef(null);
  const onScanRef = useRef(onScan);
  const [deviceId, setDeviceId] = useState(undefined);
  const [devices, setDevices] = useState([]);
  const [error, setError] = useState(null);
  // null = auto-detected, true/false = manual override
  const [flipped, setFlipped] = useState(null);
  const [autoFlip, setAutoFlip] = useState(false);

  useEffect(() => { onScanRef.current = onScan; }, [onScan]);

  useEffect(() => {
    if (!videoRef.current) return;

    if (!navigator.mediaDevices?.getUserMedia) {
      setError('Camera requires a secure connection (HTTPS). Try accessing the app via HTTPS.');
      return;
    }

    const reader = new BrowserMultiFormatReader();
    let controls = null;
    let cancelled = false;

    reader
      .decodeFromVideoDevice(deviceId, videoRef.current, (result) => {
        if (!cancelled && result) onScanRef.current(result.getText());
      })
      .then(c => {
        controls = c;
        // Detect facing mode from active track to auto-flip front cameras
        const track = videoRef.current?.srcObject?.getVideoTracks?.()[0];
        const facing = track?.getSettings?.()?.facingMode;
        if (!cancelled) setAutoFlip(facing === 'user' || facing === 'left');
        return BrowserMultiFormatReader.listVideoInputDevices();
      })
      .then(devs => {
        if (!cancelled) setDevices(devs);
      })
      .catch(e => {
        if (!cancelled) setError(e.message ?? 'Camera error');
      });

    return () => {
      cancelled = true;
      controls?.stop();
    };
  }, [deviceId]);

  const mirrored = flipped === null ? autoFlip : flipped;

  return (
    <div className="camera-wrap">
      {devices.length > 1 && (
        <select
          value={deviceId ?? ''}
          onChange={e => { setDeviceId(e.target.value); setFlipped(null); }}
          className="camera-select"
        >
          {devices.map(d => (
            <option key={d.deviceId} value={d.deviceId}>{d.label || d.deviceId}</option>
          ))}
        </select>
      )}
      {error
        ? <p className="text-danger">{error}</p>
        : (
          <div className="scanner-wrap">
            <video ref={videoRef} className={mirrored ? 'mirrored' : undefined} />
            <div className="scanner-overlay"><div className="scanner-box" /></div>
          </div>
        )
      }
      <div className="row-actions">
        <button
          className="btn btn-secondary btn-sm"
          onClick={() => setFlipped(f => !(f === null ? autoFlip : f))}
          title="Flip image horizontally"
        >
          ↔ Flip
        </button>
        <button className="btn btn-secondary btn-sm" onClick={onClose}>Close camera</button>
      </div>
    </div>
  );
}
