import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { ToastProvider } from './components/Toast.jsx';
import { AuthProvider, useAuth } from './AuthContext.jsx';
import LoginPage from './components/LoginPage.jsx';
import Dashboard from './components/Dashboard.jsx';
import BoxList from './components/BoxList.jsx';
import BoxDetail from './components/BoxDetail.jsx';
import TubeList from './components/TubeList.jsx';
import TubeDetail from './components/TubeDetail.jsx';
import TubeForm from './components/TubeForm.jsx';
import ScanPage from './components/ScanPage.jsx';

function Nav() {
  const { user, logout } = useAuth();
  return (
    <nav className="sidebar">
      <div className="sidebar-title">Sediment Samples</div>
      <NavLink to="/" end>Overview</NavLink>
      <NavLink to="/scan">Scan barcode</NavLink>
      <NavLink to="/boxes">Boxes</NavLink>
      <NavLink to="/tubes">Tubes</NavLink>
      <div style={{ marginTop: 'auto', padding: '12px 16px', borderTop: '1px solid var(--border)' }}>
        <div style={{ fontSize: 12, color: 'var(--text2)', marginBottom: 6 }}>{user?.username}</div>
        <button className="btn btn-secondary btn-sm" onClick={logout} style={{ width: '100%' }}>
          Sign out
        </button>
      </div>
    </nav>
  );
}

function AppShell() {
  const { user } = useAuth();

  if (user === undefined) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: 'var(--text2)' }}>Loading…</p>
      </div>
    );
  }

  if (user === null) return <LoginPage />;

  return (
    <div className="layout">
      <Nav />
      <main className="main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/scan" element={<ScanPage />} />
          <Route path="/boxes" element={<BoxList />} />
          <Route path="/boxes/:id" element={<BoxDetail />} />
          <Route path="/tubes" element={<TubeList />} />
          <Route path="/tubes/new" element={<TubeForm mode="create" />} />
          <Route path="/tubes/:id" element={<TubeDetail />} />
          <Route path="/tubes/:id/edit" element={<TubeForm mode="edit" />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          <AppShell />
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
