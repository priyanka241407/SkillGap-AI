import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getProfile, updateProfile, getJobRoles } from "../services/api";
import { Spinner } from "../components/Layout";
import toast from "react-hot-toast";

export default function ProfilePage() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [jobRoles, setJobRoles] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([getProfile(), getJobRoles()])
      .then(([profileRes, rolesRes]) => {
        setProfile({
          name: profileRes.data.name || "",
          education: profileRes.data.education || "",
          college: profileRes.data.college || "",
          current_year: profileRes.data.current_year || "",
          preferred_field: profileRes.data.preferred_field || "",
          career_goal: profileRes.data.career_goal || "",
        });
        setJobRoles(rolesRes.data.roles);
        setLoading(false);
      })
      .catch((err) => {
        toast.error("Failed to load profile");
        setLoading(false);
      });
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setProfile((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!profile.career_goal) return toast.error("Career goal is required.");

    setSaving(true);
    try {
      await updateProfile(profile);
      toast.success("Profile updated successfully!");
      // If they just registered, move them to the resume upload step
      navigate("/resume");
    } catch (err) {
      toast.error("Failed to update profile");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <Spinner text="Loading profile..." />;

  return (
    <div>
      <div className="page-header">
        <h1>Your Profile</h1>
        <p>Tell us about yourself and your career aspirations.</p>
      </div>

      <div className="card" style={{ maxWidth: "700px" }}>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input
              type="text"
              name="name"
              className="form-input"
              value={profile.name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Degree / Education</label>
              <input
                type="text"
                name="education"
                className="form-input"
                placeholder="e.g., B.Tech Computer Science"
                value={profile.education}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Current Year</label>
              <select
                name="current_year"
                className="form-select"
                value={profile.current_year}
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

          <div className="form-group">
            <label className="form-label">College / University</label>
            <input
              type="text"
              name="college"
              className="form-input"
              placeholder="e.g., Stanford University"
              value={profile.college}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Career Goal (Target Job Role) <span style={{color: "var(--danger)"}}>*</span></label>
            <p style={{fontSize: "12px", color: "var(--text-secondary)", marginBottom: "8px"}}>
              This is critical! We use this to determine which skills you need to learn.
            </p>
            <select
              name="career_goal"
              className="form-select"
              value={profile.career_goal}
              onChange={handleChange}
              required
            >
              <option value="">Select your dream job</option>
              {jobRoles.map((role) => (
                <option key={role} value={role}>{role}</option>
              ))}
            </select>
          </div>

          <button type="submit" className="btn btn-primary mt-4" disabled={saving}>
            {saving ? "Saving..." : "Save Profile & Continue"}
          </button>
        </form>
      </div>
    </div>
  );
}
