import Image from 'next/image';
import { PickerMediaItem } from './GooglePhotosPickerButton';

/**
 * MediaGrid displays a grid of media items with selection checkboxes.
 */
export default function MediaGrid({ mediaItems, selectedIds, onSelect }: {
  mediaItems: PickerMediaItem[];
  selectedIds: Set<string>;
  onSelect: (id: string) => void;
}) {
  if (mediaItems.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 dark:text-gray-400">No media selected. Click the button above to pick photos or videos.</p>
      </div>
    );
  }
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {mediaItems.map((item) => (
        <div key={item.id} className="dashboard-card group focus-within:ring-2 focus-within:ring-blue-500">
          <label className="block cursor-pointer">
            <div className="relative aspect-square">
              {item.mimeType.startsWith('image/') ? (
                <Image
                  src={item.baseUrl}
                  alt={item.description || item.filename}
                  fill
                  className="object-cover rounded-t-lg"
                />
              ) : (
                <div className="relative w-full h-full bg-black rounded-t-lg flex items-center justify-center">
                  <Image
                    src={item.thumbnailUrl || item.baseUrl}
                    alt={item.description || item.filename}
                    fill
                    className="object-cover opacity-70"
                  />
                  <span className="absolute inset-0 flex items-center justify-center">
                    <svg className="w-12 h-12 text-white opacity-90" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" /></svg>
                  </span>
                  {item.duration && (
                    <span className="absolute bottom-2 right-2 bg-black bg-opacity-70 text-white text-xs px-2 py-1 rounded">
                      {item.duration}
                    </span>
                  )}
                </div>
              )}
            </div>
            <div className="p-4">
              <h3 className="font-semibold text-lg mb-2 text-gray-900 dark:text-white">
                {item.description || item.filename}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {item.creationTime ? new Date(item.creationTime).toLocaleDateString() : ''}
              </p>
              <div className="mt-2 flex items-center">
                <input
                  type="checkbox"
                  className="form-checkbox h-5 w-5 text-blue-600"
                  checked={selectedIds.has(item.id)}
                  onChange={() => onSelect(item.id)}
                  aria-label={`Select ${item.filename} for analysis`}
                />
                <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Select for AI analysis</span>
              </div>
            </div>
          </label>
        </div>
      ))}
    </div>
  );
} 