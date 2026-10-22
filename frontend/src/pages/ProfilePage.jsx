import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getProfile, updateProfile, getJobRoles } from "../services/api";
import { Spinner } from "../components/Layout";
import toast from "react-hot-toast";
import {
  User,
  GraduationCap,
  Briefcase,
  Code2,
  Clock,
  Link as LinkIcon,
  Plus,
  X,
  CheckCircle,
  AlertCircle,
  Save,
  ChevronDown,
} from "lucide-react";

// ── Constants ────────────────────────────────────────────────────────────────

const BRANCH_OPTIONS = [
  "Artificial Intelligence and Data Science",
  "Computer Science",
  "Information Technology",
  "Electronics and Telecommunication",
  "Mechanical Engineering",
  "Other",
];

const CAREER_DOMAIN_OPTIONS = [
  "AI / Machine Learning",
  "Web Development",
  "Data Analytics",
  "Full Stack Development",
  "Cybersecurity",
  "Cloud Computing",
  "Other",
];

const EXPERIENCE_LEVELS = ["Beginner", "Intermediate", "Experienced"];

const WEEKLY_HOURS_OPTIONS = [
  "3–5 hours",
  "6–10 hours",
  "11–15 hours",
  "More than 15 hours",
];

const PRESET_SKILLS = [
  "Python", "Java", "C", "C++", "SQL", "HTML", "CSS",
  "JavaScript", "React", "Flask", "Machine Learning",
  "Data Analysis", "Statistics", "NumPy", "Pandas", "Git / GitHub",
];

// ── URL validator ─────────────────────────────────────────────────────────────
function isValidUrl(url) {
  if (!url || url.trim() === "") return true; // optional field
  try {
    const u = new URL(url);
    return u.protocol === "http:" || u.protocol === "https:";
  } catch {
    return false;
  }
}

// ── Section Header component ──────────────────────────────────────────────────
function SectionHeader({ icon, title, subtitle }) {
  return (
    <div className="profile-section-header">
      <div className="profile-section-icon">{icon}</div>
      <div>
        <h2 className="profile-section-title">{title}</h2>
        {subtitle && <p className="profile-section-sub">{subtitle}</p>}
      </div>
    </div>
  );
}

