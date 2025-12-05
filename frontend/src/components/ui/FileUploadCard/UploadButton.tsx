import React from 'react';

interface UploadButtonProps {
  onClick: () => void;
  disabled?: boolean;
  icon?: React.ReactNode;
  label: string;
  secondary?: boolean;
}

const UploadButton: React.FC<UploadButtonProps> = ({
  onClick,
  disabled = false,
  icon,
  label,
  secondary = false
}) => {
  const baseClasses = "w-full flex items-center justify-center py-2.5 px-4 rounded-lg font-medium text-sm transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2";
  
  const primaryClasses = secondary
    ? "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 focus:ring-gray-300"
    : "bg-[#155dfc] text-white hover:bg-[#1247c1] focus:ring-[#155dfc]";
  
  const disabledClasses = secondary
    ? "bg-gray-100 text-gray-400 border border-gray-200 cursor-not-allowed"
    : "bg-[#155dfc]/60 text-white/90 cursor-not-allowed";

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        ${baseClasses} 
        ${disabled ? disabledClasses : primaryClasses}
        cursor-pointer
      `}
    >
      {icon && <span className="mr-2">{icon}</span>}
      {label}
    </button>
  );
};

export default UploadButton;