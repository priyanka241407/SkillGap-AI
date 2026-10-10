import { useState, useEffect } from "react";
import { getAnalysisResult, getProgress, updateProgress } from "../services/api";
import { Spinner } from "../components/Layout";
import { CheckCircle, Circle, PlayCircle, Clock } from "lucide-react";
import toast from "react-hot-toast";

export default function RoadmapPage() {
  const [roadmap, setRoadmap] = useState([]);
  const [progress, setProgress] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getAnalysisResult(), getProgress()])
      .then(([analysisRes, progRes]) => {
        setRoadmap(analysisRes.data.roadmap || []);
        
        // Convert progress array to map: { "Python": "completed" }
        const progMap = {};
        if (progRes.data.progress) {
          progRes.data.progress.forEach(p => {
            progMap[p.skill] = p.status;
          });
        }
        setProgress(progMap);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, []);

  const handleStatusChange = async (skill, status) => {
    // Optimistic UI update
    setProgress(prev => ({ ...prev, [skill]: status }));
    
    try {
      await updateProgress(skill, status);
      if (status === "completed") {
        toast.success(`Marked ${skill} as completed!`);
      }
    } catch (err) {
      toast.error("Failed to update progress");
      // Revert on failure (simplified)
    }
  };

  if (loading) return <Spinner text="Building your personalized roadmap..." />;

  if (roadmap.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">🗺️</div>
        <h3>No Roadmap Available</h3>
        <p>Complete a skill gap analysis to generate your roadmap.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <h1>Your Learning Roadmap</h1>
        <p>A step-by-step guide to achieving your career goal.</p>
      </div>

      <div className="roadmap" style={{ maxWidth: "800px", margin: "0 auto", padding: "20px 0" }}>
        {roadmap.map((step) => {
          // Merge backend status with local progress state
          const currentStatus = progress[step.skill] || step.status;
          
          let statusColor = "var(--text-muted)";
          let StatusIcon = Circle;
          
          if (currentStatus === "completed") {
            statusColor = "var(--success)";
            StatusIcon = CheckCircle;
          } else if (currentStatus === "in_progress") {
            statusColor = "var(--primary)";
            StatusIcon = PlayCircle;
          }

          return (
            <div key={step.step} className="roadmap-step">
              <div className={`roadmap-circle ${currentStatus}`}>
                {currentStatus === "completed" ? "✓" : step.step}
              </div>
              
              <div className="roadmap-body" style={{ borderColor: currentStatus === "completed" ? "var(--success)" : currentStatus === "in_progress" ? "var(--primary)" : "var(--border)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <h3 style={{ color: currentStatus === "completed" ? "var(--success)" : "var(--text-primary)" }}>
                      {step.skill}
                    </h3>
                    <p>{step.description}</p>
                  </div>
                  {step.priority !== "none" && (
                    <span className={`badge badge-${step.priority.toLowerCase()}`}>
                      {step.priority} Priority
                    </span>
                  )}
                </div>

                <div className="roadmap-meta">
                  <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px", color: "var(--text-secondary)", marginRight: "auto" }}>
                    <Clock size={14} /> Est. Time: {step.estimated_time}
                  </div>
                  
                  {currentStatus !== "completed" && (
                    <button 
                      className={`btn btn-sm ${currentStatus === "in_progress" ? "btn-primary" : "btn-ghost"}`}
                      onClick={() => handleStatusChange(step.skill, currentStatus === "in_progress" ? "completed" : "in_progress")}
                    >
                      {currentStatus === "in_progress" ? (
                        <><CheckCircle size={14} /> Mark Completed</>
                      ) : (
                        <><PlayCircle size={14} /> Start Learning</>
                      )}
                    </button>
                  )}
                  
                  {currentStatus === "completed" && (
                    <span style={{ fontSize: "13px", color: "var(--success)", fontWeight: "600", display: "flex", alignItems: "center", gap: "6px" }}>
                      <CheckCircle size={16} /> Completed
                    </span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
