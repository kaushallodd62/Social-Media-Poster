import axios from 'axios';
import { Photo, Post } from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const photosApi = {
  getPhotos: async (): Promise<Photo[]> => {
    const response = await api.get('/photos');
    return response.data;
  },

  getTopPicks: async (): Promise<Photo[]> => {
    const response = await api.get('/photos/top-picks');
    return response.data;
  },

  rankPhotos: async (photoIds: string[]): Promise<Photo[]> => {
    const response = await api.post('/photos/rank', { photoIds });
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
    const response = await api.get('/auth/google/url');
    return response.data.url;
  },

  handleGoogleCallback: async (code: string): Promise<void> => {
    await api.post('/auth/google/callback', { code });
  },
}; 