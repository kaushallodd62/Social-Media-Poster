import React from 'react';
import Link from 'next/link';
import { FcGoogle } from 'react-icons/fc';
import { Alert, Button } from './ui';
import Image from 'next/image';

interface AuthFormLayoutProps {
  title: string;
  subtitle?: string;
  linkText?: string;
  linkHref?: string;
  linkLabel?: string;
  children: React.ReactNode;
  error?: string;
  success?: string;
  onGoogleAuth?: () => void;
  showGoogleAuth?: boolean;
  googleButtonText?: string;
}

const AuthFormLayout: React.FC<AuthFormLayoutProps> = ({
  title,
  subtitle,
  linkText,
  linkHref,
  linkLabel,
  children,
  error,
  success,
  onGoogleAuth,
  showGoogleAuth = true,
  googleButtonText = 'Continue with Google',
}) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-[#121212] transition-colors duration-300">
      <div className="w-full max-w-md p-8 bg-white dark:bg-[#23272f] rounded-xl shadow-2xl border border-gray-200 dark:border-gray-800">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{title}</h1>
        <div className="flex items-center justify-between mb-6">
          <span className="text-sm text-gray-600 dark:text-gray-300">
            {subtitle}
            <a
              href={linkHref}
              className="ml-1 text-blue-600 dark:text-blue-400 hover:underline focus:underline focus:outline-none"
            >
              {linkLabel}
            </a>
          </span>
        </div>
        {error && (
          <div className="mb-4 p-3 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200 rounded border border-red-200 dark:border-red-700">
            {error}
          </div>
        )}
        <div className="space-y-6">{children}</div>
        {onGoogleAuth && googleButtonText && (
          <>
            <div className="my-6 flex items-center">
              <div className="flex-grow border-t border-gray-300 dark:border-gray-700" />
              <span className="mx-4 text-gray-500 dark:text-gray-400 text-sm">Or continue with</span>
              <div className="flex-grow border-t border-gray-300 dark:border-gray-700" />
            </div>
            <button
              type="button"
              onClick={onGoogleAuth}
              className="w-full flex items-center justify-center gap-2 py-2 px-4 rounded bg-white dark:bg-[#18181b] border border-gray-300 dark:border-gray-700 shadow-md hover:shadow-lg transition-all duration-200 text-gray-900 dark:text-gray-100 font-semibold focus:outline-none focus:ring-2 focus:ring-blue-400"
            >
              <FcGoogle className="h-5 w-5" />
              {googleButtonText}
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default AuthFormLayout; 