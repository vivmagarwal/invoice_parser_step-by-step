import { forwardRef } from 'react';

// Input component with label and error handling
const Input = forwardRef(({ 
  label, 
  error, 
  type = 'text', 
  required = false,
  className = '',
  ...props 
}, ref) => {
  const inputClasses = `form-input ${error ? 'border-red-300 focus:border-red-500 focus:ring-red-500 dark:border-red-500 dark:focus:border-red-400 dark:focus:ring-red-400' : ''} ${className}`;
  
  return (
    <div>
      {label && (
        <label className="form-label">
          {label}
          {required && <span className="text-red-500 dark:text-red-400 ml-1">*</span>}
        </label>
      )}
      <input
        ref={ref}
        type={type}
        className={inputClasses}
        {...props}
      />
      {error && (
        <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;
