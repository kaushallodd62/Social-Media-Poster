import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Add paths that don't require authentication
const publicPaths = [
  '/auth/login',
  '/auth/register',
  '/auth/forgot-password',
  '/auth/reset-password',
  '/auth/callback',
  '/api/auth',
];

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token');
  const { pathname } = request.nextUrl;

  // Check if the path is public
  const isPublicPath = publicPaths.some(path => pathname.startsWith(path));

  // If the path is public, allow access
  if (isPublicPath) {
    return NextResponse.next();
  }

  // If there's no token and the path is not public, redirect to login
  if (!token && !isPublicPath) {
    const url = new URL('/auth/login', request.url);
    url.searchParams.set('from', pathname);
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|public/).*)',
  ],
}; 