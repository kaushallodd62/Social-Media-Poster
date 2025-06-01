import axios from 'axios';
import { Photo, Post } from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Enable sending cookies
});

// Helper function to get token from cookies
function getTokenFromCookies(): string | null {
  if (typeof document === 'undefined') return null;
  const match = document.cookie.match(/(?:^|; )token=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : null;
}

// Add request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = getTokenFromCookies();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', {
      status: error.response?.status,
      data: error.response?.data,
      message: error.message,
    });
    
    // If unauthorized, clear the token cookie
    if (error.response?.status === 401) {
      document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
      // Optionally redirect to login
      if (typeof window !== 'undefined') {
        window.location.href = '/auth/login';
      }
    }
    
    throw error;
  }
);

export const photosApi = {
  getPhotos: async (): Promise<Photo[]> => {
    try {
      const response = await api.get('/api/photos');
      if (!response.data || !response.data.photos) {
        console.error('Invalid response format:', response.data);
        return [];
      }
      return response.data.photos;
    } catch (error) {
      console.error('Error fetching photos:', error);
      throw new Error('Failed to fetch photos. Please check if the backend server is running.');
    }
  },

  checkConnection: async (): Promise<boolean> => {
    try {
      const response = await api.get('/api/photos/connection-status');
      return response.data.connected;
    } catch (error) {
      console.error('Error checking connection:', error);
      return false;
    }
  },

  disconnect: async (): Promise<void> => {
    try {
      await api.post('/api/photos/disconnect');
    } catch (error) {
      console.error('Error disconnecting from Google Photos:', error);
      throw new Error('Failed to disconnect from Google Photos');
    }
  },

  getTopPicks: async (): Promise<Photo[]> => {
    try {
      const response = await api.get('/api/photos/top-picks');
      return response.data;
    } catch (error) {
      console.error('Error fetching top picks:', error);
      throw new Error('Failed to fetch top picks');
    }
  },

  rankPhotos: async (photoIds: string[]): Promise<Photo[]> => {
    try {
      const response = await api.post('/api/photos/rank', { photoIds });
      return response.data;
    } catch (error) {
      console.error('Error ranking photos:', error);
      throw new Error('Failed to rank photos');
    }
  },
};

export const postsApi = {
  getPosts: async (): Promise<Post[]> => {
    try {
      const response = await api.get('/posts');
      return response.data;
    } catch (error) {
      console.error('Error fetching posts:', error);
      throw new Error('Failed to fetch posts');
    }
  },

  createPost: async (post: Omit<Post, 'id'>): Promise<Post> => {
    try {
      const response = await api.post('/posts', post);
      return response.data;
    } catch (error) {
      console.error('Error creating post:', error);
      throw new Error('Failed to create post');
    }
  },

  updatePost: async (id: string, post: Partial<Post>): Promise<Post> => {
    try {
      const response = await api.patch(`/posts/${id}`, post);
      return response.data;
    } catch (error) {
      console.error('Error updating post:', error);
      throw new Error('Failed to update post');
    }
  },

  deletePost: async (id: string): Promise<void> => {
    try {
      await api.delete(`/posts/${id}`);
    } catch (error) {
      console.error('Error deleting post:', error);
      throw new Error('Failed to delete post');
    }
  },
};

export const authApi = {
  getGoogleAuthUrl: async (): Promise<string> => {
    try {
      const response = await api.get('/api/auth/google/url');
      return response.data.url;
    } catch (error) {
      console.error('Error getting Google auth URL:', error);
      throw new Error('Failed to get Google auth URL');
    }
  },

  getGooglePhotosAuthUrl: async (): Promise<string> => {
    try {
      const response = await api.get('/api/auth/google/photos/url');
      return response.data.url;
    } catch (error) {
      console.error('Error getting Google Photos auth URL:', error);
      throw new Error('Failed to get Google Photos auth URL');
    }
  },

  handleGoogleCallback: async (code: string): Promise<void> => {
    try {
      await api.post('/api/auth/google/callback', { code });
    } catch (error) {
      console.error('Error handling Google callback:', error);
      throw new Error('Failed to handle Google callback');
    }
  },

  handleGooglePhotosCallback: async (code: string): Promise<void> => {
    try {
      await api.post('/api/auth/google/photos/callback', { code });
    } catch (error) {
      console.error('Error handling Google Photos callback:', error);
      throw new Error('Failed to handle Google Photos callback');
    }
  },
}; 