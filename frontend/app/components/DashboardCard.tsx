import { ElementType } from 'react';
import Link from 'next/link';

interface DashboardCardProps {
  title: string;
  description: string;
  icon: ElementType;
  href: string;
  status: string;
  action: string;
}

export default function DashboardCard({
  title,
  description,
  icon: Icon,
  href,
  status,
  action,
}: DashboardCardProps) {
  return (
    <div className="dashboard-card transition-colors duration-300">
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <Icon className="h-8 w-8 text-primary-600 dark:text-primary-400" />
          <div className="ml-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">{description}</p>
          </div>
        </div>
        <span className="text-sm px-2 py-1 rounded-full transition-colors duration-200
          bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200
        ">{status}</span>
      </div>
      <div className="mt-4">
        <Link 
          href={href}
          className="btn-primary inline-flex items-center"
        >
          {action}
        </Link>
      </div>
    </div>
  );
} 