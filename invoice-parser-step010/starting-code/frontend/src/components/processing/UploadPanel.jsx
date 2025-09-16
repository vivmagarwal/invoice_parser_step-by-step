import { useState, useRef } from 'react';
import { 
  CloudUploadIcon, 
  XMarkIcon
} from '../ui/Icons';
import Button from '../ui/Button';

// Upload Panel Component for side-by-side processing interface
function UploadPanel({ onFileSelect, selectedFile, onClearFile, processing }) {
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelection(files[0]);
    }
  };

  const handleFileSelection = (file) => {
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
    if (!allowedTypes.includes(file.type)) {
      alert('Please select a valid image file (JPG, PNG) or PDF.');
      return;
    }

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB in bytes
    if (file.size > maxSize) {
      alert('File size must be less than 10MB.');
      return;
    }

    onFileSelect(file);
  };

  const handleFileInputChange = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      handleFileSelection(files[0]);
    }
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };


  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">Upload Invoice</h2>
        <p className="text-gray-600 dark:text-gray-300">
          Upload your invoice image for AI-powered data extraction.
        </p>
      </div>

      {!selectedFile ? (
        /* Upload Area */
        <div
          className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragOver
              ? 'border-violet-400 bg-violet-50 dark:bg-violet-900/20 dark:border-violet-500'
              : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
          } ${processing ? 'pointer-events-none opacity-50' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {/* <CloudUploadIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" /> */}
          
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            Drop your invoice here
          </h3>
          
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            or click to browse your files
          </p>

          <Button 
            onClick={handleBrowseClick}
            disabled={processing}
            className="mb-4"
          >
            Browse Files
          </Button>

          <div className="text-sm text-gray-500 dark:text-gray-400 space-y-1">
            <p>Supports: JPG, PNG, JPEG</p>
            <p>Maximum file size: 10MB</p>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept=".jpg,.jpeg,.png,.pdf,image/jpeg,image/png,application/pdf"
            onChange={handleFileInputChange}
            className="hidden"
            disabled={processing}
          />
        </div>
      ) : (
        /* File Preview */
        <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <div className="flex items-start justify-between mb-4">
            {!processing && (
              <button
                onClick={onClearFile}
                className="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            )}
          </div>


          {/* File Preview for Images */}
          {selectedFile.type.startsWith('image/') && (
            <div className="mt-4 flex justify-center">
              <img
                src={URL.createObjectURL(selectedFile)}
                alt="Invoice preview"
                className="max-w-full h-64 object-contain rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700"
              />
            </div>
          )}

          {/* Processing Status */}
          {processing && (
            <div className="mt-4 p-3 bg-violet-50 dark:bg-violet-900/20 border border-violet-200 dark:border-violet-800 rounded-lg">
              <div className="flex items-center">
                <div className="w-4 h-4 border-2 border-violet-600 dark:border-violet-400 border-t-transparent rounded-full animate-spin mr-3"></div>
                <span className="text-sm font-medium text-violet-800 dark:text-violet-300">
                  Processing your invoice...
                </span>
              </div>
              <p className="text-xs text-violet-600 dark:text-violet-400 mt-1">
                Our AI is extracting data from your document
              </p>
            </div>
          )}
        </div>
      )}

      {/* Upload Instructions */}
      <div className="mt-6 bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
        <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">Tips for best results:</h4>
        <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-1">
          <li>• Ensure the invoice is clearly visible and well-lit</li>
          <li>• Avoid blurry or rotated images</li>
          <li>• Include the entire invoice in the image</li>
          <li>• Higher resolution images provide better accuracy</li>
        </ul>
      </div>
    </div>
  );
}

export default UploadPanel;
