import { useEffect, useState } from 'react';

// Performance monitoring component for development
function PerformanceMonitor() {
  const [metrics, setMetrics] = useState({});
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Only show in development mode
    if (import.meta.env.PROD) return;

    const updateMetrics = () => {
      if (window.performance && window.performance.timing) {
        const timing = window.performance.timing;
        const navigation = window.performance.navigation;
        
        const metrics = {
          // Page load metrics
          domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
          loadComplete: timing.loadEventEnd - timing.navigationStart,
          
          // Network metrics
          dns: timing.domainLookupEnd - timing.domainLookupStart,
          tcp: timing.connectEnd - timing.connectStart,
          request: timing.responseStart - timing.requestStart,
          response: timing.responseEnd - timing.responseStart,
          
          // Navigation type
          navigationType: navigation.type,
          
          // Memory usage (if available)
          memory: window.performance.memory ? {
            used: Math.round(window.performance.memory.usedJSHeapSize / 1048576),
            total: Math.round(window.performance.memory.totalJSHeapSize / 1048576),
            limit: Math.round(window.performance.memory.jsHeapSizeLimit / 1048576)
          } : null
        };
        
        setMetrics(metrics);
      }
    };

    // Update metrics after page load
    if (document.readyState === 'complete') {
      updateMetrics();
    } else {
      window.addEventListener('load', updateMetrics);
    }

    // Keyboard shortcut to toggle visibility (Ctrl/Cmd + Shift + P)
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'P') {
        e.preventDefault();
        setIsVisible(prev => !prev);
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('load', updateMetrics);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  // Don't render in production
  if (import.meta.env.PROD) return null;

  if (!isVisible) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <button
          onClick={() => setIsVisible(true)}
          className="bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-50 hover:opacity-100 transition-opacity"
          title="Show Performance Metrics (Ctrl+Shift+P)"
        >
          📊
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 bg-gray-900 text-white text-xs p-3 rounded-lg shadow-lg max-w-xs">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold">Performance Metrics</h3>
        <button
          onClick={() => setIsVisible(false)}
          className="text-gray-400 hover:text-white"
        >
          ×
        </button>
      </div>
      
      <div className="space-y-1">
        <div className="grid grid-cols-2 gap-2">
          <div>DOM Ready:</div>
          <div>{metrics.domContentLoaded}ms</div>
          
          <div>Load Complete:</div>
          <div>{metrics.loadComplete}ms</div>
          
          <div>DNS:</div>
          <div>{metrics.dns}ms</div>
          
          <div>Request:</div>
          <div>{metrics.request}ms</div>
          
          <div>Response:</div>
          <div>{metrics.response}ms</div>
        </div>
        
        {metrics.memory && (
          <div className="mt-2 pt-2 border-t border-gray-700">
            <div className="text-gray-300">Memory Usage:</div>
            <div>{metrics.memory.used}MB / {metrics.memory.total}MB</div>
            <div className="text-gray-400">Limit: {metrics.memory.limit}MB</div>
          </div>
        )}
        
        <div className="mt-2 pt-2 border-t border-gray-700 text-gray-400">
          Press Ctrl+Shift+P to toggle
        </div>
      </div>
    </div>
  );
}

export default PerformanceMonitor;
