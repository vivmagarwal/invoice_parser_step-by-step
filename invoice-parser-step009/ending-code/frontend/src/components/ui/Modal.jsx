import { useEffect, useRef } from 'react';
import { XMarkIcon } from './Icons';
import { useKeyboardNavigation, useFocusTrap } from '../../hooks/useKeyboardNavigation';

// Modal component with enhanced accessibility
function Modal({ isOpen, onClose, title, children, showCloseButton = true }) {
  const modalRef = useRef(null);
  
  // Enhanced keyboard navigation and focus management
  useKeyboardNavigation(isOpen, onClose);
  useFocusTrap(isOpen, modalRef);
  
  // Handle body scroll and focus management
  useEffect(() => {
    if (isOpen) {
      // Prevent body scrolling when modal is open
      document.body.style.overflow = 'hidden';
      
      // Set focus to modal container
      if (modalRef.current) {
        modalRef.current.focus();
      }
    }
    
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-4 text-center sm:p-0">
        {/* Backdrop */}
        <div 
          className="modal-overlay"
          onClick={onClose}
        ></div>

        {/* Modal content */}
        <div 
          ref={modalRef}
          className="inline-block align-middle modal-content"
          role="dialog"
          aria-modal="true"
          aria-labelledby={title ? 'modal-title' : undefined}
          tabIndex="-1"
        >
          {/* Header */}
          {(title || showCloseButton) && (
            <div className="flex items-center justify-between mb-4">
              {title && (
                <h3 id="modal-title" className="text-lg font-medium text-gray-900 dark:text-gray-100 text-center w-full">
                  {title}
                </h3>
              )}
              {showCloseButton && (
                <button
                  onClick={onClose}
                  className="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 transition-colors focus:outline-none focus:ring-2 focus:ring-violet-500 dark:focus:ring-violet-400 rounded-md"
                  aria-label="Close modal"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              )}
            </div>
          )}

          {/* Content */}
          <div>
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Modal;
