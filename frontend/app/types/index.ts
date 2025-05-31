export interface DashboardSection {
  title: string;
  description: string;
  icon: React.ElementType;
  href: string;
  status: string;
  action: string;
}

export interface Photo {
  id: string;
  baseUrl: string;
  description: string;
  filename: string;
  mediaMetadata: {
    creationTime: string;
    width: string;
    height: string;
  };
  scores?: {
    technical: number;
    aesthetic: number;
    semantic: number;
    novelty: number;
    trendy_vibe: number;
    metadata: number;
    activity: number;
    achievement: number;
    talent: number;
    overall: number;
  };
}

export interface Post {
  id: string;
  photoId: string;
  caption: string;
  scheduledTime: string;
  status: 'draft' | 'scheduled' | 'published' | 'failed';
  platform: 'instagram' | 'twitter' | 'facebook';
  analytics?: {
    likes: number;
    comments: number;
    shares: number;
    reach: number;
  };
} 