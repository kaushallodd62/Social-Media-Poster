export const isValidUrl = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

export const isValidImageUrl = (url: string): boolean => {
  if (!isValidUrl(url)) return false;
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp'];
  return imageExtensions.some(ext => url.toLowerCase().endsWith(ext));
};

export const isValidCaption = (caption: string): boolean => {
  return caption.length >= 10 && caption.length <= 2200;
};

export const isValidScheduleTime = (date: Date): boolean => {
  const now = new Date();
  return date > now;
}; 