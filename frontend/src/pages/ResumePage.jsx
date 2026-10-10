import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { uploadResume, getSkills, updateSkills } from "../services/api";
import { StepIndicator, SkillTag, Spinner } from "../components/Layout";
import { UploadCloud, File, Plus, ArrowRight } from "lucide-react";
import toast from "react-hot-toast";

export default function ResumePage() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [skills, setSkills] = useState([]);
  const [newSkill, setNewSkill] = useState("");
  const [resumeData, setResumeData] = useState(null);
  const [loading, setLoading] = useState(true);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user already has a resume/skills
    getSkills()
      .then((res) => {
        if (res.data.skills && res.data.skills.length > 0) {
          setSkills(res.data.skills);
          setResumeData(res.data);
        }
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      if (!selected.name.endsWith(".pdf") && !selected.name.endsWith(".docx")) {
        return toast.error("Only PDF or DOCX files are allowed.");
      }
      setFile(selected);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await uploadResume(formData);
      setSkills(res.data.skills);
      setResumeData(res.data);
      toast.success("Resume processed successfully!");
      setFile(null);
    } catch (err) {
      toast.error(err.response?.data?.error || "Failed to process resume.");
    } finally {
      setUploading(false);
    }
  };

  const handleAddSkill = async (e) => {
    e.preventDefault();
    const trimmed = newSkill.trim();
    if (!trimmed) return;
    if (skills.some((s) => s.toLowerCase() === trimmed.toLowerCase())) {
      return toast.error("Skill already exists.");
    }

    const updated = [...skills, trimmed].sort();
    setSkills(updated);
    setNewSkill("");

    try {
      await updateSkills(updated);
    } catch (err) {
      toast.error("Failed to save skill.");
    }
  };

  const handleRemoveSkill = async (skillToRemove) => {
    const updated = skills.filter((s) => s !== skillToRemove);
    setSkills(updated);
    try {
      await updateSkills(updated);
    } catch (err) {
      toast.error("Failed to update skills.");
    }
  };

  const handleContinue = () => {
    if (skills.length === 0) {
      return toast.error("Please upload a resume or add skills manually.");
    }
    navigate("/test");
  };

  if (loading) return <Spinner text="Loading..." />;

  return (
    <div>
      <div className="page-header">
        <h1>Resume & Skills</h1>
        <p>Upload your resume to automatically extract your current skills.</p>
      </div>

      <StepIndicator steps={["Upload Resume", "Take Skill Test", "View Analysis"]} currentStep={0} />

      <div className="grid-2">
        {/* Upload Section */}
        <div className="card">
          <h3 className="card-title">Upload Resume</h3>
          <p className="text-secondary mb-4" style={{ fontSize: "14px" }}>
            Upload your latest resume (PDF or DOCX). Our AI will scan it to extract your technical skills.
          </p>

          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf,.docx,.doc"
            style={{ display: "none" }}
          />

          <div
            className="upload-area"
            onClick={() => fileInputRef.current.click()}
          >
            <UploadCloud className="upload-icon" color="var(--primary)" />
            <h3>{file ? file.name : "Click or drag file here"}</h3>
            <p>Supports PDF, DOCX (Max 10MB)</p>
          </div>

          {file && (
            <button
              className="btn btn-primary w-full mt-4 justify-center"
              onClick={handleUpload}
              disabled={uploading}
            >
              {uploading ? "Analyzing Resume..." : "Extract Skills"}
            </button>
          )}

          {resumeData?.filename && !file && (
            <div className="mt-4 p-3 bg-gray-50 rounded" style={{ background: "var(--bg)", borderRadius: "var(--radius-sm)", display: "flex", alignItems: "center", gap: "10px" }}>
              <File size={20} color="var(--text-secondary)" />
              <div>
                <p style={{ fontSize: "14px", fontWeight: "600" }}>Last uploaded file:</p>
                <p style={{ fontSize: "13px", color: "var(--text-secondary)" }}>{resumeData.filename}</p>
              </div>
            </div>
          )}
        </div>

        {/* Skills Section */}
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <h3 className="card-title" style={{ marginBottom: 0 }}>Extracted Skills</h3>
            <span className="badge badge-primary">{skills.length} Found</span>
          </div>

          {skills.length === 0 ? (
            <div className="empty-state" style={{ padding: "40px 0" }}>
              <p>No skills extracted yet. Upload a resume to get started.</p>
            </div>
          ) : (
            <div className="skills-grid mb-6">
              {skills.map((skill) => (
                <SkillTag key={skill} skill={skill} onRemove={handleRemoveSkill} />
              ))}
            </div>
          )}

          <hr style={{ border: 0, borderTop: "1px solid var(--border)", margin: "20px 0" }} />

          <form onSubmit={handleAddSkill} style={{ display: "flex", gap: "10px" }}>
            <input
              type="text"
              className="form-input"
              placeholder="Add skill manually..."
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
            />
            <button type="submit" className="btn btn-secondary">
              <Plus size={16} /> Add
            </button>
          </form>

          <button
            className="btn btn-success w-full mt-8 justify-center"
            onClick={handleContinue}
          >
            Continue to Skill Test <ArrowRight size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
