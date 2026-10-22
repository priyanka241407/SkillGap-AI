import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getAssessmentHistory, getAssessmentDetail, deleteAssessmentAttempt } from "../services/api";
import { Spinner } from "../components/Layout";
import {
  ClipboardList,
  CheckCircle,
  XCircle,
  Calendar,
  Filter,
  TrendingUp,
  Award,
  Eye,
  Trash2,
  X,
  ArrowRight,
  BookOpen,
  Sparkles,
  HelpCircle,
} from "lucide-react";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from "chart.js";
import { Line } from "react-chartjs-2";
import toast from "react-hot-toast";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

export default function AssessmentHistoryPage() {
  const [attempts, setAttempts] = useState([]);
  const [stats, setStats] = useState(null);
  const [skillOptions, setSkillOptions] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [typeFilter, setTypeFilter] = useState("all");
  const [skillFilter, setSkillFilter] = useState("all");
  const [sortFilter, setSortFilter] = useState("newest");

  // Modal detail view state
  const [selectedAttempt, setSelectedAttempt] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const fetchHistory = () => {
    setLoading(true);
    getAssessmentHistory({
      type: typeFilter,
      skill: skillFilter,
      sort: sortFilter,
    })
      .then((res) => {
        setAttempts(res.data.attempts || []);
        setStats(res.data.stats || null);
        setSkillOptions(res.data.skill_options || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load assessment history:", err);
        toast.error("Could not load assessment history.");
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchHistory();
  }, [typeFilter, skillFilter, sortFilter]);

  const handleOpenDetail = async (id) => {
    setDetailLoading(true);
    try {
      const res = await getAssessmentDetail(id);
      setSelectedAttempt(res.data);
    } catch (err) {
      toast.error("Failed to load attempt details.");
    } finally {
      setDetailLoading(false);
    }
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this assessment record?")) return;

    try {
      await deleteAssessmentAttempt(id);
      toast.success("Record deleted.");
      fetchHistory();
      if (selectedAttempt && selectedAttempt.id === id) {
        setSelectedAttempt(null);
      }
    } catch (err) {
      toast.error("Failed to delete record.");
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    const d = new Date(dateString);
    return d.toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (loading && attempts.length === 0 && !stats) {
    return <Spinner text="Loading assessment history..." />;
  }

  // Chart configuration for genuine progress trend
  const trendData = stats?.score_trend || [];
  const hasEnoughTrendData = trendData.length >= 2;

  const chartData = {
    labels: trendData.map((t, idx) => {
      const d = new Date(t.completed_at);
      return `${d.toLocaleDateString(undefined, { month: "short", day: "numeric" })} (#${idx + 1})`;
    }),
    datasets: [
      {
        label: "Score Percentage (%)",
        data: trendData.map((t) => t.score_percentage),
        borderColor: "#6366f1",
        backgroundColor: "rgba(99, 102, 241, 0.15)",
        tension: 0.3,
        pointBackgroundColor: trendData.map((t) =>
          t.assessment_type === "skill_test" ? "#8b5cf6" : "#06b6d4"
        ),
        pointRadius: 6,
        pointHoverRadius: 8,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        min: 0,
        max: 100,
        ticks: { callback: (val) => `${val}%` },
      },
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (context) => {
            const item = trendData[context.dataIndex];
            const typeLabel = item?.assessment_type === "skill_test" ? "Formal Test" : "Practice Quiz";
            return `${item?.skill_name} (${typeLabel}): ${context.raw}%`;
          },
        },
      },
    },
  };

  return (
    <div className="assessment-history-page">
      {/* Header */}
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "16px" }}>
        <div>
          <h1>Skill Assessment History</h1>
          <p>Review your previous formal skill tests and practice quiz attempts, monitor your score trends, and study question explanations.</p>
        </div>
        <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
          <Link to="/quiz" className="btn btn-primary btn-sm" style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}>
            <HelpCircle size={15} /> Practice Quiz
          </Link>
          <Link to="/test" className="btn btn-secondary btn-sm" style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}>
            <ClipboardList size={15} /> Retake Skill Test
          </Link>
        </div>
      </div>

      {/* Summary Stat Cards */}
      {stats && stats.total_assessments > 0 && (
        <div className="grid-4 mb-6">
          <div className="stat-card">
            <div className="stat-icon purple"><ClipboardList size={22} color="var(--primary)" /></div>
            <div>
              <div className="stat-value">{stats.total_assessments}</div>
              <div className="stat-label">Total Assessments</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon cyan"><TrendingUp size={22} color="var(--accent)" /></div>
            <div>
              <div className="stat-value">{stats.average_score}%</div>
              <div className="stat-label">Average Score</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon green"><Award size={22} color="var(--success)" /></div>
            <div>
              <div className="stat-value">{stats.highest_score}%</div>
              <div className="stat-label">Highest Score</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon amber"><CheckCircle size={22} color="var(--warning)" /></div>
            <div>
              <div className="stat-value">{stats.practice_quizzes_count}</div>
              <div className="stat-label">Practice Quizzes</div>
            </div>
          </div>
        </div>
      )}

      {/* Progress Trend Chart */}
      {stats && stats.total_assessments > 0 && (
        <div className="card mb-6">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px", flexWrap: "wrap", gap: "8px" }}>
            <h3 className="card-title" style={{ margin: 0, fontSize: "16px" }}>
              <TrendingUp size={18} /> Performance & Score Improvement Trend
            </h3>
            <div style={{ display: "flex", alignItems: "center", gap: "12px", fontSize: "12px" }}>
              <span style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}>
                <span style={{ width: "10px", height: "10px", borderRadius: "50%", background: "#8b5cf6" }}></span> Formal Skill Test
              </span>
              <span style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}>
                <span style={{ width: "10px", height: "10px", borderRadius: "50%", background: "#06b6d4" }}></span> Practice Quiz
              </span>
            </div>
          </div>

          {hasEnoughTrendData ? (
            <div style={{ height: "240px", width: "100%" }}>
              <Line data={chartData} options={chartOptions} />
            </div>
          ) : (
            <p style={{ color: "var(--text-secondary)", fontSize: "13px", padding: "16px 0" }}>
              ℹ️ Complete at least 2 assessments to view your performance trend graph.
            </p>
          )}
        </div>
      )}

      {/* Filter and Control Bar */}
      <div className="card mb-6" style={{ padding: "16px 20px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "16px" }}>
          {/* Type Filter Tabs */}
          <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
            {[
              { id: "all", label: "All Assessments" },
              { id: "skill_test", label: "Formal Skill Tests" },
              { id: "practice_quiz", label: "Practice Quizzes" },
            ].map((t) => (
              <button
                key={t.id}
                onClick={() => setTypeFilter(t.id)}
                className={`btn btn-sm ${typeFilter === t.id ? "btn-primary" : "btn-ghost"}`}
              >
                {t.label}
              </button>
            ))}
          </div>

          {/* Secondary Filters */}
          <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
            {skillOptions.length > 0 && (
              <select
                className="form-select"
                style={{ width: "auto", padding: "6px 12px", fontSize: "13px" }}
                value={skillFilter}
                onChange={(e) => setSkillFilter(e.target.value)}
              >
                <option value="all">All Skills / Topics</option>
                {skillOptions.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            )}

            <select
              className="form-select"
              style={{ width: "auto", padding: "6px 12px", fontSize: "13px" }}
              value={sortFilter}
              onChange={(e) => setSortFilter(e.target.value)}
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="highest">Highest Score</option>
              <option value="lowest">Lowest Score</option>
            </select>
          </div>
        </div>
      </div>

      {/* Empty State */}
      {attempts.length === 0 ? (
        <div className="empty-state card">
          <div className="empty-state-icon">📝</div>
          <h3>No Assessments Completed Yet</h3>
          <p style={{ maxWidth: "460px", margin: "0 auto 20px" }}>
            You have not completed any assessments yet. Take your first skill test to see your history here.
          </p>
          <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
            <Link to="/test" className="btn btn-primary">Take Skill Assessment</Link>
            <Link to="/quiz" className="btn btn-secondary">Start Practice Quiz</Link>
          </div>
        </div>
      ) : (
        /* Assessments Table / List */
        <div className="card" style={{ padding: 0, overflow: "hidden" }}>
          <div className="assessment-table-wrapper">
            <table className="assessment-table">
              <thead>
                <tr>
                  <th>Date & Time</th>
                  <th>Assessment Type</th>
                  <th>Skill / Topic</th>
                  <th>Difficulty</th>
                  <th>Questions</th>
                  <th>Score</th>
                  <th style={{ textAlign: "right" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {attempts.map((item) => {
                  const isSkillTest = item.assessment_type === "skill_test";
                  const isPassed = item.score_percentage >= 60;

                  return (
                    <tr
                      key={item.id}
                      onClick={() => handleOpenDetail(item.id)}
                      style={{ cursor: "pointer" }}
                    >
                      <td style={{ whiteSpace: "nowrap" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "13px" }}>
                          <Calendar size={14} color="var(--text-muted)" />
                          {formatDate(item.completed_at)}
                        </div>
                      </td>
                      <td>
                        {isSkillTest ? (
                          <span className="badge badge-primary" style={{ background: "rgba(139,92,246,0.15)", color: "var(--secondary)" }}>
                            Formal Skill Test
                          </span>
                        ) : (
                          <span className="badge badge-primary" style={{ background: "rgba(6,182,212,0.15)", color: "var(--accent)" }}>
                            Practice Quiz
                          </span>
                        )}
                      </td>
                      <td>
                        <strong>{item.skill_name}</strong>
                      </td>
                      <td>
                        <span className="badge badge-medium" style={{ textTransform: "none" }}>
                          {item.difficulty}
                        </span>
                      </td>
                      <td>
                        <span style={{ fontSize: "13px" }}>
                          <strong>{item.correct_answers}</strong> / {item.total_questions}
                        </span>
                      </td>
                      <td>
                        <span
                          className={`skill-tag ${isPassed ? "success" : "warning"}`}
                          style={{ fontWeight: "700" }}
                        >
                          {item.score_percentage}%
                        </span>
                      </td>
                      <td style={{ textAlign: "right" }}>
                        <div style={{ display: "inline-flex", gap: "6px" }}>
                          <button
                            onClick={() => handleOpenDetail(item.id)}
                            className="btn btn-ghost btn-sm"
                            title="Review question answers and explanations"
                          >
                            <Eye size={14} /> Review
                          </button>
                          <button
                            onClick={(e) => handleDelete(item.id, e)}
                            className="btn btn-ghost btn-sm"
                            style={{ color: "var(--danger)" }}
                            title="Delete this record"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Detail Breakdown Modal */}
      {selectedAttempt && (
        <div className="modal-backdrop" onClick={() => setSelectedAttempt(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                  <span className={selectedAttempt.assessment_type === "skill_test" ? "badge badge-primary" : "badge badge-cyan"}>
                    {selectedAttempt.assessment_type === "skill_test" ? "Formal Skill Test" : "Practice Quiz"}
                  </span>
                  <span className="badge badge-medium">{selectedAttempt.difficulty}</span>
                </div>
                <h2 style={{ fontSize: "20px", margin: 0 }}>
                  {selectedAttempt.skill_name} Assessment Review
                </h2>
                <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: "4px 0 0" }}>
                  Completed on {formatDate(selectedAttempt.completed_at)}
                </p>
              </div>
              <button
                onClick={() => setSelectedAttempt(null)}
                className="btn btn-ghost btn-sm"
                style={{ padding: "6px" }}
              >
                <X size={20} />
              </button>
            </div>

            <div className="modal-body">
              {/* Score summary banner */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", background: "rgba(99,102,241,0.06)", padding: "16px 20px", borderRadius: "var(--radius-sm)", marginBottom: "20px" }}>
                <div>
                  <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>Result Score</span>
                  <div style={{ fontSize: "24px", fontWeight: "800", color: "var(--primary)" }}>
                    {selectedAttempt.score_percentage}%
                  </div>
                </div>
                <div>
                  <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>Correct Answers</span>
                  <div style={{ fontSize: "18px", fontWeight: "700" }}>
                    {selectedAttempt.correct_answers} / {selectedAttempt.total_questions}
                  </div>
                </div>
              </div>

              {/* Questions List */}
              {selectedAttempt.questions_detail && selectedAttempt.questions_detail.length > 0 ? (
                <div className="flex-col gap-4">
                  {selectedAttempt.questions_detail.map((q, idx) => (
                    <div
                      key={idx}
                      className="card"
                      style={{
                        padding: "16px",
                        borderLeft: q.is_correct ? "4px solid var(--success)" : "4px solid var(--danger)",
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "8px" }}>
                        <span style={{ fontWeight: "700", fontSize: "14px" }}>
                          Question {idx + 1}
                        </span>
                        {q.is_correct ? (
                          <span className="badge badge-low" style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}>
                            <CheckCircle size={13} /> Correct
                          </span>
                        ) : (
                          <span className="badge badge-high" style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}>
                            <XCircle size={13} /> Incorrect
                          </span>
                        )}
                      </div>

                      <p style={{ fontSize: "14px", fontWeight: "600", marginBottom: "12px" }}>
                        {q.question}
                      </p>

                      <div style={{ display: "flex", gap: "16px", fontSize: "13px", marginBottom: "10px", flexWrap: "wrap" }}>
                        <div>
                          <span style={{ color: "var(--text-muted)" }}>Your Answer: </span>
                          <strong style={{ color: q.is_correct ? "var(--success)" : "var(--danger)" }}>
                            {q.chosen} {q.chosen_text ? `- ${q.chosen_text}` : ""}
                          </strong>
                        </div>
                        {!q.is_correct && (
                          <div>
                            <span style={{ color: "var(--text-muted)" }}>Correct Answer: </span>
                            <strong style={{ color: "var(--success)" }}>
                              {q.correct} {q.correct_text ? `- ${q.correct_text}` : ""}
                            </strong>
                          </div>
                        )}
                      </div>

                      {q.explanation && (
                        <div className="explanation-box" style={{ marginTop: "8px" }}>
                          <strong style={{ color: "var(--success)", fontSize: "12px" }}>💡 Explanation:</strong>
                          <p style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "2px", lineHeight: "1.4" }}>
                            {q.explanation}
                          </p>
                        </div>
                      )}

                      {q.why_wrong && (
                        <div className="explanation-box" style={{ marginTop: "6px", background: "rgba(245,158,11,0.06)" }}>
                          <strong style={{ color: "var(--warning)", fontSize: "12px" }}>⚠️ Why incorrect:</strong>
                          <p style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "2px", lineHeight: "1.4" }}>
                            {q.why_wrong}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ color: "var(--text-muted)", textAlign: "center", padding: "20px 0" }}>
                  Detailed questions breakdown is not available for this record.
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
