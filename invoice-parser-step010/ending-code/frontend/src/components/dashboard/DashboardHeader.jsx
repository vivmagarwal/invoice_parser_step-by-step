import { Link } from 'react-router-dom';
import { 
  PlusIcon
} from '../ui/Icons';
import Button from '../ui/Button';

// Dashboard Header Component
function DashboardHeader({ user }) {
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
      {/* Welcome Section */}
      <div className="mb-4 sm:mb-0">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
          {getGreeting()}, {user?.name}!
        </h1>
        <p className="text-gray-600 dark:text-gray-300 mt-1">
          Here's an overview of your invoice processing activity
        </p>
      </div>
      
      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-3">
        
        {/* Process New Invoice Button */}
        <Link to="/process">
          <Button size="md" className="w-full sm:w-auto">
            <PlusIcon className="h-4 w-4 mr-2" />
            Process New Invoice
          </Button>
        </Link>
      </div>
    </div>
  );
}

export default DashboardHeader;
