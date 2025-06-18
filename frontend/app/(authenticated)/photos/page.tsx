'use client';

import { useState } from 'react';
import Image from 'next/image';
import { LoadingSpinner, Button } from '../../components/ui';
import GooglePhotosPickerButton, { PickerMediaItem } from '../../components/features/GooglePhotosPickerButton';
import MediaGrid from '../../components/features/MediaGrid';
import { useAuth } from '../../contexts/AuthContext';

/**
 * Main page for selecting and displaying media from Google Photos Picker.
 */
export default function PhotosPage() {
  const { token } = useAuth();
  const [mediaItems, setMediaItems] = useState<PickerMediaItem[]>([]);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  /**
   * Handles selection toggle for a media item.
   * @param id Media item ID
   */
  const handleSelect = (id: string) => {
    setSelectedIds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  /**
   * Handles Analyze Selected button click.
   */
  const handleAnalyzeSelected = () => {
    // TODO: Send selected media to backend for AI analysis
    alert(`Selected for analysis: ${Array.from(selectedIds).join(', ')}`);
  };

  /**
   * Handles media selection from Picker and saves to backend.
   */
  const handlePickerSelect = async (items: PickerMediaItem[]) => {
    setMediaItems(items);
    setSelectedIds(new Set());
    setSaving(true);
    setSaveError(null);
    try {
      const res = await fetch('/api/media/items/batch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(items),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || 'Failed to save media items');
      }
      // Optionally update mediaItems with DB IDs from response
      // const savedItems = await res.json();
      // setMediaItems(savedItems);
    } catch (err: any) {
      setSaveError(err.message || 'Failed to save media items');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Select Media from Google Photos</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            {mediaItems.length > 0 ? `${mediaItems.length} media items selected` : 'No media selected yet.'}
          </p>
        </div>
        <GooglePhotosPickerButton onSelect={handlePickerSelect} />
      </div>

      {saveError && (
        <div className="mb-6 p-4 bg-red-100 text-red-700 rounded">
          {saveError}
        </div>
      )}

      {saving && (
        <div className="min-h-[200px] flex items-center justify-center">
          <LoadingSpinner size="lg" text="Saving media..." />
        </div>
      )}

      {!saving && (
        <>
          <MediaGrid mediaItems={mediaItems} selectedIds={selectedIds} onSelect={handleSelect} />
          {mediaItems.length > 0 && (
            <div className="flex justify-end mt-8">
              <Button
                onClick={handleAnalyzeSelected}
                variant="primary"
                disabled={selectedIds.size === 0}
              >
                Analyze Selected
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
} 