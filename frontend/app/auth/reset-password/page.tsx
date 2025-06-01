'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/app/contexts/AuthContext';
import { useRouter, useSearchParams } from 'next/navigation';
import AuthFormLayout from '@/app/components/AuthFormLayout';
import { Input, Button } from '@/app/components/ui';

export default function ResetPasswordPage() {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const { resetPassword } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const tokenParam = searchParams.get('token');
    if (!tokenParam) {
      router.push('/auth/login');
    } else {
      setToken(tokenParam);
    }
  }, [searchParams, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setLoading(true);

    try {
      if (!token) {
        throw new Error('Invalid reset token');
      }
      await resetPassword(token, password);
      router.push('/auth/login?reset=success');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return null;
  }

  return (
    <AuthFormLayout
      title="Reset your password"
      subtitle="Or"
      linkHref="/auth/login"
      linkLabel="sign in to your account"
      error={error}
      showGoogleAuth={false}
    >
      <form className="space-y-6" onSubmit={handleSubmit}>
        <Input
          label="New Password"
          type="password"
          autoComplete="new-password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          showPasswordToggle
        />

        <Input
          label="Confirm New Password"
          type="password"
          autoComplete="new-password"
          required
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          showPasswordToggle
        />

        <Button
          type="submit"
          loading={loading}
          className="w-full"
        >
          {loading ? 'Resetting password...' : 'Reset password'}
        </Button>
      </form>
    </AuthFormLayout>
  );
} 