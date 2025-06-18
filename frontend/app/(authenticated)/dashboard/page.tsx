"use client";

import { useState, useEffect } from 'react';
import {
  PhotoIcon,
  ChartBarIcon,
  ClockIcon,
  StarIcon,
  FolderIcon,
} from '@heroicons/react/24/outline';
import Link from 'next/link';
import { photosApi } from '../../lib/api';
import { DashboardSection } from '../../types';
import { LoadingSpinner } from '../../components/ui';

export default function Dashboard() {
  const [isPhotosConnected, setIsPhotosConnected] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkPhotosConnection = async () => {
      try {
        const isConnected = await photosApi.checkConnection();
        setIsPhotosConnected(isConnected);
      } catch (error) {
        setIsPhotosConnected(false);
      } finally {
        setLoading(false);
      }
    };

    checkPhotosConnection();
  }, []);

  const dashboardSections: DashboardSection[] = [
    {
      title: 'Google Photos',
      description: 'Pick photos from your Google Photos account as needed. No persistent connection required.',
      icon: PhotoIcon,
      href: '/photos',
      action: 'Pick Photos',
      status: '',
    },
    {
      title: 'Top Picks',
      description: 'View your top-ranked photos',
      icon: StarIcon,
      href: '/top-picks',
      status: 'View',
      action: 'View',
    },
    {
      title: 'Media Items',
      description: 'Browse and manage your uploaded media',
      icon: FolderIcon,
      href: '/media',
      status: 'Browse',
      action: 'Browse',
    },
    {
      title: 'Ranking Sessions',
      description: 'View and create photo ranking sessions',
      icon: ChartBarIcon,
      href: '/ranking-sessions',
      status: 'View',
      action: 'View',
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <LoadingSpinner size="lg" text="Loading dashboard..." />
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8 transition-colors duration-300">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Manage your social media content and analytics
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 transition-colors duration-300">
        {dashboardSections.map((section) => (
          <div key={section.title} className="dashboard-card transition-colors duration-300">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <section.icon className="h-8 w-8 text-primary-600 dark:text-primary-400" />
                <div className="ml-4">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white">{section.title}</h2>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{section.description}</p>
                </div>
              </div>
              {section.status && section.title !== 'Google Photos' && (
                <span className={`text-sm px-2 py-1 rounded-full transition-colors duration-200 
                  bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200`}>
                  {section.status}
                </span>
              )}
            </div>
            <div className="mt-4">
              <Link
                href={section.href}
                className="btn-primary inline-flex items-center"
              >
                {section.action}
              </Link>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Activity */}
      <div className="mt-8 transition-colors duration-300">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Activity</h2>
        <div className="dashboard-card transition-colors duration-300">
          <div className="space-y-4">
            <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
              <ClockIcon className="h-5 w-5 mr-2" />
              <span>No recent activity</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 