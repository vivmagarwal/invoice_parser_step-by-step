import { 
  DocumentCheckIcon,
  ClipboardIcon,
  ArrowDownIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '../ui/Icons';
import Button from '../ui/Button';

// Skeleton loader component for loading state
function SkeletonLoader() {
  return (
    <div className="space-y-4 animate-pulse">
      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-2/3"></div>
      <div className="space-y-2 mt-6">
        <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded"></div>
        <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-4/5"></div>
        <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-3/5"></div>
        <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-4/5"></div>
        <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-2/3"></div>
      </div>
    </div>
  );
}

// Results Panel Component for displaying JSON extraction results
function ResultsPanel({ 
  processing, 
  results, 
  error, 
  onSaveToDatabase, 
  saveStatus, 
  onCopyResults, 
  onDownloadResults 
}) {

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(results, null, 2));
      onCopyResults();
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleDownload = () => {
    const dataStr = JSON.stringify(results, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `invoice-data-${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    if (onDownloadResults) {
      onDownloadResults();
    }
  };


  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">Extracted Data</h2>
        <p className="text-gray-600 dark:text-gray-300">
          AI-powered data extraction results from your invoice
        </p>
      </div>

      {/* Content */}
      <div className="min-h-96">
        {processing ? (
          /* Loading State */
          <div className="space-y-4">
            <div className="flex items-center justify-center py-8">
              <div className="text-center">
                <div className="w-12 h-12 border-4 border-violet-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-gray-600 dark:text-gray-300 font-medium">Processing your invoice...</p>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">This usually takes 2-5 seconds</p>
              </div>
            </div>
            <SkeletonLoader />
          </div>
        ) : error ? (
          /* Error State */
          <div className="text-center py-8">
            <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">Processing Failed</h3>
            <p className="text-gray-600 dark:text-gray-300 mb-4">{error}</p>
            <Button variant="outline" onClick={() => window.location.reload()}>
              Try Again
            </Button>
          </div>
        ) : results ? (
          /* Results State */
          <div className="space-y-6">

            {/* JSON Content */}
            <div className="min-h-64">
              <div className="bg-gray-900 rounded-lg p-6 overflow-auto max-h-96">
                <pre className="text-sm text-green-400 font-mono leading-relaxed">
                  {JSON.stringify(results, null, 2)}
                </pre>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              <Button
                onClick={onSaveToDatabase}
                disabled={saveStatus === 'saving' || saveStatus === 'saved'}
                loading={saveStatus === 'saving'}
                className={saveStatus === 'saved' ? 'bg-green-600 hover:bg-green-700' : ''}
              >
                {saveStatus === 'saved' ? (
                  <>
                    <CheckCircleIcon className="h-4 w-4 mr-2" />
                    Saved to Database
                  </>
                ) : saveStatus === 'saving' ? (
                  'Saving...'
                ) : (
                  <>
                    Save to Database
                  </>
                )}
              </Button>

              <Button variant="outline" onClick={handleCopy}>
                Copy JSON
              </Button>

              <Button variant="outline" onClick={handleDownload}>
                Download JSON
              </Button>
            </div>
          </div>
        ) : (
          /* Empty State */
          <div className="text-center py-16">
            <DocumentCheckIcon className="h-16 w-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">Ready to Process</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Upload an invoice to see the extracted data here
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default ResultsPanel;
