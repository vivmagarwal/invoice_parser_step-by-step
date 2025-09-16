import { createContext, useContext, useState } from 'react';
import ToastContainer from '../components/ui/Toast';

// Notification Context
const NotificationContext = createContext();

export function useNotification() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within NotificationProvider');
  }
  return context;
}

// Toast notification helper functions

// Notification Provider component
export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([]);

  const addNotification = (notification) => {
    const id = Date.now() + Math.random();
    const newNotification = { 
      ...notification, 
      id,
      duration: notification.duration || 5000
    };
    setNotifications(prev => [...prev, newNotification]);
    
    return id;
  };

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  };

  const showSuccess = (message, title, duration) => {
    return addNotification({ type: 'success', message, title, duration });
  };

  const showError = (message, title, duration) => {
    return addNotification({ type: 'error', message, title, duration });
  };

  const showInfo = (message, title, duration) => {
    return addNotification({ type: 'info', message, title, duration });
  };

  const showWarning = (message, title, duration) => {
    return addNotification({ type: 'warning', message, title, duration });
  };

  const clearAll = () => {
    setNotifications([]);
  };

  const contextValue = {
    notifications,
    showSuccess,
    showError,
    showInfo,
    showWarning,
    removeNotification,
    clearAll
  };

  return (
    <NotificationContext.Provider value={contextValue}>
      {children}
      
      {/* Toast container */}
      <ToastContainer
        toasts={notifications}
        onRemove={removeNotification}
      />
    </NotificationContext.Provider>
  );
}
