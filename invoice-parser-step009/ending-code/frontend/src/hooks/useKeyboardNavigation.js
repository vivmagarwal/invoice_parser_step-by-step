import { useEffect } from 'react';

// Custom hook for keyboard navigation and accessibility
function useKeyboardNavigation(isOpen, onClose, onConfirm) {
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (event) => {
      switch (event.key) {
        case 'Escape':
          event.preventDefault();
          onClose?.();
          break;
        
        case 'Enter':
          // Only trigger confirm if not in an input field
          if (event.target.tagName !== 'INPUT' && event.target.tagName !== 'TEXTAREA') {
            event.preventDefault();
            onConfirm?.();
          }
          break;
        
        case 'Tab':
          // Handle tab navigation within modal/dialog
          handleTabNavigation(event);
          break;
      }
    };

    const handleTabNavigation = (event) => {
      const focusableElements = document.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      
      const focusableArray = Array.from(focusableElements).filter(el => {
        return el.offsetParent !== null && !el.disabled;
      });

      const firstElement = focusableArray[0];
      const lastElement = focusableArray[focusableArray.length - 1];

      if (event.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          event.preventDefault();
          lastElement?.focus();
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          event.preventDefault();
          firstElement?.focus();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose, onConfirm]);
}

// Hook for focus management
function useFocusManagement(isOpen, focusElementRef) {
  useEffect(() => {
    if (isOpen && focusElementRef?.current) {
      // Focus the specified element when opened
      const timer = setTimeout(() => {
        focusElementRef.current.focus();
      }, 100);

      return () => clearTimeout(timer);
    }
  }, [isOpen, focusElementRef]);
}

// Hook for focus trap (keeps focus within a container)
function useFocusTrap(isActive, containerRef) {
  useEffect(() => {
    if (!isActive || !containerRef?.current) return;

    const container = containerRef.current;
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleTabKey = (e) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    };

    container.addEventListener('keydown', handleTabKey);
    
    // Focus first element initially
    firstElement?.focus();

    return () => {
      container.removeEventListener('keydown', handleTabKey);
    };
  }, [isActive, containerRef]);
}

export { useKeyboardNavigation, useFocusManagement, useFocusTrap };
