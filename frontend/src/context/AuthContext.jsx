/**
 * AuthContext - provides user authentication state to the entire app.
 * Wraps the app so any component can check if user is logged in.
 */

import { createContext, useContext, useState, useEffect } from "react";
import { getMe } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true); // True while checking auth on startup

  // On app load, check if there's a saved token and fetch user info
  useEffect(() => {
    const token = localStorage.getItem("skillgap_token");
    if (token) {
      getMe()
        .then((res) => setUser(res.data))
        .catch(() => {
          // Token is invalid or expired
          localStorage.removeItem("skillgap_token");
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const loginUser = (token, userData) => {
    localStorage.setItem("skillgap_token", token);
    setUser(userData);
  };

  const logoutUser = () => {
    localStorage.removeItem("skillgap_token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, loginUser, logoutUser }}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook for easy access
export function useAuth() {
  return useContext(AuthContext);
}
