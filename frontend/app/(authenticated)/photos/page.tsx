'use client';

import { useState, useEffect } from 'react';
import { photosApi } from '../../lib/api';
import { Photo } from '../../types';
import Image from 'next/image';
import { LoadingSpinner, Button } from '../../components/ui';

export default function PhotosPage() {
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPhotos = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await photosApi.getPhotos();
        setPhotos(data || []);
      } catch (err: unknown) {
        console.error('Error in PhotosPage:', err);
        let message = 'Failed to fetch photos. Please check the console for more details.';
        if (err && typeof err === 'object' && 'message' in err && typeof (err as { message?: string }).message === 'string') {
          message = (err as { message?: string }).message!;
        }
        setError(message);
        setPhotos([]);
      } finally {
        setLoading(false);
      }
    };

    fetchPhotos();
  }, []);

  const handleDisconnect = async () => {
    try {
      await photosApi.disconnect();
      setPhotos([]);
    } catch (err: unknown) {
      let message = 'Failed to disconnect from Google Photos';
      if (err && typeof err === 'object' && 'message' in err && typeof (err as { message?: string }).message === 'string') {
        message = (err as { message?: string }).message!;
      }
      setError(message);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading photos..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="max-w-md p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-red-600 mb-4">Error Loading Photos</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">{error}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Please make sure:
            <ul className="list-disc list-inside mt-2">
              <li>The backend server is running at {process.env.NEXT_PUBLIC_API_URL}</li>
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
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Your Photos</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            {photos.length > 0 ? `${photos.length} photos found` : 'No photos found.'}
          </p>
        </div>
        {photos.length > 0 && (
          <Button
            onClick={handleDisconnect}
            variant="danger"
          >
            Disconnect Google Photos
          </Button>
        )}
      </div>
      
      {!photos || photos.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400">No photos found.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {photos.map((photo) => (
            <div key={photo.id} className="dashboard-card">
              <div className="relative aspect-square">
                <Image
                  src={photo.baseUrl}
                  alt={photo.description || 'Photo'}
                  fill
                  className="object-cover rounded-t-lg"
                />
              </div>
              <div className="p-4">
                <h3 className="font-semibold text-lg mb-2 text-gray-900 dark:text-white">
                  {photo.description || photo.filename}
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {new Date(photo.mediaMetadata.creationTime).toLocaleDateString()}
                </p>
                {photo.scores && (
                  <div className="mt-2">
                    <div className="flex items-center">
                      <span className="text-xs text-gray-500 dark:text-gray-400 mr-2">Overall Score:</span>
                      <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                        {photo.scores.overall.toFixed(1)}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
} 