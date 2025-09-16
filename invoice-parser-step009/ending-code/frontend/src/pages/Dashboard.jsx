import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNotification } from '../context/NotificationContext';
import DashboardHeader from '../components/dashboard/DashboardHeader';
import StatsCards from '../components/dashboard/StatsCards';
import InvoiceTable from '../components/dashboard/InvoiceTable';
import LoadingSpinner from '../components/ui/LoadingSpinner';

// Enhanced Dashboard page with tabular invoice management
function Dashboard() {
  const { user, apiRequest } = useAuth();
  const { showSuccess, showError, showInfo } = useNotification();
  
  const [stats, setStats] = useState(null);
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [invoicesLoading, setInvoicesLoading] = useState(false);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
    total: 0
  });

  // Fetch dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      
      try {
        // Fetch stats and invoices in parallel
        const [statsResult, invoicesResult] = await Promise.all([
          apiRequest('/api/dashboard/stats'),
          apiRequest(`/api/dashboard/invoices?page=${pagination.page}&limit=${pagination.limit}`)
        ]);

        if (statsResult.success) {
          // Extract statistics from nested structure
          setStats(statsResult.data.statistics || statsResult.data);
        } else {
          console.warn('Failed to fetch stats:', statsResult.error);
          // Set default stats for demo
          setStats({
            total_invoices: 0,
            success_rate: 0,
            recent_activity: 0,
            storage_used: 0,
            storage_limit: 1000
          });
        }

        if (invoicesResult.success) {
          setInvoices(invoicesResult.data.invoices || []);
          setPagination(prev => ({
            ...prev,
            total: invoicesResult.data.total || 0
          }));
        } else {
          console.warn('Failed to fetch invoices:', invoicesResult.error);
          setInvoices([]);
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        showError('Failed to load dashboard data. Please refresh the page.', 'Loading Error');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [apiRequest, pagination.page, pagination.limit, showError]);

  // Refresh invoices data (used after deletion)
  const refreshInvoices = async () => {
    setInvoicesLoading(true);
    
    try {
      const result = await apiRequest(`/api/dashboard/invoices?page=${pagination.page}&limit=${pagination.limit}`);
      
      if (result.success) {
        setInvoices(result.data.invoices || []);
        setPagination(prev => ({
          ...prev,
          total: result.data.total || 0
        }));
        
        // Also refresh stats to update counts
        const statsResult = await apiRequest('/api/dashboard/stats');
        if (statsResult.success) {
          setStats(statsResult.data);
        }
      }
    } catch (error) {
      console.error('Error refreshing invoices:', error);
    } finally {
      setInvoicesLoading(false);
    }
  };

  // Handle invoice deletion
  const handleDeleteInvoice = async (invoiceId) => {
    try {
      const result = await apiRequest(`/api/dashboard/invoices/${invoiceId}`, {
        method: 'DELETE'
      });

      if (result.success) {
        showSuccess('Invoice deleted successfully', 'Deleted');
        await refreshInvoices(); // Refresh the list
      } else {
        throw new Error(result.error);
      }
    } catch (error) {
      console.error('Delete error:', error);
      showError('Failed to delete invoice. Please try again.', 'Delete Failed');
    }
  };


  // Handle pagination
  const handlePageChange = (newPage) => {
    setPagination(prev => ({
      ...prev,
      page: newPage
    }));
  };


  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600 dark:text-gray-300">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <DashboardHeader
          user={user}
        />

        {/* Stats Cards */}
        <StatsCards stats={stats} loading={false} />

        {/* Main Content */}
        <div className="space-y-6">
          {/* Invoice Table - Full Width */}
          <InvoiceTable
            invoices={invoices}
            loading={invoicesLoading}
            onDeleteInvoice={handleDeleteInvoice}
          />
        </div>
      </div>

    </div>
  );
}

export default Dashboard;