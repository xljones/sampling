import { useState, useEffect } from 'react';
import { api } from '../api.js';
import RelativeTime from './RelativeTime.jsx';

function SkeletonCard() {
  return (
    <div className="card card-body mb-6">
      <div className="form-grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        <div>
          <div className="skeleton-line" style={{ width: 60, height: 11, marginBottom: 10 }} />
          <div className="skeleton-line" style={{ width: '100%', height: 8, borderRadius: 4, marginBottom: 8 }} />
          <div className="skeleton-line" style={{ width: 120, height: 12 }} />
        </div>
        <div>
          <div className="skeleton-line" style={{ width: 60, height: 11, marginBottom: 10 }} />
          <div className="skeleton-line" style={{ width: '80%', height: 14, marginBottom: 8 }} />
          <div className="skeleton-line" style={{ width: '60%', height: 14 }} />
        </div>
      </div>
    </div>
  );
}

function CpuBar({ used, limit }) {
  const pct = limit > 0 ? Math.min(100, (used / limit) * 100) : 0;
  const color = pct > 80 ? '#e74c3c' : pct > 50 ? '#f39c12' : '#27ae60';
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
        <span className="text-sm">{pct.toFixed(1)}% used</span>
        <span className="text-sm text-muted">{used.toFixed(1)}s / {limit}s daily</span>
      </div>
      <div style={{ background: 'var(--border)', borderRadius: 4, height: 8, overflow: 'hidden' }}>
        <div style={{ width: `${pct}%`, background: color, height: '100%', borderRadius: 4, transition: 'width 0.3s' }} />
      </div>
    </div>
  );
}

export default function PythonAnywhereStats() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getPythonAnywhereStats()
      .then(setStats)
      .catch(err => setError(err.message));
  }, []);

  if (error) {
    return (
      <div className="card card-body mb-6">
        <h2 className="section-title">PythonAnywhere</h2>
        <p className="text-sm text-danger">{error}</p>
      </div>
    );
  }

  if (!stats) return <SkeletonCard />;

  if (!stats.configured) {
    return (
      <div className="card card-body mb-6">
        <h2 className="section-title">PythonAnywhere</h2>
        <p className="text-sm text-muted">
          Stats unavailable — set <code>PA_API_TOKEN</code> and <code>PA_USERNAME</code> environment variables to enable.
        </p>
      </div>
    );
  }

  if (stats.error) {
    return (
      <div className="card card-body mb-6">
        <h2 className="section-title">PythonAnywhere</h2>
        <p className="text-sm text-danger">{stats.error}</p>
      </div>
    );
  }

  const { cpu, webapps } = stats;

  return (
    <div className="card card-body mb-6">
      <h2 className="section-title">PythonAnywhere</h2>

      <div className="form-grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        <div>
          <div className="scan-field-label mb-2">Daily CPU</div>
          <CpuBar used={cpu.daily_cpu_total_usage_seconds} limit={cpu.daily_cpu_limit_seconds} />
          {cpu.next_reset_time && (
            <p className="text-sm text-muted mt-2">
              Resets <RelativeTime value={cpu.next_reset_time} />
            </p>
          )}
        </div>

        {webapps && webapps.length > 0 && (
          <div>
            <div className="scan-field-label mb-2">Web apps</div>
            {webapps.map(app => (
              <div key={app.id} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                <span
                  style={{
                    display: 'inline-block', width: 8, height: 8, borderRadius: '50%',
                    background: app.enabled ? '#27ae60' : '#e74c3c', flexShrink: 0,
                  }}
                />
                <span className="text-sm">{app.domain_name}</span>
                <span className="text-sm text-muted">Python {app.python_version}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
