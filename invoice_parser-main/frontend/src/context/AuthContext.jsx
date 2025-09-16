import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

// Custom hook to use authentication context
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Authentication provider component
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('authToken'));

  // Base API URL - configured via environment variables
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  // Initialize authentication state on app load
  useEffect(() => {
    if (token) {
      // Verify token and get user info
      verifyToken();
    } else {
      setLoading(false);
    }
  }, [token]);

  // API request helper with error handling
  const apiRequest = async (endpoint, options = {}) => {
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return { success: true, data };
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      return { 
        success: false, 
        error: error.message || 'Network error. Please check your connection and try again.' 
      };
    }
  };

  // Verify token and get user information
  const verifyToken = async () => {
    const result = await apiRequest('/api/auth/me');
    
    if (result.success) {
      setUser(result.data);
    } else {
      // Token is invalid, clear it
      console.warn('Token verification failed:', result.error);
      logout();
    }
    
    setLoading(false);
  };

  // Login function
  const login = async (credentials) => {
    setLoading(true);
    
    const result = await apiRequest('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });

    setLoading(false);

    if (result.success) {
      setUser(result.data.user);
      setToken(result.data.access_token);
      localStorage.setItem('authToken', result.data.access_token);
      return { success: true, user: result.data.user };
    } else {
      return { success: false, error: result.error };
    }
  };

  // Register function
  const register = async (userData) => {
    setLoading(true);
    
    const result = await apiRequest('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });

    setLoading(false);

    if (result.success) {
      setUser(result.data.user);
      setToken(result.data.access_token);
      localStorage.setItem('authToken', result.data.access_token);
      return { success: true, user: result.data.user };
    } else {
      return { success: false, error: result.error };
    }
  };

  // Logout function
  const logout = async () => {
    try {
      if (token) {
        await apiRequest('/api/auth/logout', {
          method: 'POST',
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setToken(null);
      localStorage.removeItem('authToken');
    }
  };

  // Get user status (new user vs returning user)
  const getUserStatus = async () => {
    if (!token) return null;
    
    const result = await apiRequest('/api/user/status');
    
    if (result.success) {
      return result.data;
    } else {
      console.warn('Failed to get user status:', result.error);
      return null;
    }
  };

  // Get user invoice count
  const getUserInvoiceCount = async () => {
    if (!token) return null;
    
    const result = await apiRequest('/api/user/invoice-count');
    
    if (result.success) {
      return result.data;
    } else {
      console.warn('Failed to get user invoice count:', result.error);
      return null;
    }
  };

  // Refresh user data
  const refreshUser = async () => {
    if (!token) return;
    
    const result = await apiRequest('/api/auth/me');
    
    if (result.success) {
      setUser(result.data);
      return result.data;
    } else {
      console.warn('Failed to refresh user data:', result.error);
      return null;
    }
  };

  // Context value
  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    getUserStatus,
    getUserInvoiceCount,
    refreshUser,
    apiRequest // Expose for other components to use
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}