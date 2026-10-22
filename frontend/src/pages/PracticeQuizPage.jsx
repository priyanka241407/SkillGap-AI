import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getQuizTopics, getQuizQuestions, submitQuiz } from "../services/api";
import { Spinner } from "../components/Layout";
import {
  HelpCircle,
  CheckCircle,
  XCircle,
  ArrowRight,
  ArrowLeft,
  RotateCcw,
  Sparkles,
  BookOpen,
  Award,
  AlertCircle,
  History,
} from "lucide-react";
import toast from "react-hot-toast";

export default function PracticeQuizPage() {
  // Navigation phase: 'select' -> 'quiz' -> 'results'
  const [phase, setPhase] = useState("select");

  // Topic selection state
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState("Python");
  const [selectedDifficulty, setSelectedDifficulty] = useState("All");
  const [questionCount, setQuestionCount] = useState(5);
  const [suggestedTopic, setSuggestedTopic] = useState(null);
  const [loadingTopics, setLoadingTopics] = useState(true);

  // Quiz in-progress state
  const [questions, setQuestions] = useState([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState({});
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Results state
  const [quizResult, setQuizResult] = useState(null);

  // Load available topics and student recommendation on mount
  useEffect(() => {
    getQuizTopics()
      .then((res) => {
        if (res.data?.topics) {
          setTopics(res.data.topics);
          if (res.data.suggested_topic) {
            setSuggestedTopic(res.data.suggested_topic);
            setSelectedTopic(res.data.suggested_topic.topic);
          } else if (res.data.topics.length > 0) {
            setSelectedTopic(res.data.topics[0].name);
          }
        }
        setLoadingTopics(false);
      })
      .catch((err) => {
        console.error("Failed to load quiz topics:", err);
        toast.error("Could not load practice topics. Please check backend connection.");
        setLoadingTopics(false);
      });
  }, []);

  // Start the quiz
  const handleStartQuiz = async (topicToUse, diffToUse) => {
    const topic = topicToUse || selectedTopic;
    const diff = diffToUse || selectedDifficulty;

    setLoadingQuestions(true);
    try {
      const res = await getQuizQuestions({
        topic,
        difficulty: diff,
        limit: questionCount,
      });

      if (!res.data.questions || res.data.questions.length === 0) {
        toast.error("No questions found for this topic and difficulty. Try 'All'.");
        setLoadingQuestions(false);
        return;
      }

      setQuestions(res.data.questions);
      setCurrentIdx(0);
      setAnswers({});
      setQuizResult(null);
      setPhase("quiz");
    } catch (err) {
      console.error("Failed to load questions:", err);
      toast.error(err.response?.data?.error || "Failed to load practice questions.");
    } finally {
      setLoadingQuestions(false);
    }
  };

  // Select answer option for current question
  const handleSelectOption = (letter) => {
    const qId = questions[currentIdx].id;
    setAnswers((prev) => ({
      ...prev,
      [qId]: letter,
    }));
  };

  // Submit quiz
  const handleSubmitQuiz = async () => {
    const answeredCount = Object.keys(answers).length;
    if (answeredCount < questions.length) {
      const confirmed = window.confirm(
        `You have answered ${answeredCount} of ${questions.length} questions. Submit anyway?`
      );
      if (!confirmed) return;
    }

    setSubmitting(true);
    try {
      const res = await submitQuiz({
        topic: selectedTopic,
        difficulty: selectedDifficulty,
        answers,
      });

      setQuizResult(res.data);
      setPhase("results");
      toast.success("Practice quiz completed!");
    } catch (err) {
      console.error("Failed to submit quiz:", err);
      toast.error(err.response?.data?.error || "Failed to submit practice quiz.");
    } finally {
      setSubmitting(false);
    }
  };

  // Reset to try again
  const handleTryAgain = () => {
    setPhase("select");
    setQuestions([]);
    setAnswers({});
    setQuizResult(null);
  };

  if (loadingTopics) return <Spinner text="Loading practice topics..." />;

  // ── PHASE 1: TOPIC & DIFFICULTY SELECTION ──────────────────────────────────
  if (phase === "select") {
    const activeTopicObj = topics.find((t) => t.name === selectedTopic) || topics[0];
    const availableDifficulties = activeTopicObj?.difficulties || ["All", "Beginner", "Intermediate", "Advanced"];

    return (
      <div className="practice-quiz-page">
        <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "16px" }}>
          <div>
            <h1>Practice Quiz & Explanations</h1>
            <p>Test your technical knowledge, receive instant scoring, and learn with detailed answer explanations.</p>
          </div>
          <Link to="/assessment-history" className="btn btn-secondary btn-sm" style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}>
            <History size={16} /> View Assessment History
          </Link>
        </div>

        {/* Personalized Suggestion Banner */}
        {suggestedTopic && (
          <div className="alert alert-info" style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "12px", marginBottom: "24px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <Sparkles size={20} color="var(--primary)" style={{ flexShrink: 0 }} />
              <div>
                <strong style={{ color: "var(--primary)" }}>Recommended for you: {suggestedTopic.topic}</strong>
                <p style={{ margin: "2px 0 0", fontSize: "13px", color: "var(--text-secondary)" }}>
                  {suggestedTopic.reason}
                </p>
              </div>
            </div>
            <button
              onClick={() => {
                setSelectedTopic(suggestedTopic.topic);
                setSelectedDifficulty("All");
                handleStartQuiz(suggestedTopic.topic, "All");
              }}
              className="btn btn-primary btn-sm"
              disabled={loadingQuestions}
            >
              {loadingQuestions ? "Loading..." : `Start ${suggestedTopic.topic} Quiz`}
            </button>
          </div>
        )}

        {/* Topic Grid */}
        <div className="card mb-6">
          <h2 className="card-title" style={{ fontSize: "16px", marginBottom: "16px" }}>
            1. Select a Topic or Skill
          </h2>
          <div className="quiz-topics-grid">
            {topics.map((t) => {
              const isSelected = selectedTopic === t.name;
              return (
                <div
                  key={t.name}
                  onClick={() => setSelectedTopic(t.name)}
                  className={`quiz-topic-card ${isSelected ? "selected" : ""}`}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                    <h3 style={{ fontSize: "16px", fontWeight: "700", color: isSelected ? "var(--primary)" : "var(--text-primary)" }}>
                      {t.name}
                    </h3>
                    <span className="badge badge-primary">{t.total_questions} Questions</span>
                  </div>
                  <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: "1.4" }}>
                    {t.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Configuration Options Card */}
        <div className="grid-2 mb-6">
          <div className="card">
            <h2 className="card-title" style={{ fontSize: "16px", marginBottom: "14px" }}>
              2. Select Difficulty Level
            </h2>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "10px" }}>
              {["All", "Beginner", "Intermediate", "Advanced"].map((level) => (
                <button
                  key={level}
                  type="button"
                  onClick={() => setSelectedDifficulty(level)}
                  className={`btn ${selectedDifficulty === level ? "btn-primary" : "btn-ghost"}`}
                  style={{ flex: 1, minWidth: "100px", justifyContent: "center" }}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>

          <div className="card">
            <h2 className="card-title" style={{ fontSize: "16px", marginBottom: "14px" }}>
              3. Questions Per Quiz
            </h2>
            <div style={{ display: "flex", gap: "12px" }}>
              {[5, 10].map((num) => (
                <button
                  key={num}
                  type="button"
                  onClick={() => setQuestionCount(num)}
                  className={`btn ${questionCount === num ? "btn-primary" : "btn-ghost"}`}
                  style={{ flex: 1, justifyContent: "center" }}
                >
                  {num} Questions
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Start Button */}
        <div style={{ textAlign: "center", marginTop: "16px" }}>
          <button
            onClick={() => handleStartQuiz()}
            className="btn btn-primary btn-lg"
            disabled={loadingQuestions}
            style={{ minWidth: "240px", justifyContent: "center" }}
          >
            {loadingQuestions ? "Preparing Quiz..." : `Start ${selectedTopic} Quiz`}
          </button>
        </div>
      </div>
    );
  }

  // ── PHASE 2: QUIZ IN PROGRESS ──────────────────────────────────────────────
  if (phase === "quiz") {
    if (questions.length === 0) return null;
    const currentQ = questions[currentIdx];
    const selectedLetter = answers[currentQ.id];
    const progressPct = ((currentIdx + 1) / questions.length) * 100;
    const answeredCount = Object.keys(answers).length;

    return (
      <div className="practice-quiz-page">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
          <div>
            <span className="badge badge-primary" style={{ marginRight: "8px" }}>{selectedTopic}</span>
            <span className="badge badge-medium">{currentQ.difficulty || selectedDifficulty}</span>
          </div>
          <button onClick={handleTryAgain} className="btn btn-ghost btn-sm">
            Cancel Quiz
          </button>
        </div>

        <div className="quiz-card">
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px", fontSize: "14px", color: "var(--text-secondary)" }}>
            <span>Question {currentIdx + 1} of {questions.length}</span>
            <span>Answered: <strong>{answeredCount}</strong>/{questions.length}</span>
          </div>

          <div className="quiz-progress-bar">
            <div className="quiz-progress-fill" style={{ width: `${progressPct}%` }} />
          </div>

          <h3 className="quiz-question">{currentQ.question}</h3>

          <div className="quiz-options">
            {Object.entries(currentQ.options).map(([letter, text]) => (
              <button
                key={letter}
                type="button"
                className={`quiz-option ${selectedLetter === letter ? "selected" : ""}`}
                onClick={() => handleSelectOption(letter)}
              >
                <div className="option-letter">{letter}</div>
                <div style={{ flex: 1 }}>{text}</div>
              </button>
            ))}
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", marginTop: "32px", paddingTop: "20px", borderTop: "1px solid var(--border)" }}>
            <button
              onClick={() => setCurrentIdx((i) => Math.max(0, i - 1))}
              disabled={currentIdx === 0}
              className="btn btn-ghost"
              style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
            >
              <ArrowLeft size={16} /> Previous
            </button>

            {currentIdx < questions.length - 1 ? (
              <button
                onClick={() => setCurrentIdx((i) => i + 1)}
                className="btn btn-primary"
                style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
              >
                Next <ArrowRight size={16} />
              </button>
            ) : (
              <button
                onClick={handleSubmitQuiz}
                disabled={submitting}
                className="btn btn-success"
                style={{ minWidth: "150px", justifyContent: "center" }}
              >
                {submitting ? "Scoring..." : "Submit Quiz"}
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  // ── PHASE 3: RESULTS & EXPLANATIONS ────────────────────────────────────────
  if (phase === "results" && quizResult) {
    const isPassing = quizResult.percentage >= 60;

    return (
      <div className="practice-quiz-page">
        {/* Score Summary Card */}
        <div className="card text-center mb-6" style={{ padding: "36px 24px" }}>
          <div className={`score-circle ${isPassing ? "" : "warning"}`} style={{
            background: isPassing
              ? "linear-gradient(135deg, var(--success), var(--primary))"
              : "linear-gradient(135deg, var(--warning), var(--danger))"
          }}>
            <div className="score-number">{quizResult.percentage}%</div>
            <div className="score-label">{quizResult.score} / {quizResult.total} Correct</div>
          </div>

          <h2 style={{ fontSize: "24px", marginBottom: "8px" }}>
            {quizResult.percentage === 100
              ? "🎉 Perfect Score!"
              : isPassing
              ? "👏 Great Job!"
              : "💪 Keep Practicing!"}
          </h2>
          <p style={{ color: "var(--text-secondary)", maxWidth: "500px", margin: "0 auto 20px" }}>
            You completed the <strong>{quizResult.topic}</strong> practice quiz ({quizResult.difficulty} level).
            Review your answers and explanations below.
          </p>

          <div style={{ display: "flex", justifyContent: "center", gap: "16px", flexWrap: "wrap", marginBottom: "24px" }}>
            <div className="stat-card" style={{ padding: "12px 24px", minWidth: "140px" }}>
              <div style={{ textAlign: "center", width: "100%" }}>
                <div style={{ fontSize: "20px", fontWeight: "700", color: "var(--success)" }}>{quizResult.score}</div>
                <div style={{ fontSize: "12px", color: "var(--text-muted)" }}>Correct</div>
              </div>
            </div>
            <div className="stat-card" style={{ padding: "12px 24px", minWidth: "140px" }}>
              <div style={{ textAlign: "center", width: "100%" }}>
                <div style={{ fontSize: "20px", fontWeight: "700", color: "var(--danger)" }}>{quizResult.incorrect}</div>
                <div style={{ fontSize: "12px", color: "var(--text-muted)" }}>Incorrect</div>
              </div>
            </div>
            <div className="stat-card" style={{ padding: "12px 24px", minWidth: "140px" }}>
              <div style={{ textAlign: "center", width: "100%" }}>
                <div style={{ fontSize: "20px", fontWeight: "700", color: "var(--primary)" }}>{quizResult.total}</div>
                <div style={{ fontSize: "12px", color: "var(--text-muted)" }}>Total Questions</div>
              </div>
            </div>
          </div>

          <div style={{ display: "flex", justifyContent: "center", gap: "12px", flexWrap: "wrap" }}>
            <button
              onClick={handleTryAgain}
              className="btn btn-primary"
              style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
            >
              <RotateCcw size={16} /> Try Another Quiz
            </button>
            <Link
              to="/assessment-history"
              className="btn btn-secondary"
              style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
            >
              <History size={16} /> View in History
            </Link>
            <Link
              to="/assistant"
              className="btn btn-ghost"
              style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
            >
              <Sparkles size={16} /> Ask Career Assistant
            </Link>
          </div>
        </div>

        {/* Topics to Practice More (if mistakes occurred) */}
        {quizResult.topics_to_practice && quizResult.topics_to_practice.length > 0 && (
          <div className="alert alert-warning mb-6">
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
              <AlertCircle size={18} />
              <strong>Topics to Practice More:</strong>
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "8px" }}>
              {quizResult.topics_to_practice.map((topicItem, i) => (
                <span key={i} className="skill-tag warning">
                  {topicItem}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Detailed Question Review with Explanations */}
        <h3 style={{ fontSize: "18px", fontWeight: "700", marginBottom: "16px" }}>
          Detailed Answer Breakdown ({quizResult.results.length} Questions)
        </h3>

        <div className="flex-col gap-4">
          {quizResult.results.map((item, index) => {
            return (
              <div
                key={item.id}
                className="card"
                style={{
                  borderLeft: item.is_correct ? "4px solid var(--success)" : "4px solid var(--danger)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "10px", flexWrap: "wrap", gap: "8px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <span style={{ fontWeight: "700", fontSize: "15px" }}>Question {index + 1}</span>
                    <span className="badge badge-primary">{item.skill}</span>
                    <span className="badge badge-medium">{item.difficulty}</span>
                  </div>
                  <div>
                    {item.is_correct ? (
                      <span className="badge badge-low" style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}>
                        <CheckCircle size={14} /> Correct
                      </span>
                    ) : (
                      <span className="badge badge-high" style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}>
                        <XCircle size={14} /> Incorrect
                      </span>
                    )}
                  </div>
                </div>

                <p style={{ fontSize: "15px", fontWeight: "600", marginBottom: "16px" }}>
                  {item.question}
                </p>

                {/* Option Choices */}
                <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginBottom: "16px" }}>
                  {Object.entries(item.options).map(([letter, text]) => {
                    const isChosen = item.chosen === letter;
                    const isCorrect = item.correct === letter;

                    let optionClass = "review-option";
                    if (isCorrect) optionClass += " correct-opt";
                    else if (isChosen && !isCorrect) optionClass += " wrong-opt";

                    return (
                      <div key={letter} className={optionClass}>
                        <div className="opt-marker">
                          {letter}
                        </div>
                        <div style={{ flex: 1, fontSize: "14px" }}>
                          {text}
                        </div>
                        {isChosen && !isCorrect && (
                          <span style={{ fontSize: "12px", color: "var(--danger)", fontWeight: "600" }}>
                            Your Choice ✕
                          </span>
                        )}
                        {isCorrect && (
                          <span style={{ fontSize: "12px", color: "var(--success)", fontWeight: "600" }}>
                            {isChosen ? "Your Choice ✓" : "Correct Answer ✓"}
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>

                {/* Explanations Area */}
                <div className="explanation-box">
                  <div style={{ marginBottom: item.why_wrong ? "8px" : "0" }}>
                    <strong style={{ color: "var(--success)", fontSize: "13px" }}>
                      💡 Explanation (Why {item.correct} is correct):
                    </strong>
                    <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "4px", lineHeight: "1.5" }}>
                      {item.explanation}
                    </p>
                  </div>

                  {item.why_wrong && (
                    <div style={{ borderTop: "1px dashed var(--border)", paddingTop: "8px", marginTop: "8px" }}>
                      <strong style={{ color: "var(--warning)", fontSize: "13px" }}>
                        ⚠️ Common Misconception:
                      </strong>
                      <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "4px", lineHeight: "1.5" }}>
                        {item.why_wrong}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  return null;
}
