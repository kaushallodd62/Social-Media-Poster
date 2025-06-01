# Frontend Application

This is the frontend application built with Next.js 13+ using the App Router architecture.

## Directory Structure

```
frontend/
├── app/                    # Main application code
│   ├── (authenticated)/    # Routes requiring authentication
│   ├── (unauthenticated)/  # Public routes
│   ├── auth/              # Authentication related routes
│   ├── dashboard/         # Dashboard specific routes
│   ├── components/        # React components
│   │   ├── ui/           # Basic UI components
│   │   ├── features/     # Feature-specific components
│   │   ├── layouts/      # Layout components
│   │   └── __tests__/    # Component tests
│   ├── hooks/            # Custom React hooks
│   ├── contexts/         # React contexts
│   ├── utils/            # Utility functions
│   ├── styles/           # Global styles
│   ├── lib/              # External integrations
│   ├── types/            # TypeScript types
│   ├── constants/        # Application constants
│   └── assets/           # Static assets
├── public/               # Public static files
├── __tests__/           # Global tests
└── __mocks__/           # Test mocks
```

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
Copy `.env.local.example` to `.env.local` and fill in the required values.

3. Run the development server:
```bash
npm run dev
```

## Development Guidelines

### Component Organization
- Place reusable UI components in `components/ui/`
- Feature-specific components go in `components/features/`
- Layout components belong in `components/layouts/`

### Testing
- Write tests alongside components in `__tests__` directories
- Use Jest and React Testing Library for testing
- Place global mocks in `__mocks__` directory

### Styling
- Use Tailwind CSS for styling
- Global styles are in `styles/` directory
- Component-specific styles should be co-located with components

### TypeScript
- All components should be written in TypeScript
- Types are defined in `types/` directory
- Use strict type checking

## Build and Deployment

1. Build the application:
```bash
npm run build
```

2. Start the production server:
```bash
npm start
```

## Docker Support

The application includes Docker support. To build and run:

```bash
docker build -t frontend .
docker run -p 3000:3000 frontend
``` 