import React, { forwardRef, useId } from 'react';
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: React.ReactNode;
  showPasswordToggle?: boolean;
  icon?: React.ReactNode;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, showPasswordToggle, icon, className = '', type = 'text', ...props }, ref) => {
    const [showPassword, setShowPassword] = React.useState(false);
    const inputType = showPasswordToggle ? (showPassword ? 'text' : 'password') : type;
    const id = useId();

    const baseClasses = `
      appearance-none block w-full px-3 py-2 border rounded-md shadow-sm 
      placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 
      focus:border-blue-500 sm:text-sm transition-colors duration-200
      ${error 
        ? 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500' 
        : 'border-gray-300'
      }
      ${icon ? 'pl-10' : ''}
      ${showPasswordToggle ? 'pr-10' : ''}
    `;

    return (
      <div className="space-y-1">
        {label && (
          <label htmlFor={id} className="block text-sm font-medium text-gray-700">
            {label}
          </label>
        )}
        <div className="relative">
          {icon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              {icon}
            </div>
          )}
          <input
            ref={ref}
            type={inputType}
            id={label ? id : undefined}
            className={`${baseClasses} ${className}`}
            {...props}
          />
          {showPasswordToggle && (
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
            >
              {showPassword ? (
                <EyeSlashIcon className="h-5 w-5 text-gray-400" />
              ) : (
                <EyeIcon className="h-5 w-5 text-gray-400" />
              )}
            </button>
          )}
        </div>
        {error && (
          <span className="text-sm text-red-600" aria-live="polite">{error}</span>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input; 