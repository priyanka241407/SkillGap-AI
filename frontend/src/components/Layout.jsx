import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { BrainCircuit, LayoutDashboard, FileText, BarChart2, BookOpen, Map, History, LogOut, User, ChevronRight } from "lucide-react";

/**
 * Sidebar navigation shown inside the authenticated app layout.
 * Links update based on current route (active state).
 */
export function Sidebar() {
  const { user, logoutUser } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const isActive = (path) => location.pathname === path;

  const handleLogout = () => {
    logoutUser();
    navigate("/");
  };

  const navLinks = [
    { to: "/dashboard", icon: <LayoutDashboard size={18} />, label: "Dashboard" },
    { to: "/resume", icon: <FileText size={18} />, label: "Resume & Skills" },
    { to: "/analysis", icon: <BarChart2 size={18} />, label: "Skill Gap Analysis" },
    { to: "/courses", icon: <BookOpen size={18} />, label: "Courses" },
    { to: "/roadmap", icon: <Map size={18} />, label: "My Roadmap" },
    { to: "/history", icon: <History size={18} />, label: "History" },
    { to: "/profile", icon: <User size={18} />, label: "Profile" },
  ];

  return (
    <aside className="sidebar">
      {/* User greeting */}
      <div style={{ marginBottom: "24px", padding: "12px 14px", background: "rgba(99,102,241,.06)", borderRadius: "var(--radius-sm)" }}>
        <p style={{ fontSize: "12px", color: "var(--text-muted)", marginBottom: "2px" }}>Signed in as</p>
        <p style={{ fontSize: "14px", fontWeight: "700", color: "var(--primary)" }}>{user?.name}</p>
      </div>

      <span className="sidebar-section-label">Main Menu</span>
      <nav className="sidebar-nav">
        {navLinks.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className={`sidebar-link ${isActive(link.to) ? "active" : ""}`}
          >
            {link.icon}
            {link.label}
          </Link>
        ))}
      </nav>

      <div style={{ marginTop: "auto", paddingTop: "24px", borderTop: "1px solid var(--border)", marginTop: "32px" }}>
        <button className="sidebar-link" onClick={handleLogout} style={{ color: "var(--danger)" }}>
          <LogOut size={18} />
          Logout
        </button>
      </div>
    </aside>
  );
}

/**
 * Top Navbar - shown on landing page and marketing pages.
 */
export function Navbar() {
  const { user } = useAuth();
  const location = useLocation();

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-logo">
          <BrainCircuit size={26} />
          SkillGap<span> AI</span>
        </Link>

        <ul className="navbar-links">
          <li><a href="#features">Features</a></li>
          <li><a href="#how-it-works">How It Works</a></li>
          <li><a href="#about">About</a></li>
        </ul>

        <div className="navbar-actions">
          {user ? (
            <Link to="/dashboard" className="btn btn-primary btn-sm">
              <LayoutDashboard size={15} /> Dashboard
            </Link>
          ) : (
            <>
              <Link to="/login" className="btn btn-ghost btn-sm">Login</Link>
              <Link to="/register" className="btn btn-primary btn-sm">Get Started</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

/**
 * App layout for authenticated pages (sidebar + main content).
 */
export function AppLayout({ children }) {
  return (
    <>
      <AppNavbar />
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">{children}</main>
      </div>
    </>
  );
}

/**
 * Simplified navbar for authenticated pages.
 */
function AppNavbar() {
  const { user, logoutUser } = useAuth();
  const navigate = useNavigate();

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/dashboard" className="navbar-logo">
          <BrainCircuit size={24} />
          SkillGap<span> AI</span>
        </Link>
        <div className="navbar-actions">
          <span style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
            👋 {user?.name}
          </span>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => { logoutUser(); navigate("/"); }}
          >
            <LogOut size={14} /> Logout
          </button>
        </div>
      </div>
    </nav>
  );
}

/**
 * Spinner shown during loading states.
 */
export function Spinner({ text = "Loading..." }) {
  return (
    <div className="loading-page">
      <div className="spinner" />
      <p>{text}</p>
    </div>
  );
}

/**
 * Step indicator for the analysis flow (Resume → Test → Analysis).
 */
export function StepIndicator({ steps, currentStep }) {
  return (
    <div className="step-indicator">
      {steps.map((step, i) => (
        <div key={i} className="step" style={{ display: "flex", alignItems: "center" }}>
          <div className="step-inner">
            <div className={`step-circle ${i < currentStep ? "done" : i === currentStep ? "active" : ""}`}>
              {i < currentStep ? "✓" : i + 1}
            </div>
            <span className={`step-label ${i === currentStep ? "active" : i < currentStep ? "done" : ""}`}>
              {step}
            </span>
          </div>
          {i < steps.length - 1 && <div className="step-connector" style={{ margin: "0 4px", marginBottom: "20px" }} />}
        </div>
      ))}
    </div>
  );
}

/**
 * Skill tag that can optionally have a remove button.
 */
export function SkillTag({ skill, variant = "", onRemove }) {
  return (
    <span className={`skill-tag ${variant}`}>
      {skill}
      {onRemove && (
        <button
          onClick={() => onRemove(skill)}
          style={{ background: "none", border: "none", cursor: "pointer", padding: "0", lineHeight: 1, color: "inherit", marginLeft: "2px" }}
          title={`Remove ${skill}`}
        >
          ×
        </button>
      )}
    </span>
  );
}

/**
 * Progress bar component.
 */
export function ProgressBar({ value, max = 100, label, variant = "" }) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  return (
    <div className="progress-container">
      {label && (
        <div className="progress-label">
          <span>{label}</span>
          <span>{Math.round(pct)}%</span>
        </div>
      )}
      <div className="progress-bar">
        <div className={`progress-fill ${variant}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

/**
 * Protected Route - redirects to login if not authenticated.
 */
export function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  const navigate = useNavigate();

  if (loading) return <Spinner />;
  if (!user) {
    navigate("/login");
    return null;
  }
  return children;
}
