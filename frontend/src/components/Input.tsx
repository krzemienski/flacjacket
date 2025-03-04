'use client';

import { InputHTMLAttributes, ReactNode, forwardRef } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  helperText?: string;
  error?: boolean;
  startAdornment?: ReactNode;
  endAdornment?: ReactNode;
  fullWidth?: boolean;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      helperText,
      error = false,
      className = '',
      startAdornment,
      endAdornment,
      fullWidth = false,
      id,
      ...props
    },
    ref
  ) => {
    return (
      <div className={`${fullWidth ? 'w-full' : ''} mb-4`}>
        {label && (
          <label
            htmlFor={id}
            className={`block text-sm font-medium mb-1 ${
              error
                ? 'text-error-light dark:text-error-dark'
                : 'text-gray-700 dark:text-gray-300'
            }`}
          >
            {label}
          </label>
        )}
        <div className="relative">
          {startAdornment && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              {startAdornment}
            </div>
          )}
          <input
            ref={ref}
            id={id}
            className={`block w-full rounded-md shadow-sm px-3 py-2 
              ${startAdornment ? 'pl-10' : ''} 
              ${endAdornment ? 'pr-10' : ''} 
              ${
                error
                  ? 'border-error-light focus:ring-error-light focus:border-error-light dark:border-error-dark dark:focus:ring-error-dark dark:focus:border-error-dark'
                  : 'border-gray-300 focus:ring-primary-500 focus:border-primary-500 dark:border-gray-700 dark:bg-surface-dark dark:text-white dark:focus:ring-primary-400 dark:focus:border-primary-400'
              } 
              transition-colors ${className}`}
            {...props}
          />
          {endAdornment && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              {endAdornment}
            </div>
          )}
        </div>
        {helperText && (
          <p
            className={`mt-1 text-sm ${
              error
                ? 'text-error-light dark:text-error-dark'
                : 'text-gray-500 dark:text-gray-400'
            }`}
          >
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
