import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import { AppLayout, ProtectedRoute } from "./components/Layout";
import { Toaster } from "react-hot-toast";

// Pages
import LandingPage from "./pages/LandingPage";
import { LoginPage, RegisterPage } from "./pages/AuthPages";
import Dashboard from "./pages/Dashboard";
import ProfilePage from "./pages/ProfilePage";
import ResumePage from "./pages/ResumePage";
import TestPage from "./pages/TestPage";
import AnalysisPage from "./pages/AnalysisPage";
import CareerAssistantPage from "./pages/CareerAssistantPage";
import PracticeQuizPage from "./pages/PracticeQuizPage";
import AssessmentHistoryPage from "./pages/AssessmentHistoryPage";
import CoursesPage from "./pages/CoursesPage";
import RoadmapPage from "./pages/RoadmapPage";
import HistoryPage from "./pages/HistoryPage";

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <Toaster position="top-center" toastOptions={{ duration: 3000 }} />
          <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected Routes (inside AppLayout) */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <AppLayout>
                  <Dashboard />
                </AppLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <AppLayout>
                  <ProfilePage />
                </AppLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/resume"
            element={
              <ProtectedRoute>
                <AppLayout>
                  <ResumePage />
                </AppLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/test"
            element={
              <ProtectedRoute>
                <AppLayout>
                  <TestPage />
                </AppLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/analysis"
            element={
              <ProtectedRoute>
                <AppLayout>
                  <AnalysisPage />
                </AppLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/assistant"
            element={
              <ProtectedRoute>
                <AppLayout>
                  <CareerAssistantPage />
                </AppLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/quiz"
            element={
              <ProtectedRoute>
                <AppLayout>
                  <PracticeQuizPage />
                </AppLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/assessment-history"
            element={
              <ProtectedRoute>
                <AppLayout>
                  <AssessmentHistoryPage />
                </AppLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/courses"
            element={
              <ProtectedRoute>
                <AppLayout>
                  <CoursesPage />
                </AppLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/roadmap"
            element={
              <ProtectedRoute>
                <AppLayout>
                  <RoadmapPage />
                </AppLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/history"
            element={
              <ProtectedRoute>
                <AppLayout>
                  <HistoryPage />
                </AppLayout>
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
