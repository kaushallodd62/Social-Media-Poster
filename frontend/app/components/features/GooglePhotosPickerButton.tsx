import { Button } from '../ui';
import { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';

/**
 * Represents a media item selected from Google Photos Picker.
 */
export type PickerMediaItem = {
  id: string;
  baseUrl: string;
  filename: string;
  mimeType: string;
  description?: string;
  creationTime?: string;
  duration?: string;
  thumbnailUrl?: string;
};

/**
 * Loads the Google API script if not already loaded.
 * @returns {Promise<void>} Resolves when the script is loaded.
 */
function loadGoogleApiScript(): Promise<void> {
  return new Promise((resolve, reject) => {
    if (typeof window === 'undefined') return reject('Not in browser');
    if ((window as any).gapi && (window as any).google) return resolve();
    const script = document.createElement('script');
    script.src = 'https://apis.google.com/js/api.js';
    script.async = true;
    script.onload = () => {
      // Load the picker API
      (window as any).gapi.load('picker', resolve);
    };
    script.onerror = reject;
    document.body.appendChild(script);
  });
}

/**
 * Loads the Google Identity Services script if not already loaded.
 * @returns {Promise<void>} Resolves when the script is loaded.
 */
function loadGoogleIdentityScript(): Promise<void> {
  return new Promise((resolve, reject) => {
    if (typeof window === 'undefined') return reject('Not in browser');
    if ((window as any).google && (window as any).google.accounts) return resolve();
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.onload = () => resolve();
    script.onerror = reject;
    document.body.appendChild(script);
  });
}

/**
 * Gets an OAuth 2.0 access token for the Picker API using Google Identity Services.
 * @returns {Promise<string>} Resolves with the access token string.
 */
async function getAccessToken(): Promise<string> {
  await loadGoogleIdentityScript();
  return new Promise((resolve, reject) => {
    const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
    if (!clientId) return reject('Google Client ID not set');
    (window as any).google.accounts.oauth2.requestAccessToken({
      client_id: clientId,
      scope: 'https://www.googleapis.com/auth/photospicker.mediaitems.readonly',
      prompt: 'consent',
      callback: (response: any) => {
        if (response && response.access_token) {
          resolve(response.access_token);
        } else {
          reject('Failed to get access token');
        }
      },
      error_callback: (err: any) => reject(err),
    });
  });
}

/**
 * Custom hook to handle Google Photos Picker logic.
 * Handles loading state, error/success feedback, and picker launch.
 * @param onSelect Callback to handle selected media items.
 * @param accessToken Optional access token to use directly.
 * @returns Object with loading, error, success, openPicker, and clearSelection.
 */
function useGooglePhotosPicker(
  onSelect: (items: PickerMediaItem[]) => void,
  accessToken?: string | null
): {
  loading: boolean;
  error: string | null;
  success: string | null;
  openPicker: () => Promise<void>;
  clearSelection: () => void;
} {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  /**
   * Launches the Google Photos Picker API and calls onSelect with selected media.
   */
  const openPicker = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await loadGoogleApiScript();
      let token = accessToken;
      if (!token) {
        token = await getAccessToken();
      }
      const view = (window as any).google.picker.ViewId.PHOTOS;
      const picker = new (window as any).google.picker.PickerBuilder()
        .addView(new (window as any).google.picker.View(view))
        .setOAuthToken(token)
        .setDeveloperKey(process.env.NEXT_PUBLIC_GOOGLE_API_KEY)
        .setCallback((data: any) => {
          if (data.action === (window as any).google.picker.Action.PICKED) {
            const items: PickerMediaItem[] = (data.docs || []).map((doc: any) => ({
              id: doc.id,
              baseUrl: doc.url,
              filename: doc.name,
              mimeType: doc.mimeType,
              description: doc.description,
              creationTime: doc.creationTime,
              duration: doc.duration,
              thumbnailUrl: doc.thumbnails && doc.thumbnails[0] && doc.thumbnails[0].url,
            }));
            onSelect(items);
            setSuccess('Media selected successfully!');
          } else if (data.action === (window as any).google.picker.Action.CANCEL) {
            setError('Picker cancelled by user.');
          }
        })
        .build();
      picker.setVisible(true);
    } catch (err: any) {
      setError(typeof err === 'string' ? err : 'Failed to load Google Photos Picker.');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Clears the current selection and feedback.
   */
  const clearSelection = () => {
    setSuccess(null);
    setError(null);
    onSelect([]);
  };

  return { loading, error, success, openPicker, clearSelection };
}

/**
 * Button to launch Google Photos Picker and clear selection.
 * Accepts accessToken as a prop (from AuthContext or login).
 * @param onSelect Callback to handle selected media items.
 * @param accessToken Optional access token to use directly.
 * @returns JSX.Element
 */
export default function GooglePhotosPickerButton({
  onSelect,
  accessToken
}: {
  onSelect: (items: PickerMediaItem[]) => void;
  accessToken?: string | null;
}): JSX.Element {
  const { loading, error, success, openPicker, clearSelection } = useGooglePhotosPicker(onSelect, accessToken);
  return (
    <div className="flex flex-col items-end gap-2">
      <div className="flex gap-2">
        <Button onClick={openPicker} variant="primary" disabled={loading}>
          {loading ? 'Loading Picker...' : 'Select from Google Photos'}
        </Button>
        <Button onClick={clearSelection} variant="secondary">
          Clear Selection
        </Button>
      </div>
      {error && <div className="mt-2 text-red-600 text-sm">{error}</div>}
      {success && <div className="mt-2 text-green-600 text-sm">{success}</div>}
    </div>
  );
} 