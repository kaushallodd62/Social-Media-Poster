import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './styles/globals.css'
import { AuthProvider } from './contexts/AuthContext'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Social Media Poster Dashboard',
  description: 'Manage and schedule your social media posts',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          <div className="min-h-screen bg-gray-100">
            {children}
          </div>
        </AuthProvider>
      </body>
    </html>
  )
} 