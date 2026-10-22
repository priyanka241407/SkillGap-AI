/**
 * API Service - handles all communication with the Flask backend.
 * Base URL is http://localhost:5000
 */

import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:5000/api",
  headers: { "Content-Type": "application/json" },
});

// ── JWT Token Injection ────────────────────────────────────────────────────────
// Automatically add the JWT token to every request if the user is logged in
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("skillgap_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Auth ──────────────────────────────────────────────────────────────────────
export const register = (data) => API.post("/auth/register", data);
export const login = (data) => API.post("/auth/login", data);
export const getMe = () => API.get("/auth/me");

// ── Profile ───────────────────────────────────────────────────────────────────
export const getProfile = () => API.get("/profile/");
export const updateProfile = (data) => API.put("/profile/", data);

// ── Resume ────────────────────────────────────────────────────────────────────
export const uploadResume = (formData) =>
  API.post("/resume/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
export const getSkills = () => API.get("/resume/skills");
export const updateSkills = (skills) => API.put("/resume/skills", { skills });

// ── Test ──────────────────────────────────────────────────────────────────────
export const getTestQuestions = () => API.get("/test/questions");
export const submitTest = (answers) => API.post("/test/submit", { answers });
export const getTestResults = () => API.get("/test/results");

// ── Analysis ──────────────────────────────────────────────────────────────────
export const getJobRoles = () => API.get("/analysis/job-roles");
export const runAnalysis = () => API.post("/analysis/run");
export const getAnalysisResult = () => API.get("/analysis/result");
export const getRecommendations = (params) =>
  API.get("/analysis/recommendations", { params });
export const updateProgress = (skill, status) =>
  API.post("/analysis/roadmap/progress", { skill, status });
export const getProgress = () => API.get("/analysis/roadmap/progress");
export const getHistory = () => API.get("/analysis/history");
export const deleteHistoryItem = (id) => API.delete(`/analysis/history/${id}`);
export const clearAllHistory = () => API.delete("/analysis/history");
export const getDashboard = () => API.get("/analysis/dashboard");

// ── Career Assistant ──────────────────────────────────────────────────────────
export const sendAssistantMessage = (message, history = []) =>
  API.post("/assistant/chat", { message, history });
export const getAssistantSuggestions = () =>
  API.get("/assistant/suggestions");

// ── Practice Quiz ─────────────────────────────────────────────────────────────
export const getQuizTopics = () => API.get("/quiz/topics");
export const getQuizQuestions = (params) => API.get("/quiz/questions", { params });
export const submitQuiz = (data) => API.post("/quiz/submit", data);

// ── Assessment History ────────────────────────────────────────────────────────
export const getAssessmentHistory = (params) => API.get("/assessment/history", { params });
export const getAssessmentDetail = (id) => API.get(`/assessment/history/${id}`);
export const deleteAssessmentAttempt = (id) => API.delete(`/assessment/history/${id}`);

