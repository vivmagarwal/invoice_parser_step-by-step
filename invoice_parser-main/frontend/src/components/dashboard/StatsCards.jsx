import { 
  DocumentTextIcon,
  CheckCircleIcon,
  ClockIcon,
  ChartBarIcon,
  ArrowUpIcon,
  ArrowDownIcon
} from '../ui/Icons';

// Stats Cards Component for dashboard metrics
function StatsCards({ stats, loading }) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 animate-pulse">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
              <div className="ml-4 flex-1">
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-20 mb-2"></div>
                <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-16"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }


  const statsConfig = [
    {
      id: 'total_invoices',
      title: 'Total Invoices',
      value: stats?.total_invoices || 0,
      icon: DocumentTextIcon,
      iconBg: 'bg-violet-100 dark:bg-violet-900',
      iconColor: 'text-violet-600 dark:text-violet-300',
      change: stats?.invoice_change || 0,
      changeType: (stats?.invoice_change || 0) >= 0 ? 'increase' : 'decrease'
    },
    {
      id: 'success_rate',
      title: 'Success Rate',
      value: `${Math.round(stats?.success_rate || 0)}%`,
      icon: CheckCircleIcon,
      iconBg: 'bg-green-100 dark:bg-green-900',
      iconColor: 'text-green-600 dark:text-green-300',
      change: stats?.success_rate_change || 0,
      changeType: (stats?.success_rate_change || 0) >= 0 ? 'increase' : 'decrease'
    },
    {
      id: 'recent_activity',
      title: 'This Week',
      value: stats?.recent_invoices || 0,
      icon: ClockIcon,
      iconBg: 'bg-blue-100 dark:bg-blue-900',
      iconColor: 'text-blue-600 dark:text-blue-300',
      change: stats?.weekly_change || 0,
      changeType: (stats?.weekly_change || 0) >= 0 ? 'increase' : 'decrease'
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
      {statsConfig.map((stat) => (
        <div key={stat.id} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow">
          <div className="flex items-center">
            <div className={`w-12 h-12 ${stat.iconBg} rounded-lg flex items-center justify-center`}>
              <stat.icon className={`h-6 w-6 ${stat.iconColor}`} />
            </div>
            
            <div className="ml-4 flex-1">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-300">{stat.title}</p>
              <div className="flex items-baseline">
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stat.value}</p>
                
                {/* Change indicator */}
                {stat.change !== undefined && stat.change !== 0 && (
                  <div className={`ml-2 flex items-center text-sm ${
                    stat.changeType === 'increase' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                  }`}>
                    {stat.changeType === 'increase' ? (
                      <ArrowUpIcon className="h-4 w-4 mr-1" />
                    ) : (
                      <ArrowDownIcon className="h-4 w-4 mr-1" />
                    )}
                    <span>{Math.abs(stat.change)}%</span>
                  </div>
                )}
              </div>
              
              {/* Subtitle for storage */}
              {stat.subtitle && (
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{stat.subtitle}</p>
              )}
            </div>
          </div>

          {/* Progress bar for storage */}
          {stat.progress !== undefined && (
            <div className="mt-4">
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full transition-all duration-300 ${
                    stat.progress > 90 ? 'bg-red-500' : 
                    stat.progress > 70 ? 'bg-yellow-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${Math.min(stat.progress, 100)}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {stat.progress.toFixed(1)}% used
              </p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default StatsCards;