// ── Main Profile Page ─────────────────────────────────────────────────────────
export default function ProfilePage() {
  const [loading, setLoading]   = useState(true);
  const [saving, setSaving]     = useState(false);
  const [jobRoles, setJobRoles] = useState([]);
  const navigate = useNavigate();

  // ── Form state ──────────────────────────────────────────────────────────────
  const [form, setForm] = useState({
    // Existing fields
    name:             "",
    education:        "",
    college:          "",
    current_year:     "",
    preferred_field:  "",
    career_goal:      "",
    // New fields
    branch:           "",
    branch_custom:    "",   // local only – merged into branch on save
    career_domain:    "",
    career_domain_custom: "", // local only
    experience_level: "",
    weekly_hours:     "",
    portfolio_url:    "",
  });

  const [selfSkills,   setSelfSkills]   = useState([]); // self-reported skill chips
  const [customSkill,  setCustomSkill]  = useState(""); // text box for adding custom
  const [urlError,     setUrlError]     = useState("");

  // ── Load profile on mount ──────────────────────────────────────────────────
  useEffect(() => {
    Promise.all([getProfile(), getJobRoles()])
      .then(([profileRes, rolesRes]) => {
        const p = profileRes.data;
        const savedBranch = p.branch || "";
        const savedDomain = p.career_domain || "";

        setForm({
          name:             p.name             || "",
          education:        p.education        || "",
          college:          p.college          || "",
          current_year:     p.current_year     || "",
          preferred_field:  p.preferred_field  || "",
          career_goal:      p.career_goal      || "",
          branch:           BRANCH_OPTIONS.includes(savedBranch) ? savedBranch : (savedBranch ? "Other" : ""),
          branch_custom:    BRANCH_OPTIONS.includes(savedBranch) ? "" : savedBranch,
          career_domain:    CAREER_DOMAIN_OPTIONS.includes(savedDomain) ? savedDomain : (savedDomain ? "Other" : ""),
          career_domain_custom: CAREER_DOMAIN_OPTIONS.includes(savedDomain) ? "" : savedDomain,
          experience_level: p.experience_level || "",
          weekly_hours:     p.weekly_hours     || "",
          portfolio_url:    p.portfolio_url    || "",
        });

        // self_skills comes back as an array from backend
        if (Array.isArray(p.self_skills)) {
          setSelfSkills(p.self_skills);
        }

        setJobRoles(rolesRes.data.roles || []);
        setLoading(false);
      })
      .catch(() => {
        toast.error("Failed to load profile. Please refresh.");
        setLoading(false);
      });
  }, []);

  // ── Generic field change ───────────────────────────────────────────────────
  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    if (name === "portfolio_url") {
      setUrlError(isValidUrl(value) ? "" : "Please enter a valid URL (start with http:// or https://)");
    }
  };

  // ── Skill chip helpers ─────────────────────────────────────────────────────
  const togglePresetSkill = (skill) => {
    setSelfSkills((prev) =>
      prev.includes(skill) ? prev.filter((s) => s !== skill) : [...prev, skill]
    );
  };

  const addCustomSkill = () => {
    const trimmed = customSkill.trim();
    if (!trimmed) return;
    if (selfSkills.map((s) => s.toLowerCase()).includes(trimmed.toLowerCase())) {
      toast.error("Skill already added.");
      return;
    }
    setSelfSkills((prev) => [...prev, trimmed]);
    setCustomSkill("");
  };

  const removeSkill = (skill) => {
    setSelfSkills((prev) => prev.filter((s) => s !== skill));
  };

  // ── Submit ─────────────────────────────────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!form.career_goal) {
      toast.error("Career Goal is required – it drives your entire skill analysis.");
      return;
    }
    if (form.portfolio_url && !isValidUrl(form.portfolio_url)) {
      toast.error("Please fix the portfolio URL before saving.");
      return;
    }

    // Resolve "Other" custom values
    const finalBranch = form.branch === "Other"
      ? (form.branch_custom.trim() || "Other")
      : form.branch;
    const finalDomain = form.career_domain === "Other"
      ? (form.career_domain_custom.trim() || "Other")
      : form.career_domain;

    const payload = {
      name:             form.name,
      education:        form.education,
      college:          form.college,
      current_year:     form.current_year,
      preferred_field:  form.preferred_field,
      career_goal:      form.career_goal,
      branch:           finalBranch,
      career_domain:    finalDomain,
      experience_level: form.experience_level,
      self_skills:      selfSkills,
      weekly_hours:     form.weekly_hours,
      portfolio_url:    form.portfolio_url.trim(),
    };

    setSaving(true);
    try {
      await updateProfile(payload);
      toast.success("Profile saved successfully! 🎉");
      navigate("/resume");
    } catch {
      toast.error("Failed to save profile. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <Spinner text="Loading your profile..." />;

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="profile-page">
      {/* Page Header */}
      <div className="page-header">
        <h1>Your Profile</h1>
        <p>Complete your profile to get personalised skill gap analysis and learning recommendations.</p>
      </div>

      <form onSubmit={handleSubmit}>
        {/* ── 1. ACADEMIC INFORMATION ────────────────────────────────────────── */}
        <div className="profile-card">
          <SectionHeader
            icon={<GraduationCap size={20} />}
            title="Academic Information"
            subtitle="Tell us about your educational background."
          />

          {/* Full Name */}
          <div className="form-group">
            <label className="form-label">
              Full Name <span className="required-star">*</span>
            </label>
            <input
              type="text"
              name="name"
              className="form-input"
              placeholder="e.g., Priyanka Nikam"
              value={form.name}
              onChange={handleChange}
              required
            />
          </div>

          {/* Degree & Year */}
          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Degree / Education</label>
              <input
                type="text"
                name="education"
                className="form-input"
                placeholder="e.g., B.Tech Computer Science"
                value={form.education}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Current Year</label>
              <select
                name="current_year"
                className="form-select"
                value={form.current_year}
                onChange={handleChange}
              >
                <option value="">Select Year</option>
                <option value="1st Year">1st Year</option>
                <option value="2nd Year">2nd Year</option>
                <option value="3rd Year">3rd Year</option>
                <option value="4th Year">4th Year</option>
                <option value="Graduated">Graduated</option>
              </select>
            </div>
          </div>

          {/* College */}
          <div className="form-group">
            <label className="form-label">College / University</label>
            <input
              type="text"
              name="college"
              className="form-input"
              placeholder="e.g., MIT College of Engineering"
              value={form.college}
              onChange={handleChange}
            />
          </div>

          {/* Branch / Specialization */}
          <div className="form-group">
            <label className="form-label">Branch / Specialization</label>
            <select
              name="branch"
              className="form-select"
              value={form.branch}
              onChange={handleChange}
            >
              <option value="">Select Branch</option>
              {BRANCH_OPTIONS.map((b) => (
                <option key={b} value={b}>{b}</option>
              ))}
            </select>
          </div>

          {/* Custom branch input shown when "Other" is selected */}
          {form.branch === "Other" && (
            <div className="form-group">
              <label className="form-label">Specify Your Branch</label>
              <input
                type="text"
                name="branch_custom"
                className="form-input"
                placeholder="e.g., Civil Engineering"
                value={form.branch_custom}
                onChange={handleChange}
              />
            </div>
          )}
        </div>

        {/* ── 2. CAREER PREFERENCES ──────────────────────────────────────────── */}
        <div className="profile-card">
          <SectionHeader
            icon={<Briefcase size={20} />}
            title="Career Preferences"
            subtitle="Help us understand your career direction and experience level."
          />

          {/* Career Goal – existing critical field */}
          <div className="form-group">
            <label className="form-label">
              Career Goal (Target Job Role) <span className="required-star">*</span>
            </label>
            <p className="form-hint">
              This is critical! We use this to determine which skills you need to learn.
            </p>
            <select
              name="career_goal"
              className="form-select"
              value={form.career_goal}
              onChange={handleChange}
              required
            >
              <option value="">Select your dream job role</option>
              {jobRoles.map((role) => (
                <option key={role} value={role}>{role}</option>
              ))}
            </select>
          </div>

          <div className="grid-2">
            {/* Preferred Career Domain */}
            <div className="form-group">
              <label className="form-label">Preferred Career Domain</label>
              <select
                name="career_domain"
                className="form-select"
                value={form.career_domain}
                onChange={handleChange}
              >
                <option value="">Select Domain</option>
                {CAREER_DOMAIN_OPTIONS.map((d) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>

            {/* Experience Level */}
            <div className="form-group">
              <label className="form-label">Experience Level</label>
              <select
                name="experience_level"
                className="form-select"
                value={form.experience_level}
                onChange={handleChange}
              >
                <option value="">Select Level</option>
                {EXPERIENCE_LEVELS.map((lvl) => (
                  <option key={lvl} value={lvl}>{lvl}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Custom domain input */}
          {form.career_domain === "Other" && (
            <div className="form-group">
              <label className="form-label">Specify Your Domain</label>
              <input
                type="text"
                name="career_domain_custom"
                className="form-input"
                placeholder="e.g., Embedded Systems"
                value={form.career_domain_custom}
                onChange={handleChange}
              />
            </div>
          )}
        </div>

        {/* ── 3. TECHNICAL SKILLS ────────────────────────────────────────────── */}
        <div className="profile-card">
          <SectionHeader
            icon={<Code2 size={20} />}
            title="Technical Skills"
            subtitle="Select your self-reported skills. Assessment-verified skills are shown separately in the Analysis section."
          />

          {/* Note: Self-reported vs verified */}
          <div className="profile-skills-note">
            <CheckCircle size={14} style={{ color: "var(--primary)", flexShrink: 0 }} />
            <span>
              These are <strong>self-reported skills</strong>. Skills verified through assessments
              appear in your Skill Gap Analysis page.
            </span>
          </div>

          {/* Preset skill pills */}
          <p className="form-label" style={{ marginBottom: "10px" }}>
            Click to select / deselect skills:
          </p>
          <div className="profile-skill-picker">
            {PRESET_SKILLS.map((skill) => {
              const selected = selfSkills.includes(skill);
              return (
                <button
                  key={skill}
                  type="button"
                  onClick={() => togglePresetSkill(skill)}
                  className={`profile-skill-chip ${selected ? "selected" : ""}`}
                >
                  {selected && <CheckCircle size={13} />}
                  {skill}
                </button>
              );
            })}
          </div>

          {/* Add custom skill */}
          <div className="profile-custom-skill-row">
            <input
              type="text"
              className="form-input"
              placeholder="Add a custom skill (e.g., TensorFlow)..."
              value={customSkill}
              onChange={(e) => setCustomSkill(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") { e.preventDefault(); addCustomSkill(); }
              }}
              style={{ flex: 1 }}
            />
            <button
              type="button"
              onClick={addCustomSkill}
              className="btn btn-secondary btn-sm"
              style={{ whiteSpace: "nowrap" }}
            >
              <Plus size={15} /> Add Skill
            </button>
          </div>

          {/* Selected skills display */}
          {selfSkills.length > 0 && (
            <div style={{ marginTop: "16px" }}>
              <p className="form-label" style={{ marginBottom: "8px" }}>
                Your selected skills ({selfSkills.length}):
              </p>
              <div className="skills-grid">
                {selfSkills.map((skill) => (
                  <span key={skill} className="profile-selected-skill">
                    {skill}
                    <button
                      type="button"
                      onClick={() => removeSkill(skill)}
                      className="profile-skill-remove"
                      title={`Remove ${skill}`}
                      aria-label={`Remove ${skill}`}
                    >
                      <X size={12} />
                    </button>
                  </span>
                ))}
              </div>
            </div>
          )}

          {selfSkills.length === 0 && (
            <p style={{ color: "var(--text-muted)", fontSize: "13px", marginTop: "12px" }}>
              No skills selected yet. Click skills above or add a custom one.
            </p>
          )}
        </div>

        {/* ── 4. LEARNING PREFERENCES ───────────────────────────────────────── */}
        <div className="profile-card">
          <SectionHeader
            icon={<Clock size={20} />}
            title="Learning Preferences"
            subtitle="Help us personalise your learning roadmap."
          />

          <div className="form-group" style={{ maxWidth: "340px" }}>
            <label className="form-label">Weekly Learning Availability</label>
            <select
              name="weekly_hours"
              className="form-select"
              value={form.weekly_hours}
              onChange={handleChange}
            >
              <option value="">Select hours per week</option>
              {WEEKLY_HOURS_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
            <p className="form-hint" style={{ marginTop: "6px" }}>
              Used to suggest realistic weekly learning goals in your roadmap.
            </p>
          </div>
        </div>

        {/* ── 5. PROJECTS & PORTFOLIO ───────────────────────────────────────── */}
        <div className="profile-card">
          <SectionHeader
            icon={<LinkIcon size={20} />}
            title="Projects & Portfolio"
            subtitle="Share your work – this field is completely optional."
          />

          <div className="form-group" style={{ maxWidth: "520px" }}>
            <label className="form-label">GitHub / Portfolio URL</label>
            <div style={{ position: "relative" }}>
              <input
                type="url"
                name="portfolio_url"
                className={`form-input ${urlError ? "input-error" : ""}`}
                placeholder="https://github.com/yourusername"
                value={form.portfolio_url}
                onChange={handleChange}
                style={{ paddingLeft: "42px" }}
              />
              <LinkIcon
                size={16}
                style={{
                  position: "absolute", left: "14px", top: "50%",
                  transform: "translateY(-50%)",
                  color: "var(--text-muted)",
                  pointerEvents: "none",
                }}
              />
            </div>

            {/* URL validation feedback */}
            {urlError && (
              <div className="profile-url-error">
                <AlertCircle size={14} />
                <span>{urlError}</span>
              </div>
            )}

            {form.portfolio_url && !urlError && (
              <div className="profile-url-success">
                <CheckCircle size={14} />
                <a
                  href={form.portfolio_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ color: "var(--success)", fontSize: "13px" }}
                >
                  Preview link ↗
                </a>
              </div>
            )}
          </div>
        </div>

        {/* ── Save Button ────────────────────────────────────────────────────── */}
        <div className="profile-save-row">
          <button
            type="submit"
            className="btn btn-primary btn-lg"
            disabled={saving || !!urlError}
            id="save-profile-btn"
          >
            {saving ? (
              <>
                <span className="spinner-mini" />
                Saving...
              </>
            ) : (
              <>
                <Save size={18} />
                Save Profile &amp; Continue
              </>
            )}
          </button>
          <p className="profile-save-hint">
            <span className="required-star">*</span> Career Goal is required. All other fields are optional.
          </p>
        </div>
      </form>
    </div>
  );
}
