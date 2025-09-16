import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useNotification } from '../../context/NotificationContext';
import Modal from '../ui/Modal';
import Button from '../ui/Button';
import Input from '../ui/Input';

// Global state for modal visibility (simple approach for beginner-friendly code)
let setGlobalLoginModal = null;

export function openLoginModal() {
  if (setGlobalLoginModal) {
    setGlobalLoginModal(true);
  }
}

export function closeLoginModal() {
  if (setGlobalLoginModal) {
    setGlobalLoginModal(false);
  }
}

// Login modal component
function LoginModal() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, getUserStatus, getUserInvoiceCount } = useAuth();
  const { showSuccess, showError, showInfo } = useNotification();
  
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  // Set up global modal control
  useEffect(() => {
    setGlobalLoginModal = setIsOpen;
    return () => {
      setGlobalLoginModal = null;
    };
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const determineUserRoute = async () => {
    try {
      // Try to get user invoice count first
      const invoiceCount = await getUserInvoiceCount();
      
      if (invoiceCount && invoiceCount.count > 0) {
        return '/dashboard'; // User has processed invoices
      }
      
      // Fallback to user status check
      const userStatus = await getUserStatus();
      
      if (userStatus && userStatus.is_new_user) {
        return '/process'; // New user
      }
      
      return '/dashboard'; // Default to dashboard
    } catch (error) {
      console.warn('Error determining user route:', error);
      return '/dashboard'; // Fallback
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    
    try {
      const result = await login(formData);
      
      if (result.success) {
        showSuccess(
          `Welcome back, ${result.user.name}!`,
          'Login Successful'
        );
        
        handleClose();
        
        // Determine where to route the user
        const targetRoute = await determineUserRoute();
        
        // Check if user was trying to access a protected route
        const from = location.state?.from?.pathname || targetRoute;
        
        navigate(from, { replace: true });
      } else {
        showError(result.error, 'Login Failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      showError('An unexpected error occurred. Please try again.', 'Error');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setIsOpen(false);
    setFormData({ email: '', password: '' });
    setErrors({});
    setLoading(false);
  };

  const handleSwitchToRegister = () => {
    handleClose();
    navigate('/register');
  };

  const handleForgotPassword = () => {
    showInfo(
      'Password reset functionality will be available soon. Please contact support if you need immediate assistance.',
      'Coming Soon'
    );
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Welcome Back"
      showCloseButton={false}
    >
      <div className="space-y-6">
        {/* Welcome Message */}
        <div className="text-center">
          <p className="text-sm text-gray-600 dark:text-gray-300">
            Sign in to your account to continue processing invoices
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Email"
            name="email"
            type="email"
            required
            value={formData.email}
            onChange={handleChange}
            error={errors.email}
            placeholder="Enter your email"
            className="transition-all duration-200"
            autoFocus
          />

          <Input
            label="Password"
            name="password"
            type="password"
            required
            value={formData.password}
            onChange={handleChange}
            error={errors.password}
            placeholder="Enter your password"
            className="transition-all duration-200"
          />

          {/* Forgot Password Link */}
          <div className="text-right">
            <button
              type="button"
              className="text-sm text-violet-600 hover:text-violet-500 transition-colors"
              onClick={handleForgotPassword}
            >
              Forgot your password?
            </button>
          </div>

          <div className="pt-4">
            <Button
              type="submit"
              className="w-full py-2.5 text-base font-semibold"
              loading={loading}
              disabled={loading}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </Button>
          </div>
        </form>

        {/* Register Link */}
        <div className="pt-4 border-t border-gray-200">
          <div className="text-center">
            <p className="text-sm text-gray-600 dark:text-gray-300">
              Don't have an account?{' '}
              <button
                type="button"
                onClick={handleSwitchToRegister}
                className="font-medium text-violet-600 hover:text-violet-500 transition-colors"
                disabled={loading}
              >
                Create free account
              </button>
            </p>
          </div>
        </div>

        {/* Trust Indicators */}
        <div className="pt-4 border-t border-gray-200">
          <div className="flex items-center justify-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
              <span>Secure Login</span>
            </div>
            <div className="w-px h-3 bg-gray-300"></div>
            <div className="flex items-center">
              <div className="w-2 h-2 bg-blue-500 rounded-full mr-1"></div>
              <span>256-bit SSL</span>
            </div>
          </div>
        </div>
      </div>
    </Modal>
  );
}

export default LoginModal;