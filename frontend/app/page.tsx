'use client';

import { useState } from 'react';
import { 
  PhotoIcon, 
  CalendarIcon, 
  ChartBarIcon, 
  PencilSquareIcon,
  ClockIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import Link from 'next/link';

export default function Dashboard() {
  const [isConnected, setIsConnected] = useState(false);

  const dashboardSections = [
    {
      title: 'Google Photos',
      description: 'Connect your Google Photos account',
      icon: PhotoIcon,
      href: '/photos',
      status: isConnected ? 'Connected' : 'Not Connected',
      action: isConnected ? 'Manage' : 'Connect'
    },
    {
      title: 'Top Picks',
      description: 'View and filter your best photos',
      icon: ArrowPathIcon,
      href: '/top-picks',
      status: 'Ready',
      action: 'View'
    },
    {
      title: 'Photo Editor',
      description: 'Edit and enhance your photos',
      icon: PencilSquareIcon,
      href: '/editor',
      status: 'Ready',
      action: 'Edit'
    },
    {
      title: 'Caption Generator',
      description: 'Generate and edit captions',
      icon: PencilSquareIcon,
      href: '/captions',
      status: 'Ready',
      action: 'Generate'
    },
    {
      title: 'Post Scheduler',
      description: 'Schedule and monitor posts',
      icon: CalendarIcon,
      href: '/scheduler',
      status: 'Ready',
      action: 'Schedule'
    },
    {
      title: 'Analytics',
      description: 'View post performance metrics',
      icon: ChartBarIcon,
      href: '/analytics',
      status: 'Ready',
      action: 'View'
    }
  ];

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {dashboardSections.map((section) => (
            <div key={section.title} className="dashboard-card">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <section.icon className="h-8 w-8 text-blue-600" />
                  <div className="ml-4">
                    <h2 className="text-lg font-semibold text-gray-900">{section.title}</h2>
                    <p className="text-sm text-gray-500">{section.description}</p>
                  </div>
                </div>
                <span className="text-sm text-gray-500">{section.status}</span>
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
        <div className="mt-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
          <div className="dashboard-card">
            <div className="space-y-4">
              <div className="flex items-center text-sm text-gray-500">
                <ClockIcon className="h-5 w-5 mr-2" />
                <span>No recent activity</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
} 