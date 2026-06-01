import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { useState } from 'react';
import { ToastProvider } from './components/Toast.jsx';
import BuildInfo from './components/BuildInfo.jsx';
import { AuthProvider, useAuth } from './AuthContext.jsx';
import LoginPage from './components/LoginPage.jsx';
import Dashboard from './components/Dashboard.jsx';
import BoxList from './components/BoxList.jsx';
import BoxDetail from './components/BoxDetail.jsx';
import TubeList from './components/TubeList.jsx';
import TubeDetail from './components/TubeDetail.jsx';
import TubeForm from './components/TubeForm.jsx';
import ScanPage from './components/ScanPage.jsx';
import CoreList from './components/CoreList.jsx';
import CoreDetail from './components/CoreDetail.jsx';
import CoreForm from './components/CoreForm.jsx';
import LocationList from './components/LocationList.jsx';
import LocationDetail from './components/LocationDetail.jsx';
import UserList from './components/UserList.jsx';
import AccountPage from './components/AccountPage.jsx';

function Nav() {
  const { user, logout } = useAuth();

  return (
    <nav className="sidebar">
      <img src="/dna-icon.svg" className="sidebar-logo" alt="DNA icon" />
      <div className="sidebar-title">Dirt Nap</div>
      <div className="sidebar-tagline">The samples are at rest</div>
      <NavLink to="/" end>Overview</NavLink>
      <NavLink to="/scan">Scan barcode</NavLink>
      <hr className="sidebar-divider" />
      <NavLink to="/cores">Cores</NavLink>
      <NavLink to="/boxes">Boxes</NavLink>
      <NavLink to="/tubes">Tubes</NavLink>
      <NavLink to="/locations">Storage locations</NavLink>
      <div className="mt-auto">
        <div className="sidebar-user">
          <div className="meta">{user?.username}</div>
          {user?.is_admin && <div className="meta dim">admin</div>}
          {user?.is_readonly && <div className="meta dim">read-only</div>}
        </div>
        {user?.is_admin && <NavLink to="/users" className="sidebar-nav-btn">Users</NavLink>}
        <NavLink to="/account" className="sidebar-nav-btn">Change password</NavLink>
        <button className="sidebar-nav-btn text-danger" onClick={logout}>Sign out</button>
        <div className="sidebar-grass-wrap">
          <div className="sidebar-grass" aria-hidden="true" />
          <BuildInfo className="sidebar-version" />
        </div>
      </div>
    </nav>
  );
}

function BottomNav() {
  const { user, logout } = useAuth();
  const [moreOpen, setMoreOpen] = useState(false);
  const closeMore = () => setMoreOpen(false);

  return (
    <>
      {moreOpen && (
        <>
          <div className="bottom-nav-backdrop" onClick={closeMore} />
          <div className="bottom-nav-more">
            <NavLink to="/cores" className="sidebar-nav-btn" onClick={closeMore}>Cores</NavLink>
            <NavLink to="/locations" className="sidebar-nav-btn" onClick={closeMore}>Storage locations</NavLink>
            <div className="sidebar-user">
              <div className="text-sm fw-600">{user?.username}</div>
              {user?.is_admin && <div className="meta mt-2">admin</div>}
              {user?.is_readonly && <div className="meta mt-2">read-only</div>}
            </div>
            {user?.is_admin && (
              <NavLink to="/users" className="sidebar-nav-btn" onClick={closeMore}>Users</NavLink>
            )}
            <NavLink to="/account" className="sidebar-nav-btn" onClick={closeMore}>Change password</NavLink>
            <button className="sidebar-nav-btn text-danger" onClick={logout}>Sign out</button>
            <BuildInfo className="sidebar-version" />
          </div>
        </>
      )}
      <nav className="bottom-nav">
        <NavLink to="/" end className="bottom-nav-item" onClick={closeMore}>Overview</NavLink>
        <NavLink to="/scan" className="bottom-nav-item" onClick={closeMore}>Scan</NavLink>
        <NavLink to="/boxes" className="bottom-nav-item" onClick={closeMore}>Boxes</NavLink>
        <NavLink to="/tubes" className="bottom-nav-item" onClick={closeMore}>Tubes</NavLink>
        <button className={`bottom-nav-item${moreOpen ? ' active' : ''}`} onClick={() => setMoreOpen(v => !v)}>
          More
        </button>
      </nav>
    </>
  );
}

function AppShell() {
  const { user } = useAuth();

  if (user === undefined) {
    return (
      <div className="page-center">
        <p className="text-muted">Loading…</p>
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
          <Route path="/cores" element={<CoreList />} />
          <Route path="/cores/new" element={<CoreForm />} />
          <Route path="/cores/:id" element={<CoreDetail />} />
          <Route path="/locations" element={<LocationList />} />
          <Route path="/locations/:id" element={<LocationDetail />} />
          {user.is_admin && <Route path="/users" element={<UserList />} />}
          <Route path="/account" element={<AccountPage />} />
        </Routes>
      </main>
      <BottomNav />
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
