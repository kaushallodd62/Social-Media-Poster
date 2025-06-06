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
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white py-12 px-4 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        {/* Logo */}
        <div className="flex justify-center">
          <Link href="/" className="flex items-center space-x-2">
            <Image
              src="/logo.png"
              alt="Logo"
              width={40}
              height={40}
              className="h-10 w-auto"
            />
            <span className="text-2xl font-bold text-gray-900">YourApp</span>
          </Link>
        </div>

        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 tracking-tight">
          {title}
        </h2>
        {subtitle && linkText && linkHref && linkLabel && (
          <p className="mt-2 text-center text-sm text-gray-600">
            {subtitle}{' '}
            <Link 
              href={linkHref} 
              className="font-medium text-blue-600 hover:text-blue-500 transition-colors duration-200"
            >
              {linkLabel}
            </Link>
          </p>
        )}
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow-xl sm:rounded-lg sm:px-10 transform transition-all duration-200 hover:shadow-2xl">
          {error && (
            <Alert 
              type="error" 
              message={error} 
              className="mb-4 animate-fade-in" 
            />
          )}
          
          {success && (
            <Alert 
              type="success" 
              message={success} 
              className="mb-4 animate-fade-in" 
            />
          )}

          {children}

          {showGoogleAuth && onGoogleAuth && (
            <>
              <div className="mt-6">
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-300" />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-white text-gray-500">Or continue with</span>
                  </div>
                </div>

                <div className="mt-6">
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={onGoogleAuth}
                    className="w-full border border-gray-300 shadow-sm hover:shadow-md transition-all duration-200"
                    icon={<FcGoogle className="h-5 w-5" />}
                  >
                    {googleButtonText}
                  </Button>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-600">
          <p>
            By continuing, you agree to our{' '}
            <Link href="/terms" className="font-medium text-blue-600 hover:text-blue-500 transition-colors duration-200">
              Terms of Service
            </Link>{' '}
            and{' '}
            <Link href="/privacy" className="font-medium text-blue-600 hover:text-blue-500 transition-colors duration-200">
              Privacy Policy
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthFormLayout; 