'use client';

import { useState } from 'react';
import { useAuth } from '@/app/contexts/AuthContext';
import AuthFormLayout from '@/app/components/AuthFormLayout';
import { Input, Button } from '@/app/components/ui';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const { forgotPassword } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setLoading(true);

    try {
      await forgotPassword(email);
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthFormLayout
      title="Reset your password"
      subtitle="Or"
      linkHref="/auth/login"
      linkLabel="sign in to your account"
      error={error}
      success={success ? 'If an account exists with that email, you will receive password reset instructions.' : undefined}
      showGoogleAuth={false}
    >
      {!success ? (
        <form className="space-y-6" onSubmit={handleSubmit}>
          <Input
            label="Email address"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <Button
            type="submit"
            loading={loading}
            className="w-full"
          >
            {loading ? 'Sending...' : 'Send reset instructions'}
          </Button>
        </form>
      ) : null}
    </AuthFormLayout>
  );
} 