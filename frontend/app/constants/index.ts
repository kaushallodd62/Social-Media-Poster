export const APP_CONFIG = {
  name: 'Social Media Poster',
  version: '0.1.0',
  description: 'A social media management and posting application',
}

export const API_ENDPOINTS = {
  auth: {
    login: '/api/auth/login',
    register: '/api/auth/register',
    logout: '/api/auth/logout',
  },
  posts: {
    create: '/api/posts',
    list: '/api/posts',
    get: (id: string) => `/api/posts/${id}`,
    update: (id: string) => `/api/posts/${id}`,
    delete: (id: string) => `/api/posts/${id}`,
  },
}

export const ROUTES = {
  home: '/',
  dashboard: '/dashboard',
  auth: {
    login: '/auth/login',
    register: '/auth/register',
  },
  posts: {
    create: '/posts/create',
    list: '/posts',
    edit: (id: string) => `/posts/${id}/edit`,
  },
}

export const THEME = {
  light: 'light',
  dark: 'dark',
  system: 'system',
} 