import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getTestQuestions, submitTest, runAnalysis } from "../services/api";
import { StepIndicator, Spinner } from "../components/Layout";
import { ArrowRight, ArrowLeft } from "lucide-react";
import toast from "react-hot-toast";

export default function TestPage() {
  const [questions, setQuestions] = useState([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    getTestQuestions()
      .then((res) => {
        if (res.data.questions.length === 0) {
          toast.error("No questions available for your skills.");
          navigate("/analysis");
        } else {
          setQuestions(res.data.questions);
        }
        setLoading(false);
      })
      .catch((err) => {
        toast.error(err.response?.data?.error || "Failed to load test.");
        navigate("/resume");
        setLoading(false);
      });
  }, [navigate]);

  const handleSelect = (option) => {
    setAnswers({ ...answers, [questions[currentIdx].id]: option });
  };

  const handleNext = () => {
    if (currentIdx < questions.length - 1) {
      setCurrentIdx(currentIdx + 1);
    }
  };

  const handlePrev = () => {
    if (currentIdx > 0) {
      setCurrentIdx(currentIdx - 1);
    }
  };

  const handleSubmit = async () => {
    if (Object.keys(answers).length < questions.length) {
      const confirm = window.confirm("You have unanswered questions. Are you sure you want to submit?");
      if (!confirm) return;
    }

    setSubmitting(true);
    try {
      // 1. Submit test answers
      await submitTest(answers);
      // 2. Immediately trigger full skill gap analysis based on these new results
      await runAnalysis();
      
      toast.success("Test submitted! Analysis complete.");
      navigate("/analysis");
    } catch (err) {
      toast.error("Failed to submit test or run analysis.");
      setSubmitting(false);
    }
  };

  if (loading) return <Spinner text="Generating your personalized test..." />;
  if (questions.length === 0) return null;

  const currentQ = questions[currentIdx];
  const selectedAnswer = answers[currentQ.id];
  const progressPct = ((currentIdx + 1) / questions.length) * 100;

  return (
    <div>
      <div className="page-header">
        <h1>Skill Assessment</h1>
        <p>Answer these questions so we can understand your current knowledge level.</p>
      </div>

      <StepIndicator steps={["Upload Resume", "Take Skill Test", "View Analysis"]} currentStep={1} />

      <div className="quiz-card">
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px", fontSize: "14px", color: "var(--text-secondary)" }}>
          <span>Question {currentIdx + 1} of {questions.length}</span>
          <span>Skill: <strong>{currentQ.skill}</strong></span>
        </div>
        
        <div className="quiz-progress-bar">
          <div className="quiz-progress-fill" style={{ width: `${progressPct}%` }} />
        </div>

        <h3 className="quiz-question">{currentQ.question}</h3>

        <div className="quiz-options">
          {Object.entries(currentQ.options).map(([letter, text]) => (
            <button
              key={letter}
              className={`quiz-option ${selectedAnswer === letter ? "selected" : ""}`}
              onClick={() => handleSelect(letter)}
            >
              <div className="option-letter">{letter}</div>
              <div style={{ flex: 1 }}>{text}</div>
            </button>
          ))}
        </div>

        <div style={{ display: "flex", justifyContent: "space-between", marginTop: "32px" }}>
          <button
            className="btn btn-ghost"
            onClick={handlePrev}
            disabled={currentIdx === 0}
          >
            <ArrowLeft size={16} /> Previous
          </button>

          {currentIdx === questions.length - 1 ? (
            <button
              className="btn btn-primary"
              onClick={handleSubmit}
              disabled={submitting}
            >
              {submitting ? "Analyzing..." : "Submit Test & See Results"} <ArrowRight size={16} />
            </button>
          ) : (
            <button
              className="btn btn-primary"
              onClick={handleNext}
            >
              Next <ArrowRight size={16} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
