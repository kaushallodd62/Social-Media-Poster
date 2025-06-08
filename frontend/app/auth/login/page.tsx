'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import Link from 'next/link';
import AuthFormLayout from '../../components/AuthFormLayout';
import { Input, Button, Alert } from '../../components/ui';
import { useRouter } from 'next/navigation';

interface FormErrors {
  email?: string;
  password?: string;
}

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const { login, googleLogin } = useAuth();
  const router = useRouter();

  // Check for remembered email on component mount
  useEffect(() => {
    const rememberedEmail = localStorage.getItem('rememberedEmail');
    if (rememberedEmail) {
      setEmail(rememberedEmail);
      setRememberMe(true);
    }
  }, []);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
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
      // Handle remember me
      if (rememberMe) {
        localStorage.setItem('rememberedEmail', email);
      } else {
        localStorage.removeItem('rememberedEmail');
      }

      await login(email, password);
      router.push('/dashboard');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      
      // Provide more specific error messages
      if (errorMessage.toLowerCase().includes('invalid credentials')) {
        setError('Invalid email or password. Please try again.');
      } else if (errorMessage.toLowerCase().includes('network')) {
        setError('Network error. Please check your connection and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setLoading(true);
    try {
      await googleLogin();
      router.push('/dashboard');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthFormLayout
      title="Welcome back"
      subtitle="Don't have an account?"
      linkHref="/auth/register"
      linkLabel="Sign up"
      error={error && <div aria-live="polite">{error}</div>}
      onGoogleAuth={handleGoogleLogin}
      googleButtonText="Sign in with Google"
    >
      <form className="space-y-6" onSubmit={handleSubmit} noValidate>
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
          error={errors.email || undefined}
          disabled={loading}
          aria-describedby={errors.email ? 'email-error' : undefined}
        />

        <Input
          label="Password"
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(e) => {
            setPassword(e.target.value);
            if (errors.password) {
              setErrors(prev => ({ ...prev, password: undefined }));
            }
          }}
          showPasswordToggle
          error={errors.password || undefined}
          disabled={loading}
          aria-describedby={errors.password ? 'password-error' : undefined}
        />

        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <input
              id="remember-me"
              name="remember-me"
              type="checkbox"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              disabled={loading}
            />
            <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-900">
              Remember me
            </label>
          </div>

          <div className="text-sm">
            <Link 
              href="/auth/forgot-password" 
              className="font-medium text-blue-600 hover:text-blue-500 transition-colors duration-200"
              tabIndex={loading ? -1 : 0}
              aria-disabled={loading}
              style={loading ? { pointerEvents: 'none', opacity: 0.5 } : {}}
            >
              Forgot your password?
            </Link>
          </div>
        </div>

        <Button
          type="submit"
          loading={loading}
          className="w-full transition-all duration-200 hover:shadow-lg"
          disabled={loading}
        >
          {loading ? 'Signing in...' : 'Sign in'}
        </Button>
        <Button
          type="button"
          onClick={handleGoogleLogin}
          loading={loading}
          className="w-full mt-2"
          disabled={loading}
        >
          Sign in with Google
        </Button>
      </form>
    </AuthFormLayout>
  );
} 