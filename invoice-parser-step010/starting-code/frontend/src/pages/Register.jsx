import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useNotification } from '../context/NotificationContext';
import { DocumentTextIcon, CheckCircleIcon } from '../components/ui/Icons';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import { openLoginModal } from '../components/forms/LoginModal';

function Register() {
  const navigate = useNavigate();
  const { register, getUserStatus, getUserInvoiceCount } = useAuth();
  const { showSuccess, showError } = useNotification();
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: ''
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

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
    
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    } else if (formData.name.length < 2) {
      newErrors.name = 'Name must be at least 2 characters';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    
    try {
      const result = await register(formData);
      
      if (result.success) {
        showSuccess(
          `Welcome, ${result.user.name}! Your account has been created successfully.`,
          'Account Created'
        );
        
        // For new registrations, route directly to processing
        // since they haven't processed any invoices yet
        navigate('/process');
      } else {
        showError(result.error, 'Registration Failed');
      }
    } catch (error) {
      showError('An unexpected error occurred. Please try again.', 'Error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-50 to-blue-50 dark:from-violet-900/20 dark:to-blue-900/20 dark:bg-gray-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <Link to="/" className="flex justify-center items-center group">
          <div className="w-10 h-10 bg-gradient-to-br from-violet-500 to-purple-600 rounded-lg flex items-center justify-center group-hover:scale-105 transition-transform">
            <DocumentTextIcon className="h-6 w-6 text-white" />
          </div>
          <span className="ml-3 text-2xl font-bold text-gray-900 dark:text-gray-100">Invoice Parser</span>
        </Link>
        
        <h2 className="mt-8 text-center text-3xl font-bold text-gray-900 dark:text-gray-100">
          Try it for yoursel!
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-300">
          Join 10,000+ businesses automating their invoice processing
        </p>
      </div>

      {/* Registration Form */}
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white dark:bg-gray-800 py-8 px-4 shadow-xl rounded-lg sm:px-10 border border-gray-100 dark:border-gray-700">
          <form onSubmit={handleSubmit} className="space-y-6">
            <Input
              label="Full Name"
              name="name"
              type="text"
              required
              value={formData.name}
              onChange={handleChange}
              error={errors.name}
              placeholder="Your full name"
              className="transition-all duration-200"
            />

            <Input
              label="Work Email"
              name="email"
              type="email"
              required
              value={formData.email}
              onChange={handleChange}
              error={errors.email}
              placeholder="you@company.com"
              className="transition-all duration-200"
            />

            <Input
              label="Password"
              name="password"
              type="password"
              required
              value={formData.password}
              onChange={handleChange}
              error={errors.password}
              placeholder="Create a secure password"
              className="transition-all duration-200"
            />

            <div className="pt-2">
              <Button
                type="submit"
                className="w-full py-3 text-base font-semibold"
                loading={loading}
                disabled={loading}
              >
                {loading ? 'Creating Account...' : 'Create Account & Start Processing'}
              </Button>
            </div>
          </form>

          {/* Login Link */}
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">Already have an account?</span>
              </div>
            </div>

            <div className="mt-4 text-center">
              <button 
                onClick={openLoginModal}
                className="font-medium text-violet-600 hover:text-violet-500 transition-colors"
              >
                Sign in to your account
              </button>
            </div>
          </div>

          {/* Trust Indicators */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="flex items-center justify-center space-x-4 text-xs text-gray-500">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-500 rounded-full mr-1"></div>
                <span>SOC 2 Secure</span>
              </div>
              <div className="w-px h-4 bg-gray-300"></div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-blue-500 rounded-full mr-1"></div>
                <span>GDPR Compliant</span>
              </div>
              <div className="w-px h-4 bg-gray-300"></div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-purple-500 rounded-full mr-1"></div>
                <span>256-bit SSL</span>
              </div>
            </div>
          </div>
        </div>

        {/* Additional Trust Signals */}
        <div className="mt-8 text-center">
          <p className="text-xs text-gray-500">
            By creating an account, you agree to our{' '}
            <a href="#" className="text-violet-600 hover:text-violet-500">Terms of Service</a>
            {' '}and{' '}
            <a href="#" className="text-violet-600 hover:text-violet-500">Privacy Policy</a>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Register;