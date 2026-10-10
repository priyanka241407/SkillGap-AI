import { Link } from "react-router-dom";
import { Navbar } from "../components/Layout";
import { BrainCircuit, BookOpen, Target, FileText, CheckCircle, Compass, LineChart } from "lucide-react";

export default function LandingPage() {
  return (
    <>
      <Navbar />

      {/* Hero Section */}
      <section className="hero">
        <h1 className="hero-title">
          Discover Your Skills. <br />
          <span className="highlight">Identify Your Gaps.</span> <br />
          Build Your Future.
        </h1>
        <p className="hero-subtitle">
          SkillGap AI is an intelligent platform that analyzes your resume, assesses your knowledge, and creates a personalized learning roadmap to help you achieve your dream job.
        </p>
        <div className="hero-actions">
          <Link to="/register" className="btn btn-primary btn-lg">
            Try SkillGap AI
          </Link>
          <a href="#how-it-works" className="btn btn-secondary btn-lg">
            Learn More
          </a>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="section section-alt">
        <div className="container">
          <div className="section-header">
            <h2>Powerful Features for Students</h2>
            <p>Everything you need to bridge the gap between your current skills and your career goals.</p>
          </div>

          <div className="feature-grid">
            <div className="feature-card">
              <div className="feature-icon"><FileText size={24} color="var(--primary)" /></div>
              <h3>Resume Skill Extraction</h3>
              <p>Upload your PDF or DOCX resume. Our AI automatically extracts your technical skills and technologies.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon"><Target size={24} color="var(--primary)" /></div>
              <h3>Career Goal Analysis</h3>
              <p>Select your target role (e.g., Data Scientist). We compare your skills against industry requirements.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon"><BrainCircuit size={24} color="var(--primary)" /></div>
              <h3>Smart Skill Assessment</h3>
              <p>Take a dynamically generated multiple-choice test tailored to your specific skill set.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon"><LineChart size={24} color="var(--primary)" /></div>
              <h3>Skill Gap Detection</h3>
              <p>Discover exactly which skills you're missing and which ones need improvement.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon"><BookOpen size={24} color="var(--primary)" /></div>
              <h3>Course Recommendations</h3>
              <p>Get curated, clickable links to high-quality free resources and courses to learn missing skills.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon"><Compass size={24} color="var(--primary)" /></div>
              <h3>Personalized Roadmap</h3>
              <p>Follow a step-by-step learning journey designed specifically for your skill gaps.</p>
            </div>
          </div>
        </div>
      </section>

      {/* How it Works Section */}
      <section id="how-it-works" className="section">
        <div className="container">
          <div className="section-header">
            <h2>How It Works</h2>
            <p>Your journey from student to professional in 4 simple steps.</p>
          </div>

          <div className="how-steps">
            <div className="how-step">
              <div className="how-step-num">1</div>
              <h3>Upload Resume</h3>
              <p>Create an account and upload your current resume.</p>
            </div>
            <div className="how-step">
              <div className="how-step-num">2</div>
              <h3>Take the Test</h3>
              <p>Answer a few questions to assess your current knowledge level.</p>
            </div>
            <div className="how-step">
              <div className="how-step-num">3</div>
              <h3>View Skill Gaps</h3>
              <p>See exactly what you need to learn for your dream job.</p>
            </div>
            <div className="how-step">
              <div className="how-step-num">4</div>
              <h3>Follow Roadmap</h3>
              <p>Learn using our recommended courses and track your progress.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-logo">SkillGap AI</div>
        <p>A smart skill gap analyzer and learning assistant project.</p>
        <div className="footer-bottom">
          &copy; {new Date().getFullYear()} SkillGap AI. All rights reserved.
        </div>
      </footer>
    </>
  );
}
