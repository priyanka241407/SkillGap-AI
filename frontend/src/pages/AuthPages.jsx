import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { BrainCircuit } from "lucide-react";
import toast from "react-hot-toast";
import { login, register } from "../services/api";
import { useAuth } from "../context/AuthContext";

export function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { loginUser } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) return toast.error("Please fill in all fields.");

    setLoading(true);
    try {
      const res = await login({ email, password });
      loginUser(res.data.token, res.data.user);
      toast.success("Welcome back!");
      navigate("/dashboard");
    } catch (err) {
      if (!err.response) {
        toast.error("Cannot connect to server. Please make sure the backend is running on port 5000.");
      } else {
        toast.error(err.response?.data?.error || "Login failed.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">
          <BrainCircuit size={32} style={{ display: "inline", verticalAlign: "middle", marginRight: "8px" }} />
          SkillGap AI
        </div>
        <h2 className="auth-title">Welcome Back</h2>
        <p className="auth-subtitle">Log in to your account to continue</p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              type="email"
              className="form-input"
              placeholder="student@college.edu"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <button type="submit" className="btn btn-primary w-full justify-center" disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        <div className="auth-switch">
          Don't have an account? <Link to="/register">Create one</Link>
        </div>
      </div>
    </div>
  );
}

export function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { loginUser } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name || !email || !password) return toast.error("Please fill in all fields.");
    if (password.length < 6) return toast.error("Password must be at least 6 characters.");

    setLoading(true);
    try {
      const res = await register({ name, email, password });
      loginUser(res.data.token, res.data.user);
      toast.success("Account created successfully!");
      navigate("/profile"); // Direct to profile to set career goal
    } catch (err) {
      if (!err.response) {
        toast.error("Cannot connect to server. Please make sure the backend is running on port 5000.");
      } else {
        toast.error(err.response?.data?.error || "Registration failed.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">
          <BrainCircuit size={32} style={{ display: "inline", verticalAlign: "middle", marginRight: "8px" }} />
          SkillGap AI
        </div>
        <h2 className="auth-title">Create Account</h2>
        <p className="auth-subtitle">Start your journey to your dream job</p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input
              type="text"
              className="form-input"
              placeholder="John Doe"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              type="email"
              className="form-input"
              placeholder="student@college.edu"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <button type="submit" className="btn btn-primary w-full justify-center" disabled={loading}>
            {loading ? "Creating Account..." : "Sign Up"}
          </button>
        </form>

        <div className="auth-switch">
          Already have an account? <Link to="/login">Login here</Link>
        </div>
      </div>
    </div>
  );
}
