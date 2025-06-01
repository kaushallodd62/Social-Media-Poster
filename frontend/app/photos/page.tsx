'use client';

import { useState, useEffect } from 'react';
import { photosApi } from '../lib/api';
import { Photo } from '../types';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { useAuth } from '../contexts/AuthContext';

export default function PhotosPage() {
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { user } = useAuth();

  useEffect(() => {
    const fetchPhotos = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await photosApi.getPhotos();
        setPhotos(data || []);
      } catch (err: any) {
        console.error('Error in PhotosPage:', err);
        setError(err.message || 'Failed to fetch photos. Please check the console for more details.');
        setPhotos([]);
      } finally {
        setLoading(false);
      }
    };

    fetchPhotos();
  }, []);

  const handleConnect = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/google/photos/url`);
      const data = await response.json();
      window.location.href = data.url;
    } catch (err: any) {
      setError(err.message || 'Failed to connect to Google Photos');
    }
  };

  const handleDisconnect = async () => {
    try {
      await photosApi.disconnect();
      setPhotos([]);
    } catch (err: any) {
      setError(err.message || 'Failed to disconnect from Google Photos');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="max-w-md p-6 bg-white rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-red-600 mb-4">Error Loading Photos</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <p className="text-sm text-gray-500">
            Please make sure:
            <ul className="list-disc list-inside mt-2">
              <li>The backend server is running at {process.env.NEXT_PUBLIC_API_URL}</li>
              <li>You have authenticated with Google Photos</li>
              <li>Check the browser console for more details</li>
            </ul>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Your Photos</h1>
        {photos.length > 0 ? (
          <button
            onClick={handleDisconnect}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
          >
            Disconnect Google Photos
          </button>
        ) : (
          <button
            onClick={handleConnect}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Connect Google Photos
          </button>
        )}
      </div>
      
      {!photos || photos.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No photos found. Please connect your Google Photos account to get started.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {photos.map((photo) => (
            <div key={photo.id} className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="relative aspect-square">
                <Image
                  src={photo.baseUrl}
                  alt={photo.description || 'Photo'}
                  fill
                  className="object-cover"
                />
              </div>
              <div className="p-4">
                <h3 className="font-semibold text-lg mb-2">
                  {photo.description || photo.filename}
                </h3>
                <p className="text-sm text-gray-500">
                  {new Date(photo.mediaMetadata.creationTime).toLocaleDateString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
} 