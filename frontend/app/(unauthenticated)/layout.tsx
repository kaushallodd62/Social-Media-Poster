'use client';

import { useAuth } from '../contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { LoadingSpinner } from '../components/ui';

export default function UnauthenticatedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) {
      router.push('/dashboard');
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex min-h-screen">
        {/* Left side - Auth form */}
        <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8">
          <div className="max-w-md w-full space-y-8">
            {children}
          </div>
        </div>

        {/* Right side - Decorative image */}
        <div className="hidden lg:block relative w-0 flex-1">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-600">
            <div className="absolute inset-0 bg-opacity-75 flex flex-col justify-center px-12">
              <h2 className="text-4xl font-bold text-white mb-4">
                Social Media Poster
              </h2>
              <p className="text-xl text-white/90">
                Schedule and manage your social media posts with ease
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 