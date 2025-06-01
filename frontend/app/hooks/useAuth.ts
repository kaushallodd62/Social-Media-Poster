import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { API_ENDPOINTS } from '../constants'

interface User {
  id: string
  email: string
  name: string
}

interface AuthState {
  user: User | null
  loading: boolean
  error: string | null
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    loading: true,
    error: null,
  })
  const router = useRouter()

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const response = await fetch('/api/auth/me')
      if (response.ok) {
        const user = await response.json()
        setAuthState({ user, loading: false, error: null })
      } else {
        setAuthState({ user: null, loading: false, error: null })
      }
    } catch (error) {
      setAuthState({
        user: null,
        loading: false,
        error: 'Failed to check authentication status',
      })
    }
  }

  const login = async (email: string, password: string) => {
    try {
      setAuthState(prev => ({ ...prev, loading: true, error: null }))
      const response = await fetch(API_ENDPOINTS.auth.login, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })

      if (!response.ok) {
        throw new Error('Login failed')
      }

      const user = await response.json()
      setAuthState({ user, loading: false, error: null })
      router.push('/dashboard')
    } catch (error) {
      setAuthState({
        user: null,
        loading: false,
        error: 'Login failed. Please check your credentials.',
      })
    }
  }

  const logout = async () => {
    try {
      await fetch(API_ENDPOINTS.auth.logout, { method: 'POST' })
      setAuthState({ user: null, loading: false, error: null })
      router.push('/auth/login')
    } catch (error) {
      setAuthState(prev => ({
        ...prev,
        error: 'Failed to logout. Please try again.',
      }))
    }
  }

  return {
    user: authState.user,
    loading: authState.loading,
    error: authState.error,
    login,
    logout,
  }
} 