// Layout component with navigation
import { Link, Outlet, NavLink } from 'react-router-dom'
import './Layout.css'

export default function Layout() {
  return (
    <div className="layout">
      <header className="header">
        <div className="header-content">
          <Link to="/" className="logo">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <rect width="32" height="32" rx="6" fill="#2563eb"/>
              <path d="M8 16L14 22L24 10" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <span>signal-hub</span>
          </Link>
          <nav className="nav">
            <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              Dashboard
            </NavLink>
            <NavLink to="/analyze" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              Issue Analyzer
            </NavLink>
            <NavLink to="/health" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              Health
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="main">
        <Outlet />
      </main>
      <footer className="footer">
        <p>signal-hub-alan-vo &copy; 2026 Alan Vo alanvo@gmail.com | AI & Machine Learning</p>
      </footer>
    </div>
  )
}