import { createContext, useContext, useEffect, useState } from 'react';

// Theme context for managing dark/light mode
const ThemeContext = createContext({
  isDark: true, // Default to dark theme as per requirements
  toggleTheme: () => {},
  setTheme: () => {}
});

// Custom hook to use theme context
export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

// Theme provider component
export function ThemeProvider({ children }) {
  // Initialize with dark theme as default (per requirements)
  const [isDark, setIsDark] = useState(() => {
    // Check localStorage for saved preference, default to dark
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('theme');
      return saved ? saved === 'dark' : true; // Default to dark theme
    }
    return true;
  });

  // Apply theme class to document element
  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    
    // Save preference to localStorage
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  // Toggle between dark and light themes
  const toggleTheme = () => {
    setIsDark(prev => !prev);
  };

  // Set specific theme
  const setTheme = (theme) => {
    setIsDark(theme === 'dark');
  };

  const value = {
    isDark,
    toggleTheme,
    setTheme
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

export default ThemeContext;
