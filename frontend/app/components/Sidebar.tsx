'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { PhotoIcon, StarIcon, FolderIcon, ChartBarIcon, Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline';
import { useState } from 'react';

const navItems = [
  { name: 'Google Photos', href: '/photos', icon: PhotoIcon },
  { name: 'Top Picks', href: '/top-picks', icon: StarIcon },
  { name: 'Media Items', href: '/media', icon: FolderIcon },
  { name: 'Ranking Sessions', href: '/ranking-sessions', icon: ChartBarIcon },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const isActive = (href: string) => {
    return pathname === href || pathname.startsWith(href + '/');
  };

  const NavContent = () => (
    <>
      <div className="mb-8">
        <span className="text-2xl font-bold text-blue-600">Dashboard</span>
      </div>
      <nav className="flex-1 space-y-2">
        {navItems.map((item) => {
          const active = isActive(item.href);
          return (
            <Link 
              key={item.name} 
              href={item.href} 
              className={`flex items-center px-3 py-2 rounded-md transition-colors ${
                active
                  ? 'bg-blue-100 text-blue-700 border-r-2 border-blue-600'
                  : 'text-gray-700 hover:bg-blue-50 hover:text-blue-700'
              }`}
              onClick={() => setIsMobileMenuOpen(false)}
            >
              <item.icon className={`h-5 w-5 mr-3 ${active ? 'text-blue-600' : 'text-blue-500'}`} />
              <span className="font-medium">{item.name}</span>
            </Link>
          );
        })}
      </nav>
    </>
  );

  return (
    <>
      {/* Mobile menu button */}
      <button
        className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-md bg-white shadow-md"
        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        aria-label="Toggle menu"
      >
        {isMobileMenuOpen ? (
          <XMarkIcon className="h-6 w-6 text-gray-600" />
        ) : (
          <Bars3Icon className="h-6 w-6 text-gray-600" />
        )}
      </button>

      {/* Mobile overlay */}
      {isMobileMenuOpen && (
        <div 
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Desktop sidebar */}
      <aside className="hidden lg:flex h-full w-64 bg-gray-100 border-r shadow-md flex-col py-6 px-4">
        <NavContent />
      </aside>

      {/* Mobile sidebar */}
      <aside className={`lg:hidden fixed left-0 top-0 h-full w-64 bg-gray-100 border-r shadow-md flex flex-col py-6 px-4 z-50 transform transition-transform duration-300 ease-in-out ${
        isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="mt-12"> {/* Add margin to account for mobile menu button */}
          <NavContent />
        </div>
      </aside>
    </>
  );
} 