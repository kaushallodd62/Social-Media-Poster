'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button, LoadingSpinner, Alert } from '../../components/ui';

function parseHashFragment() {
  const hash = typeof window !== 'undefined' ? window.location.hash.substring(1) : '';
  const params: Record<string, string> = {};
  hash.split('&').forEach(pair => {
    const [key, value] = pair.split('=');
    if (key) params[key] = decodeURIComponent(value || '');
  });
  return params;
}

export default function AuthCallbackPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const params = parseHashFragment();
    const token = params['token'];
    const error = params['error'];

    if (error) {
      setError(error);
      return;
    }

    if (token) {
      // Set token as a cookie with 1-hour expiration
      document.cookie = `token=${token}; path=/; max-age=3600; samesite=lax`;
      router.push('/dashboard');
    } else {
      setError('No token received');
    }
  }, [router]);

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
            <Alert type="error" message={error} className="mb-6" />
            <Button
              onClick={() => router.push('/auth/login')}
              className="w-full"
            >
              Return to Login
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Completing authentication...
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Please wait while we complete your sign in.
          </p>
          <div className="mt-8">
            <LoadingSpinner size="lg" />
          </div>
        </div>
      </div>
    </div>
  );
} 