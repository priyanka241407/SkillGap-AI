import { useState, useEffect } from "react";
import { getAnalysisResult } from "../services/api";
import { Spinner } from "../components/Layout";
import { ExternalLink, PlayCircle, BookOpen, AlertCircle } from "lucide-react";

export default function CoursesPage() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("All");

  useEffect(() => {
    getAnalysisResult()
      .then((res) => {
        setRecommendations(res.data.recommendations || []);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, []);

  if (loading) return <Spinner text="Finding the best courses for you..." />;

  if (recommendations.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">🎓</div>
        <h3>No recommendations needed</h3>
        <p>You have all the required skills for your current career goal!</p>
      </div>
    );
  }

  const filteredRecs = filter === "All" 
    ? recommendations 
    : recommendations.filter(r => filter === "Missing" ? r.is_missing : !r.is_missing);

  return (
    <div>
      <div className="page-header">
        <h1>Recommended Resources</h1>
        <p>Curated free courses and videos to help you bridge your skill gaps.</p>
      </div>

      <div className="tabs">
        <button 
          className={`tab-btn ${filter === "All" ? "active" : ""}`}
          onClick={() => setFilter("All")}
        >
          All Recommendations
        </button>
        <button 
          className={`tab-btn ${filter === "Missing" ? "active" : ""}`}
          onClick={() => setFilter("Missing")}
        >
          For Missing Skills
        </button>
        <button 
          className={`tab-btn ${filter === "Improve" ? "active" : ""}`}
          onClick={() => setFilter("Improve")}
        >
          For Weak Skills
        </button>
      </div>

      <div className="grid-2">
        {filteredRecs.map((course, idx) => (
          <div key={`${course.id}-${idx}`} className="course-card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div className="course-platform">
                {course.platform.toLowerCase().includes("youtube") ? <PlayCircle size={14} color="#ef4444" /> : <BookOpen size={14} color="var(--primary)" />}
                {course.platform}
              </div>
              <span className={`badge ${course.is_missing ? "badge-high" : "badge-medium"}`}>
                {course.for_skill}
              </span>
            </div>
            
            <h3 className="course-title">{course.title}</h3>
            
            <div style={{ display: "flex", gap: "8px", fontSize: "12px", color: "var(--text-muted)", marginBottom: "4px" }}>
              <span>Level: {course.level}</span>
              <span>•</span>
              <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                {course.is_missing ? <AlertCircle size={12} color="var(--danger)" /> : null}
                {course.is_missing ? "Missing Skill" : "Needs Improvement"}
              </span>
            </div>

            <p className="course-desc">{course.description}</p>
            
            <a 
              href={course.url} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="btn btn-secondary w-full justify-center mt-2"
            >
              {course.link_text || "View Resource"} <ExternalLink size={14} />
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}
