import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNotification } from '../context/NotificationContext';
import UploadPanel from '../components/processing/UploadPanel';
import ResultsPanel from '../components/processing/ResultsPanel';

// Process page with enhanced side-by-side interface
function Process() {
  const { user, apiRequest } = useAuth();
  const { showSuccess, showError, showInfo } = useNotification();
  
  const [selectedFile, setSelectedFile] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [saveStatus, setSaveStatus] = useState('idle'); // idle, saving, saved, error

  const handleFileSelect = async (file) => {
    setSelectedFile(file);
    setResults(null);
    setError(null);
    setSaveStatus('idle');
    
    // Automatically start processing when file is selected
    await processInvoice(file);
  };

  const handleClearFile = () => {
    setSelectedFile(null);
    setResults(null);
    setError(null);
    setSaveStatus('idle');
  };

  const processInvoice = async (file) => {
    setProcessing(true);
    setError(null);
    
    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('file', file);

      // Make API request to process invoice
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/parse-invoice`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: formData
      });

      const data = await response.json();

      if (response.ok) {
        setResults(data);
        showSuccess(
          'Invoice processed successfully! Review the extracted data below.',
          'Processing Complete'
        );
      } else {
        throw new Error(data.detail || 'Processing failed');
      }
    } catch (error) {
      console.error('Processing error:', error);
      setError(error.message || 'Failed to process invoice. Please try again.');
      showError(
        'Failed to process the invoice. Please check the file and try again.',
        'Processing Failed'
      );
    } finally {
      setProcessing(false);
    }
  };

  const handleSaveToDatabase = async () => {
    if (!results) return;

    setSaveStatus('saving');
    
    try {
      const result = await apiRequest('/api/save-invoice', {
        method: 'POST',
        body: JSON.stringify(results.data)
      });

      if (result.success) {
        setSaveStatus('saved');
        showSuccess(
          'Invoice data has been saved to your database successfully!',
          'Data Saved'
        );
      } else {
        throw new Error(result.error);
      }
    } catch (error) {
      console.error('Save error:', error);
      setSaveStatus('error');
      showError(
        'Failed to save invoice data. Please try again.',
        'Save Failed'
      );
    }
  };

  const handleCopyResults = () => {
    showSuccess('Invoice data copied to clipboard!', 'Copied');
  };

  const handleDownloadResults = () => {
    showSuccess('Invoice data downloaded successfully!', 'Downloaded');
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            Process Invoice
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Welcome, <span className="font-semibold text-violet-600 dark:text-violet-400">{user?.name}</span>! 
            Upload your invoice and our AI will extract the data in seconds.
          </p>
        </div>

        {/* Side-by-Side Interface */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Panel */}
          <UploadPanel
            onFileSelect={handleFileSelect}
            selectedFile={selectedFile}
            onClearFile={handleClearFile}
            processing={processing}
          />

          {/* Results Panel */}
          <ResultsPanel
            processing={processing}
            results={results}
            error={error}
            onSaveToDatabase={handleSaveToDatabase}
            saveStatus={saveStatus}
            onCopyResults={handleCopyResults}
            onDownloadResults={handleDownloadResults}
          />
        </div>

        {/* Processing Tips */}
        <div className="mt-12 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            How it works
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-violet-100 dark:bg-violet-900 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-lg font-semibold text-violet-600 dark:text-violet-300">1</span>
              </div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Upload</h4>
              <p className="text-sm text-gray-600 dark:text-gray-300">
                Drag and drop or browse to select your invoice file (JPG, PNG, or JPEG)
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-violet-100 dark:bg-violet-900 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-lg font-semibold text-violet-600 dark:text-violet-300">2</span>
              </div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Process</h4>
              <p className="text-sm text-gray-600 dark:text-gray-300">
                Our AI analyzes your invoice and extracts key data with 99.5% accuracy
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-violet-100 dark:bg-violet-900 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-lg font-semibold text-violet-600 dark:text-violet-300">3</span>
              </div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Save</h4>
              <p className="text-sm text-gray-600 dark:text-gray-300">
                Review, edit if needed, and save to your database or download the data
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Process;