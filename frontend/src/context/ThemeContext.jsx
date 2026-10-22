/**
 * ThemeContext - manages light and dark mode for SkillGap AI.
 * Persists the choice in localStorage and toggles 'data-theme' on <html>.
 */

import { createContext, useContext, useState, useEffect } from "react";

const ThemeContext = createContext(null);

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    // Check saved theme in localStorage
    const savedTheme = localStorage.getItem("skillgap_theme");
    if (savedTheme === "dark" || savedTheme === "light") {
      return savedTheme;
    }
    // Default to light mode for student project
    return "light";
  });

  useEffect(() => {
    // Apply data-theme attribute on documentElement
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("skillgap_theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === "light" ? "dark" : "light"));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

// Custom hook to access theme
export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
}
