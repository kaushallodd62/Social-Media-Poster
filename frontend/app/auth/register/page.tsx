'use client';

import { useState } from 'react';
import { useAuth } from '@/app/contexts/AuthContext';
import AuthFormLayout from '@/app/components/AuthFormLayout';
import { Input, Button } from '@/app/components/ui';

interface FormErrors {
  displayName?: string;
  email?: string;
  password?: string;
}

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [error, setError] = useState('');
  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(false);
  const { register, googleLogin } = useAuth();

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!displayName) {
      newErrors.displayName = 'Display name is required';
    } else if (displayName.length < 2) {
      newErrors.displayName = 'Display name must be at least 2 characters';
    }

    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password)) {
      newErrors.password = 'Password must contain at least one uppercase letter, one lowercase letter, and one number';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setErrors({});

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      await register(email, password, displayName);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    try {
      await googleLogin();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  return (
    <AuthFormLayout
      title="Create your account"
      subtitle="Or"
      linkHref="/auth/login"
      linkLabel="sign in to your existing account"
      error={error}
      onGoogleAuth={handleGoogleLogin}
      googleButtonText="Sign up with Google"
    >
      <form className="space-y-6" onSubmit={handleSubmit}>
        <Input
          label="Display Name"
          type="text"
          required
          value={displayName}
          onChange={(e) => {
            setDisplayName(e.target.value);
            if (errors.displayName) {
              setErrors(prev => ({ ...prev, displayName: undefined }));
            }
          }}
          error={errors.displayName}
        />

        <Input
          label="Email address"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
            if (errors.email) {
              setErrors(prev => ({ ...prev, email: undefined }));
            }
          }}
          error={errors.email}
        />

        <Input
          label="Password"
          type="password"
          autoComplete="new-password"
          required
          value={password}
          onChange={(e) => {
            setPassword(e.target.value);
            if (errors.password) {
              setErrors(prev => ({ ...prev, password: undefined }));
            }
          }}
          showPasswordToggle
          error={errors.password}
        />

        <Button
          type="submit"
          loading={loading}
          className="w-full"
        >
          {loading ? 'Creating account...' : 'Create account'}
        </Button>
      </form>
    </AuthFormLayout>
  );
} 