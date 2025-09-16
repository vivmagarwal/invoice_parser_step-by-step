import { Link } from 'react-router-dom';
import { openLoginModal } from '../components/forms/LoginModal';
import { 
  DocumentTextIcon, 
  CpuChipIcon, 
  CloudUploadIcon,
  CheckCircleIcon,
  ArrowRightIcon,
  PlayIcon,
  ShieldCheckIcon,
  BoltIcon,
  ChartBarIcon
} from '../components/ui/Icons';
import Button from '../components/ui/Button';

// Landing page component with production-ready SaaS design
function Landing() {

  return (
    <div className="min-h-screen bg-white dark:bg-gray-800 dark:bg-gray-900">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white dark:bg-gray-800 dark:bg-gray-800 border-b border-gray-100 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <div className="w-8 h-8 bg-gradient-to-br from-violet-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <DocumentTextIcon className="h-5 w-5 text-white" />
                </div>
                <h1 className="ml-3 text-xl font-bold text-gray-900 dark:text-gray-100 dark:text-gray-100">Invoice Parser</h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link to="/register">
                <Button size="sm">
                  Try for Free
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-violet-50 via-white to-blue-50 dark:from-violet-900/20 dark:via-gray-900 dark:to-blue-900/20 pt-16 pb-20 sm:pt-24 sm:pb-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:grid lg:grid-cols-12 lg:gap-8 items-center">
            <div className="sm:text-center md:max-w-2xl md:mx-auto lg:col-span-6 lg:text-left">
              {/* Trust Badge */}
              <div className="inline-flex items-center bg-violet-100 dark:bg-violet-900/30 text-violet-800 dark:text-violet-300 text-sm font-medium px-3 py-1 rounded-full mb-6">
                <ShieldCheckIcon className="h-4 w-4 mr-2" />
                SOC 2 Compliant • GDPR Ready
              </div>
              
              {/* Main Headline */}
              <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100 dark:text-gray-100 tracking-tight sm:text-5xl lg:text-6xl">
                Process invoices in{' '}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-600 to-purple-600">
                  seconds
                </span>
                {' '}not hours
              </h1>
              
              {/* Subheadline */}
              <p className="mt-6 text-xl text-gray-600 dark:text-gray-300 dark:text-gray-300 max-w-3xl">
                AI-powered OCR technology that extracts data from your invoices automatically. 
                Reduce manual data entry by <strong>95%</strong> and eliminate costly errors.
              </p>

              {/* Key Benefits */}
              <div className="mt-8 space-y-3">
                <div className="flex items-center text-gray-700 dark:text-gray-300">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-3" />
                  <span>Process 100+ invoices per hour</span>
                </div>
                <div className="flex items-center text-gray-700 dark:text-gray-300">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-3" />
                  <span>99.5% accuracy with AI validation</span>
                </div>
                <div className="flex items-center text-gray-700 dark:text-gray-300">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-3" />
                  <span>Secure cloud processing & storage</span>
                </div>
              </div>

              {/* CTA Buttons */}
              <div className="mt-10 sm:flex sm:justify-center lg:justify-start">
                <div className="rounded-md shadow">
                  <Link to="/register">
                    <Button size="xl" className="w-full sm:w-auto px-8 py-4 text-lg">
                      Start Processing
                    </Button>
                  </Link>
                </div>
              </div>

            </div>

            {/* Hero Image/Demo - Stacked Invoices */}
            <div className="mt-12 relative sm:max-w-lg sm:mx-auto lg:mt-0 lg:max-w-none lg:mx-0 lg:col-span-6 lg:flex lg:items-center">
              <div className="relative mx-auto w-full lg:max-w-md">
                {/* Stack of Invoice Demos */}
                <div className="relative h-96 w-80 mx-auto">
                  
                  {/* Bottom Invoice - Least visible */}
                  <div className="absolute inset-0 bg-white dark:bg-gray-800 rounded-lg border-2 border-gray-200 dark:border-gray-700 p-6 shadow-lg transform rotate-12 translate-x-4 translate-y-4 z-10 opacity-70">
                    <div className="border-b border-gray-200 dark:border-gray-700 pb-4 mb-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">INVOICE</h3>
                          <p className="text-sm text-gray-600 dark:text-gray-400">#INV-2024-003</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-gray-600 dark:text-gray-400">Date: 2024-12-07</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Marketing Services</span>
                        <span className="font-medium dark:text-gray-200">$1,800.00</span>
                      </div>
                      <div className="border-t dark:border-gray-600 pt-3 flex justify-between font-semibold">
                        <span className="dark:text-gray-200">Total</span>
                        <span className="text-violet-600 dark:text-violet-400">$1,800.00</span>
                      </div>
                    </div>
                  </div>

                  {/* Middle Invoice */}
                  <div className="absolute inset-0 bg-white dark:bg-gray-800 rounded-lg border-2 border-gray-200 dark:border-gray-700 p-6 shadow-xl transform rotate-6 translate-x-2 translate-y-2 z-20 opacity-85">
                    <div className="border-b border-gray-200 dark:border-gray-700 pb-4 mb-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">INVOICE</h3>
                          <p className="text-sm text-gray-600 dark:text-gray-400">#INV-2024-002</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-gray-600 dark:text-gray-400">Date: 2024-12-06</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Consulting Services</span>
                        <span className="font-medium dark:text-gray-200">$2,200.00</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Travel Expenses</span>
                        <span className="font-medium dark:text-gray-200">$300.00</span>
                      </div>
                      <div className="border-t dark:border-gray-600 pt-3 flex justify-between font-semibold">
                        <span className="dark:text-gray-200">Total</span>
                        <span className="text-violet-600 dark:text-violet-400">$2,500.00</span>
                      </div>
                    </div>
                  </div>

                  {/* Top Invoice - Most prominent with hover effect */}
                  <div className="absolute inset-0 bg-white dark:bg-gray-800 rounded-lg border-2 border-gray-200 dark:border-gray-700 p-6 shadow-2xl transform rotate-3 hover:rotate-0 transition-all duration-500 z-30 hover:z-40 hover:scale-105">
                    <div className="border-b border-gray-200 dark:border-gray-700 pb-4 mb-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">INVOICE</h3>
                          <p className="text-sm text-gray-600 dark:text-gray-400">#INV-2024-001</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-gray-600 dark:text-gray-400">Date: 2024-12-05</p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">Due: 2024-12-20</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Web Development Services</span>
                        <span className="font-medium dark:text-gray-200">$2,500.00</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">UI/UX Design</span>
                        <span className="font-medium dark:text-gray-200">$1,200.00</span>
                      </div>
                      <div className="border-t dark:border-gray-600 pt-3 flex justify-between font-semibold">
                        <span className="dark:text-gray-200">Total</span>
                        <span className="text-violet-600 dark:text-violet-400">$3,700.00</span>
                      </div>
                    </div>
                    
                    {/* AI Processing Indicator */}
                    <div className="mt-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-3">
                      <div className="flex items-center">
                        <div className="w-2 h-2 bg-green-400 dark:bg-green-400 rounded-full animate-pulse mr-2"></div>
                        <span className="text-sm text-green-800 dark:text-green-300 font-medium">AI Extracted in 2.3s</span>
                      </div>
                    </div>
                  </div>
                  
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>


      {/* How It Works Section */}
      <section className="py-16 bg-white dark:bg-gray-800 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 dark:text-gray-100 sm:text-4xl">
              How it works
            </h2>
            <p className="mt-4 text-xl text-gray-600 dark:text-gray-300 dark:text-gray-300">
              Three simple steps to transform your invoice processing
            </p>
          </div>

          <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-3">
            {/* Step 1 */}
            <div className="text-center">
              <div className="bg-violet-100 dark:bg-violet-900 rounded-full w-16 h-16 flex items-center justify-center mx-auto">
                <CloudUploadIcon className="h-8 w-8 text-violet-600 dark:text-violet-300" />
              </div>
              <h3 className="mt-6 text-lg font-semibold text-gray-900 dark:text-gray-100 dark:text-gray-100">1. Upload Invoice</h3>
              <p className="mt-2 text-gray-600 dark:text-gray-300 dark:text-gray-300">
                Drag and drop your invoice image or PDF. Supports JPG, PNG, and PDF formats up to 10MB.
              </p>
            </div>

            {/* Step 2 */}
            <div className="text-center">
              <div className="bg-violet-100 dark:bg-violet-900 rounded-full w-16 h-16 flex items-center justify-center mx-auto">
                <CpuChipIcon className="h-8 w-8 text-violet-600 dark:text-violet-300" />
              </div>
              <h3 className="mt-6 text-lg font-semibold text-gray-900 dark:text-gray-100 dark:text-gray-100">2. AI Processing</h3>
              <p className="mt-2 text-gray-600 dark:text-gray-300 dark:text-gray-300">
                Our advanced AI extracts all key data points with 99.5% accuracy in under 3 seconds.
              </p>
            </div>

            {/* Step 3 */}
            <div className="text-center">
              <div className="bg-violet-100 dark:bg-violet-900 rounded-full w-16 h-16 flex items-center justify-center mx-auto">
                <DocumentTextIcon className="h-8 w-8 text-violet-600 dark:text-violet-300" />
              </div>
              <h3 className="mt-6 text-lg font-semibold text-gray-900 dark:text-gray-100 dark:text-gray-100">3. Export Data</h3>
              <p className="mt-2 text-gray-600 dark:text-gray-300 dark:text-gray-300">
                Review, edit if needed, and export to your accounting system or download as JSON/CSV.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-gray-50 dark:bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 dark:text-gray-100 sm:text-4xl">
              Powerful features for modern businesses
            </h2>
          </div>

          <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {/* Feature 1 */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-violet-100 rounded-lg flex items-center justify-center">
                <BoltIcon className="h-6 w-6 text-violet-600" />
              </div>
              <h3 className="mt-4 text-lg font-semibold text-gray-900 dark:text-gray-100">Lightning Fast</h3>
              <p className="mt-2 text-gray-600 dark:text-gray-300">
                Process invoices in seconds, not minutes. Our AI is optimized for speed without sacrificing accuracy.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-violet-100 rounded-lg flex items-center justify-center">
                <ShieldCheckIcon className="h-6 w-6 text-violet-600" />
              </div>
              <h3 className="mt-4 text-lg font-semibold text-gray-900 dark:text-gray-100">Secure & Compliant</h3>
              <p className="mt-2 text-gray-600 dark:text-gray-300">
                Bank-level security with SOC 2 Type II compliance. Your data is encrypted and never shared.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-violet-100 rounded-lg flex items-center justify-center">
                <ChartBarIcon className="h-6 w-6 text-violet-600" />
              </div>
              <h3 className="mt-4 text-lg font-semibold text-gray-900 dark:text-gray-100">Smart Analytics</h3>
              <p className="mt-2 text-gray-600 dark:text-gray-300">
                Track processing metrics, identify trends, and optimize your accounts payable workflow.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="bg-violet-600">
        <div className="max-w-7xl mx-auto py-16 px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-white sm:text-4xl">
              Ready to transform your invoice processing?
            </h2>
            <p className="mt-4 text-xl text-violet-100">
              Join thousands of businesses saving time and money with AI-powered automation.
            </p>
            
            <div className="mt-8">
              <Link to="/register">
                <Button 
                  variant="secondary" 
                  size="xl" 
                  className="bg-white dark:bg-gray-800 text-violet-600 hover:bg-gray-50 px-8 py-4 text-lg font-semibold"
                >
                  Start Processing
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-gradient-to-br from-violet-500 to-purple-600 rounded-lg flex items-center justify-center">
                <DocumentTextIcon className="h-5 w-5 text-white" />
              </div>
              <span className="ml-3 text-white font-semibold">Invoice Parser</span>
            </div>
            <div className="flex space-x-6 text-sm text-gray-400">
              <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
              <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
              <a href="#" className="hover:text-white transition-colors">Support</a>
            </div>
          </div>
          <div className="mt-8 border-t border-gray-800 pt-8">
            <p className="text-sm text-gray-400 text-center">
              © 2024 Invoice Parser. All rights reserved. Built with ❤️ for modern businesses.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default Landing;