import { useState, useEffect } from "react";
import { getHistory, deleteHistoryItem, clearAllHistory } from "../services/api";
import { Spinner } from "../components/Layout";
import { Clock, Target, Trash2 } from "lucide-react";
import toast from "react-hot-toast";

export default function HistoryPage() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState(null);
  const [clearing, setClearing] = useState(false);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = () => {
    getHistory()
      .then((res) => {
        setHistory(res.data.history || []);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  };

  const handleDeleteItem = async (id) => {
    if (!window.confirm("Are you sure you want to delete this analysis record?")) return;

    setDeletingId(id);
    try {
      await deleteHistoryItem(id);
      setHistory((prev) => prev.filter((item) => item.id !== id));
      toast.success("Analysis record deleted.");
    } catch (err) {
      toast.error(err.response?.data?.error || "Failed to delete record.");
    } finally {
      setDeletingId(null);
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm("Are you sure you want to clear your entire analysis history? This action cannot be undone.")) return;

    setClearing(true);
    try {
      await clearAllHistory();
      setHistory([]);
      toast.success("All history cleared successfully.");
    } catch (err) {
      toast.error(err.response?.data?.error || "Failed to clear history.");
    } finally {
      setClearing(false);
    }
  };

  if (loading) return <Spinner text="Loading history..." />;

  if (history.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">🕒</div>
        <h3>No History Yet</h3>
        <p>Complete your first skill gap analysis to see it here.</p>
      </div>
    );
  }

  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  return (
    <div>
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "16px" }}>
        <div>
          <h1>Analysis History</h1>
          <p>Review your past skill gap analyses and track your improvement over time.</p>
        </div>
        {history.length > 0 && (
          <button
            onClick={handleClearAll}
            disabled={clearing}
            className="btn btn-secondary"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
              color: "var(--danger)",
              borderColor: "var(--danger)"
            }}
          >
            <Trash2 size={16} />
            {clearing ? "Clearing..." : "Clear All History"}
          </button>
        )}
      </div>

      <div className="flex-col gap-4">
        {history.map((record, index) => (
          <div key={record.id} className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
              <div>
                <h3 className="card-title" style={{ marginBottom: "4px" }}>
                  Analysis #{history.length - index}
                </h3>
                <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "13px", color: "var(--text-secondary)" }}>
                  <Clock size={14} /> {formatDate(record.created_at)}
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <span className="badge badge-primary" style={{ display: "inline-flex", alignItems: "center", gap: "4px", fontSize: "13px", padding: "4px 12px" }}>
                  <Target size={14} /> {record.career_goal}
                </span>
                <button
                  onClick={() => handleDeleteItem(record.id)}
                  disabled={deletingId === record.id}
                  className="btn-icon"
                  title="Delete this analysis"
                  style={{
                    background: "none",
                    border: "1px solid var(--border)",
                    borderRadius: "var(--radius-sm)",
                    padding: "6px 8px",
                    cursor: "pointer",
                    color: "var(--text-muted)",
                    transition: "all 0.2s ease"
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.color = "var(--danger)";
                    e.currentTarget.style.borderColor = "var(--danger)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.color = "var(--text-muted)";
                    e.currentTarget.style.borderColor = "var(--border)";
                  }}
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>

            <div className="grid-3 mt-4" style={{ background: "var(--bg)", padding: "16px", borderRadius: "var(--radius-sm)" }}>
              <div>
                <p style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "1px", fontWeight: "600", marginBottom: "4px" }}>Career Readiness</p>
                <p style={{ fontSize: "24px", fontWeight: "800", color: "var(--primary)" }}>{record.readiness_score}%</p>
              </div>
              <div>
                <p style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "1px", fontWeight: "600", marginBottom: "4px" }}>Test Score</p>
                <p style={{ fontSize: "24px", fontWeight: "800", color: "var(--text-primary)" }}>
                  {record.test_score} <span style={{ fontSize: "16px", color: "var(--text-muted)", fontWeight: "500" }}>/ {record.test_total}</span>
                </p>
              </div>
              <div>
                <p style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "1px", fontWeight: "600", marginBottom: "4px" }}>Skills Summary</p>
                <div style={{ display: "flex", gap: "8px", fontSize: "13px", fontWeight: "600" }}>
                  <span style={{ color: "var(--success)" }}>{record.strong_skills.length} Strong</span>
                  <span style={{ color: "var(--danger)" }}>{record.missing_skills.length} Missing</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
