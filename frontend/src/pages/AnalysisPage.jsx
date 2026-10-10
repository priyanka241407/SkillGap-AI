import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getAnalysisResult } from "../services/api";
import { StepIndicator, Spinner, SkillTag } from "../components/Layout";
import { ArrowRight, Download } from "lucide-react";
import { Chart as ChartJS, RadialLinearScale, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';

ChartJS.register(RadialLinearScale, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

export default function AnalysisPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    getAnalysisResult()
      .then((res) => {
        if (!res.data.career_goal) {
          navigate("/dashboard");
        } else {
          setData(res.data);
        }
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, [navigate]);

  if (loading) return <Spinner text="Loading your analysis..." />;
  if (!data) return null;

  const missingSkills = data.missing_skills || [];
  const strongSkills = data.strong_skills || [];
  const weakSkills = data.weak_skills || [];

  // Chart Data
  const doughnutData = {
    labels: ['Strong', 'Weak', 'Missing'],
    datasets: [{
      data: [strongSkills.length, weakSkills.length, missingSkills.length],
      backgroundColor: ['rgba(16,185,129,0.8)', 'rgba(245,158,11,0.8)', 'rgba(239,68,68,0.8)'],
      borderWidth: 0,
    }],
  };

  return (
    <div>
      <div className="page-header">
        <h1>Skill Gap Analysis</h1>
        <p>Detailed breakdown of your current skills compared to the {data.career_goal} role.</p>
      </div>

      <StepIndicator steps={["Upload Resume", "Take Skill Test", "View Analysis"]} currentStep={2} />

      <div className="grid-3 mb-6">
        <div className="readiness-card">
          <div className="readiness-label">Career Readiness</div>
          <div className="readiness-score">{data.readiness_score}%</div>
          <p style={{ fontSize: "14px", opacity: 0.8 }}>Target: {data.career_goal}</p>
        </div>

        <div className="card" style={{ gridColumn: "span 2", display: "flex", alignItems: "center", gap: "24px" }}>
          <div style={{ width: "160px", flexShrink: 0 }}>
            <Doughnut 
              data={doughnutData} 
              options={{ maintainAspectRatio: true, cutout: '70%', plugins: { legend: { display: false } } }} 
            />
          </div>
          <div style={{ flex: 1 }}>
            <h3 className="mb-4">Test Performance Overview</h3>
            <div style={{ display: "flex", gap: "20px" }}>
              <div>
                <p className="text-muted text-sm">Test Score</p>
                <p style={{ fontSize: "24px", fontWeight: "700" }}>{data.test_score} / {data.test_total}</p>
              </div>
              <div>
                <p className="text-muted text-sm">Skills Mastered</p>
                <p style={{ fontSize: "24px", fontWeight: "700", color: "var(--success)" }}>{strongSkills.length}</p>
              </div>
              <div>
                <p className="text-muted text-sm">Skills Needed</p>
                <p style={{ fontSize: "24px", fontWeight: "700", color: "var(--danger)" }}>{missingSkills.length + weakSkills.length}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid-3">
        <div className="gap-section">
          <h3 className="gap-section-title" style={{ color: "var(--success)" }}>
            <span className="badge badge-low">Strong</span> Skills
          </h3>
          <p className="text-secondary mb-4" style={{ fontSize: "13px" }}>Skills you know well and performed well on in the test.</p>
          <div className="flex-col gap-2">
            {strongSkills.length > 0 ? strongSkills.map(skill => (
              <SkillTag key={skill} skill={skill} variant="success" />
            )) : <p className="text-muted text-sm">None identified yet.</p>}
          </div>
        </div>

        <div className="gap-section">
          <h3 className="gap-section-title" style={{ color: "var(--warning)" }}>
            <span className="badge badge-medium">Weak</span> Skills
          </h3>
          <p className="text-secondary mb-4" style={{ fontSize: "13px" }}>Skills on your resume that need improvement based on the test.</p>
          <div className="flex-col gap-2">
            {weakSkills.length > 0 ? weakSkills.map(skill => (
              <SkillTag key={skill} skill={skill} variant="warning" />
            )) : <p className="text-muted text-sm">None identified yet.</p>}
          </div>
        </div>

        <div className="gap-section" style={{ borderLeft: "4px solid var(--danger)" }}>
          <h3 className="gap-section-title" style={{ color: "var(--danger)" }}>
            <span className="badge badge-high">Missing</span> Skills
          </h3>
          <p className="text-secondary mb-4" style={{ fontSize: "13px" }}>Crucial skills required for the job that you don't have yet.</p>
          <div className="flex-col gap-2">
            {missingSkills.length > 0 ? missingSkills.map(item => (
              <div key={item.skill} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <SkillTag skill={item.skill} variant="danger" />
                <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>Priority: {item.priority}</span>
              </div>
            )) : <p className="text-muted text-sm">None! You have all required skills.</p>}
          </div>
        </div>
      </div>

      <div className="mt-8 flex gap-4 justify-center">
        <Link to="/courses" className="btn btn-primary btn-lg">
          View Recommended Courses <ArrowRight size={18} />
        </Link>
        <Link to="/roadmap" className="btn btn-secondary btn-lg">
          View Learning Roadmap
        </Link>
      </div>
    </div>
  );
}
