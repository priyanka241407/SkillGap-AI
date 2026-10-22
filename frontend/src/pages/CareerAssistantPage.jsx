import { useState, useEffect, useRef } from "react";
import { sendAssistantMessage, getAssistantSuggestions } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { Bot, Send, Trash2, Sparkles, AlertCircle, RefreshCw, User, ArrowRight } from "lucide-react";
import toast from "react-hot-toast";

/**
 * Simple markdown formatter for assistant messages:
 * supports bold (**text**), headers (### text), bullet points (- text), numbered lists (1. text), and links ([text](url)).
 */
function FormattedMessage({ content }) {
  if (!content) return null;

  const lines = content.split("\n");
  const renderedElements = [];

  const parseInline = (text) => {
    // Replace markdown links: [text](url)
    const parts = [];
    const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
    let lastIndex = 0;
    let match;

    while ((match = linkRegex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        parts.push(renderBoldItalic(text.substring(lastIndex, match.index)));
      }
      parts.push(
        <a
          key={match.index}
          href={match[2]}
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: "var(--primary)", textDecoration: "underline", fontWeight: "600" }}
        >
          {match[1]}
        </a>
      );
      lastIndex = linkRegex.lastIndex;
    }

    if (lastIndex < text.length) {
      parts.push(renderBoldItalic(text.substring(lastIndex)));
    }

    return parts;
  };

  const renderBoldItalic = (text) => {
    // Replace **bold**
    const boldParts = text.split(/(\*\*[^*]+\*\*)/g);
    return boldParts.map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return <strong key={i}>{part.slice(2, -2)}</strong>;
      }
      // Replace *italic*
      if (part.startsWith("*") && part.endsWith("*")) {
        return <em key={i}>{part.slice(1, -1)}</em>;
      }
      // Replace `code`
      if (part.startsWith("`") && part.endsWith("`")) {
        return <code key={i} style={{ background: "rgba(99,102,241,.12)", padding: "2px 6px", borderRadius: "4px", fontSize: "0.9em" }}>{part.slice(1, -1)}</code>;
      }
      return part;
    });
  };

  lines.forEach((line, idx) => {
    const trimmed = line.trim();
    if (!trimmed) {
      renderedElements.push(<div key={`sp-${idx}`} style={{ height: "10px" }} />);
      return;
    }

    if (trimmed.startsWith("### ")) {
      renderedElements.push(
        <h4 key={idx} style={{ margin: "14px 0 8px", fontSize: "16px", fontWeight: "700", color: "var(--text-primary)" }}>
          {parseInline(trimmed.substring(4))}
        </h4>
      );
    } else if (trimmed.startsWith("- ")) {
      renderedElements.push(
        <li key={idx} style={{ marginLeft: "20px", marginBottom: "4px", listStyleType: "disc" }}>
          {parseInline(trimmed.substring(2))}
        </li>
      );
    } else if (/^\d+\.\s/.test(trimmed)) {
      const match = trimmed.match(/^(\d+\.)\s(.*)/);
      renderedElements.push(
        <div key={idx} style={{ display: "flex", gap: "8px", marginBottom: "6px" }}>
          <span style={{ fontWeight: "700", color: "var(--primary)", minWidth: "18px" }}>{match[1]}</span>
          <div>{parseInline(match[2])}</div>
        </div>
      );
    } else {
      renderedElements.push(
        <p key={idx} style={{ marginBottom: "6px", lineHeight: "1.6" }}>
          {parseInline(trimmed)}
        </p>
      );
    }
  });

  return <div>{renderedElements}</div>;
}

