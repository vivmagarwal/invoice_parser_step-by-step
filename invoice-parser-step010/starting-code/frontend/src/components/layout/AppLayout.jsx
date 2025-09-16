import { useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Navbar from './Navbar';

// Layout component that conditionally shows navbar
function AppLayout({ children }) {
  const location = useLocation();
  const { isAuthenticated } = useAuth();

  // Routes where navbar should NOT be shown
  const publicRoutes = ['/', '/register'];
  
  // Determine if navbar should be shown
  const showNavbar = isAuthenticated && !publicRoutes.includes(location.pathname);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Conditionally render navbar */}
      {showNavbar && <Navbar />}
      
      {/* Main content */}
      <main className={showNavbar ? '' : 'min-h-screen'}>
        {children}
      </main>
    </div>
  );
}

export default AppLayout;
