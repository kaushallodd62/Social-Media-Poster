import axios from 'axios';
import { Photo, Post } from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
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
    const response = await api.get('/api/photos/top-picks');
    return response.data;
  },

  rankPhotos: async (photoIds: string[]): Promise<Photo[]> => {
    const response = await api.post('/api/photos/rank', { photoIds });
    return response.data;
  },
};

export const postsApi = {
  getPosts: async (): Promise<Post[]> => {
    const response = await api.get('/posts');
    return response.data;
  },

  createPost: async (post: Omit<Post, 'id'>): Promise<Post> => {
    const response = await api.post('/posts', post);
    return response.data;
  },

  updatePost: async (id: string, post: Partial<Post>): Promise<Post> => {
    const response = await api.patch(`/posts/${id}`, post);
    return response.data;
  },

  deletePost: async (id: string): Promise<void> => {
    await api.delete(`/posts/${id}`);
  },
};

export const authApi = {
  getGoogleAuthUrl: async (): Promise<string> => {
    const response = await api.get('/api/auth/google/url');
    return response.data.url;
  },

  getGooglePhotosAuthUrl: async (): Promise<string> => {
    const response = await api.get('/api/auth/google/photos/url');
    return response.data.url;
  },

  handleGoogleCallback: async (code: string): Promise<void> => {
    await api.post('/api/auth/google/callback', { code });
  },

  handleGooglePhotosCallback: async (code: string): Promise<void> => {
    await api.post('/api/auth/google/photos/callback', { code });
  },
}; 