export default function CareerAssistantPage() {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([
    "What skills do I need to become a Data Analyst?",
    "How can I improve my Python skills?",
    "Create a beginner-friendly roadmap for a Machine Learning Engineer.",
    "Which projects should I add to my resume?",
    "How can I prepare for technical interviews?",
  ]);
  const [userCareerGoal, setUserCareerGoal] = useState("");
  const [backendError, setBackendError] = useState(false);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const initialWelcome = {
    id: "welcome",
    sender: "assistant",
    time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    text: `Hello ${user?.name ? user.name.split(" ")[0] : "Student"}! 👋 I am your **SkillGap AI Career Assistant**.\n\nI can help you understand the skills required for tech roles, provide tailored roadmaps, suggest impressive resume projects, and prepare for technical interviews.\n\n*Note: I provide rule-based career guidance grounded in industry benchmarks and your profile data.* Click any suggestion below to start!`,
  };

  useEffect(() => {
    // Initialize welcome message
    setMessages([initialWelcome]);

    // Fetch contextual suggestions
    getAssistantSuggestions()
      .then((res) => {
        if (res.data?.suggestions && res.data.suggestions.length > 0) {
          setSuggestions(res.data.suggestions);
        }
        if (res.data?.career_goal) {
          setUserCareerGoal(res.data.career_goal);
        }
        setBackendError(false);
      })
      .catch((err) => {
        console.error("Could not fetch assistant suggestions:", err);
        if (!err.response) {
          setBackendError(true);
        }
      });
  }, [user]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (messageText) => {
    const textToSend = (messageText || input).trim();
    if (!textToSend || loading) return;

    const userMsg = {
      id: "u-" + Date.now(),
      sender: "user",
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      text: textToSend,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    setBackendError(false);

    try {
      const res = await sendAssistantMessage(textToSend);
      const assistantMsg = {
        id: "a-" + Date.now(),
        sender: "assistant",
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        text: res.data.reply,
        followups: res.data.suggested_followups || [],
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error("Chat error:", err);
      const errorMessage =
        !err.response
          ? "Unable to connect to the backend server. Please make sure the Flask backend is running on port 5000."
          : (err.response?.data?.error || "Sorry, I encountered an error while processing your request. Please try again.");

      setBackendError(!err.response);
      toast.error(errorMessage);

      setMessages((prev) => [
        ...prev,
        {
          id: "err-" + Date.now(),
          sender: "assistant",
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          text: `⚠️ **Error**: ${errorMessage}`,
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        ...initialWelcome,
        id: "welcome-" + Date.now(),
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);
    toast.success("Chat history cleared");
    if (inputRef.current) inputRef.current.focus();
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="career-assistant-container">
      {/* Page Header */}
      <div className="page-header assistant-header">
        <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
          <div className="assistant-header-icon">
            <Bot size={28} />
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
              <h1 style={{ margin: 0, fontSize: "24px" }}>AI Career Assistant</h1>
              <span className="badge badge-primary" style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}>
                <Sparkles size={12} /> Rule-Based Guidance
              </span>
              {userCareerGoal && (
                <span className="badge badge-medium" style={{ textTransform: "none" }}>
                  Target: <strong>{userCareerGoal}</strong>
                </span>
              )}
            </div>
            <p style={{ margin: "4px 0 0", fontSize: "14px", color: "var(--text-secondary)" }}>
              Ask questions about career paths, technical skills, projects, and interview preparation.
            </p>
          </div>
        </div>

        <button
          onClick={handleClearChat}
          className="btn btn-ghost btn-sm"
          title="Clear all messages in this conversation"
          style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
        >
          <Trash2 size={15} /> Clear Chat
        </button>
      </div>

      {/* Backend connection warning if offline */}
      {backendError && (
        <div className="alert alert-danger" style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <AlertCircle size={18} style={{ flexShrink: 0 }} />
          <div>
            <strong>Backend Connection Offline:</strong> The assistant cannot reach <code>http://localhost:5000</code>.
            Please ensure the Flask backend is running (<code>python app.py</code>).
          </div>
        </div>
      )}

      {/* Chat Messages Card */}
      <div className="card chat-card">
        <div className="chat-messages-area">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`chat-bubble-row ${msg.sender === "user" ? "user-row" : "assistant-row"}`}
            >
              <div className="chat-avatar">
                {msg.sender === "user" ? (
                  <User size={18} />
                ) : (
                  <Bot size={18} />
                )}
              </div>
              <div className={`chat-bubble ${msg.sender === "user" ? "user-bubble" : "assistant-bubble"} ${msg.isError ? "error-bubble" : ""}`}>
                <div className="chat-bubble-header">
                  <span className="chat-sender-name">
                    {msg.sender === "user" ? "You" : "Career Assistant"}
                  </span>
                  <span className="chat-timestamp">{msg.time}</span>
                </div>
                <div className="chat-bubble-body">
                  <FormattedMessage content={msg.text} />
                </div>

                {/* Follow-up suggestions if assistant provided them */}
                {msg.followups && msg.followups.length > 0 && (
                  <div className="chat-followups">
                    <span className="followup-title">Suggested follow-ups:</span>
                    <div className="followup-chips">
                      {msg.followups.map((q, idx) => (
                        <button
                          key={idx}
                          className="followup-chip"
                          onClick={() => handleSend(q)}
                          disabled={loading}
                        >
                          <span>{q}</span>
                          <ArrowRight size={12} />
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Typing Indicator */}
          {loading && (
            <div className="chat-bubble-row assistant-row">
              <div className="chat-avatar">
                <Bot size={18} />
              </div>
              <div className="chat-bubble assistant-bubble typing-bubble">
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
                <span style={{ fontSize: "12px", color: "var(--text-muted)", marginLeft: "8px" }}>
                  Generating response...
                </span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Questions Section */}
        {suggestions.length > 0 && (
          <div className="chat-suggestions-tray">
            <span className="suggestions-tray-label">
              <Sparkles size={13} style={{ display: "inline", verticalAlign: "middle", marginRight: "4px" }} />
              Suggested questions:
            </span>
            <div className="suggestions-chips-wrapper">
              {suggestions.map((q, index) => (
                <button
                  key={index}
                  className="suggestion-chip-btn"
                  onClick={() => handleSend(q)}
                  disabled={loading}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input Bar */}
        <div className="chat-input-bar">
          <textarea
            ref={inputRef}
            rows={1}
            className="chat-textarea"
            placeholder="Ask a question about skills, roadmaps, projects, or interviews... (Press Enter to send)"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button
            type="button"
            className="btn btn-primary chat-send-btn"
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
          >
            {loading ? <RefreshCw size={16} className="spin-icon" /> : <Send size={16} />}
            <span>Send</span>
          </button>
        </div>
      </div>
    </div>
  );
}
