import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getDashboard } from "../services/api";
import { Spinner, ProgressBar } from "../components/Layout";
import { Target, BookOpen, AlertCircle, TrendingUp, CheckCircle, BrainCircuit } from "lucide-react";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboard()
      .then((res) => {
        setData(res.data);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, []);

  if (loading) return <Spinner text="Loading your dashboard..." />;

  // If no career goal is set, prompt them to set it up
  if (!data?.career_goal) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">👋</div>
        <h3>Welcome to SkillGap AI</h3>
        <p>To get started, please set up your profile and tell us your career goal.</p>
        <Link to="/profile" className="btn btn-primary mt-4">Set Up Profile</Link>
      </div>
    );
  }

  // If no skills found, prompt to upload resume
  if (data.skills_found === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">📄</div>
        <h3>Upload Your Resume</h3>
        <p>We need to know what you already know. Upload your resume to extract your current skills.</p>
        <Link to="/resume" className="btn btn-primary mt-4">Upload Resume</Link>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1>Welcome back, {data.user_name.split(' ')[0]}!</h1>
          <p>Here is an overview of your progress towards becoming a {data.career_goal}.</p>
        </div>
        <Link to="/analysis" className="btn btn-primary">
          <BrainCircuit size={16} /> Re-run Analysis
        </Link>
      </div>

      {/* Main Stats */}
      <div className="grid-4 mb-8">
        <div className="stat-card">
          <div className="stat-icon purple"><Target size={24} color="var(--primary)" /></div>
          <div>
            <div className="stat-value">{data.readiness_score}%</div>
            <div className="stat-label">Career Readiness</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon cyan"><CheckCircle size={24} color="var(--accent)" /></div>
          <div>
            <div className="stat-value">{data.skills_found}</div>
            <div className="stat-label">Skills Found</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon amber"><AlertCircle size={24} color="var(--warning)" /></div>
          <div>
            <div className="stat-value">{data.skills_to_improve}</div>
            <div className="stat-label">Skills to Learn/Improve</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon green"><TrendingUp size={24} color="var(--success)" /></div>
          <div>
            <div className="stat-value">{data.learning_progress}%</div>
            <div className="stat-label">Roadmap Progress</div>
          </div>
        </div>
      </div>

      <div className="grid-2">
        {/* Left Column */}
        <div className="flex-col gap-6">
          <div className="card">
            <h3 className="card-title">Learning Progress</h3>
            <ProgressBar value={data.learning_progress} label="Overall Completion" />
            <div className="flex justify-between mt-4 text-sm text-secondary">
              <span>{data.completed_topics} Topics Completed</span>
              <span>{data.in_progress_topics} In Progress</span>
            </div>
            <div className="mt-6">
              <Link to="/roadmap" className="btn btn-ghost btn-sm w-full justify-center">View Full Roadmap</Link>
            </div>
          </div>

          <div className="card">
            <h3 className="card-title">Recent Test Performance</h3>
            {data.test_total > 0 ? (
              <>
                <div style={{ textAlign: "center", marginBottom: "20px" }}>
                  <div style={{ fontSize: "48px", fontWeight: "800", color: "var(--primary)" }}>
                    {Math.round((data.test_score / data.test_total) * 100)}%
                  </div>
                  <p className="text-secondary">Score: {data.test_score} out of {data.test_total}</p>
                </div>
                <Link to="/test" className="btn btn-secondary btn-sm w-full justify-center">Retake Skill Test</Link>
              </>
            ) : (
              <div className="text-center py-4">
                <p className="text-muted mb-4">You haven't taken a skill test recently.</p>
                <Link to="/test" className="btn btn-primary btn-sm">Take Skill Test</Link>
              </div>
            )}
          </div>
        </div>

        {/* Right Column */}
        <div className="card">
          <h3 className="card-title">Missing & Weak Skills</h3>
          <p className="text-secondary mb-4" style={{ fontSize: "14px" }}>
            Focus on learning these skills to improve your readiness for the {data.career_goal} role.
          </p>

          <div className="flex-col gap-4">
            {data.missing_skills.length === 0 && data.weak_skills.length === 0 ? (
              <div className="alert alert-success">
                Great job! You have all the base skills required for this role. Keep practicing!
              </div>
            ) : (
              <>
                {data.missing_skills.slice(0, 5).map(skill => (
                  <div key={skill} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px", border: "1px solid var(--border)", borderRadius: "var(--radius-sm)" }}>
                    <span style={{ fontWeight: "600" }}>{skill}</span>
                    <span className="badge badge-high">Missing</span>
                  </div>
                ))}
                {data.weak_skills.slice(0, 5).map(skill => (
                  <div key={skill} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px", border: "1px solid var(--border)", borderRadius: "var(--radius-sm)" }}>
                    <span style={{ fontWeight: "600" }}>{skill}</span>
                    <span className="badge badge-medium">Weak</span>
                  </div>
                ))}
              </>
            )}
          </div>

          <div className="mt-6 text-center">
            <Link to="/courses" className="btn btn-primary btn-sm">Find Courses for These</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
