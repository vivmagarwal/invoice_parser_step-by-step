import { CircleLoader } from 'react-spinners';

// Loading spinner component using react-spinners
function LoadingSpinner({ size = 'md', className = '', color = '#6366f1' }) {
  const sizeMap = {
    sm: 24,
    md: 32,
    lg: 48,
    xl: 64
  };

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <CircleLoader
        color={color} // customizable color, defaults to indigo-500
        size={sizeMap[size]}
        loading={true}
        speedMultiplier={0.8}
      />
    </div>
  );
}

export default LoadingSpinner;
