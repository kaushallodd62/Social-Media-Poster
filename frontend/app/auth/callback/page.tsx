'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Button, LoadingSpinner, Alert } from '@/app/components/ui';

export default function AuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = searchParams.get('token');
    const error = searchParams.get('error');
    const message = searchParams.get('message');

    if (error) {
      setError(message || error);
      return;
    }

    if (token) {
      // Set token as a cookie with 7-day expiration for development
      document.cookie = `token=${token}; path=/; max-age=604800; samesite=lax`;
      router.push('/dashboard');
    } else {
      setError('No token received');
    }
  }, [searchParams, router]);

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