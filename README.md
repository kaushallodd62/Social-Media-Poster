# Social Media Poster

A full-stack application for managing and scheduling social media posts with AI-powered image ranking and caption generation.

## Project Structure

```
.
├── backend/                 # Python Flask backend
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration settings
│   ├── models.py           # SQLAlchemy models
│   ├── routes.py           # API routes
│   ├── photo_fetcher.py    # Google Photos integration
│   ├── llm_ranking_service.py  # AI-based image ranking
│   ├── requirements.txt    # Python dependencies
│   └── alembic/           # Database migrations
│       ├── versions/      # Migration scripts
│       └── env.py         # Migration environment
│
└── frontend/               # Next.js frontend
    ├── app/               # Next.js app directory
    │   ├── components/    # Reusable React components
    │   ├── lib/          # Utility libraries and API clients
    │   ├── styles/       # Global styles and CSS modules
    │   ├── types/        # TypeScript type definitions
    │   └── utils/        # Helper functions and utilities
    ├── public/           # Static assets
    └── package.json      # Node.js dependencies
```

## Prerequisites

- Docker and Docker Compose
- Google Cloud Platform account with Photos API enabled
- Google OAuth 2.0 credentials

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd social-media-poster
   ```

2. Create a `.env` file in the `backend` directory:
   ```bash
   cp backend/.env.example backend/.env
   ```
   Then edit `backend/.env` and add your:
   - Google Client ID
   - Google Client Secret
   - Flask Secret Key

3. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

4. In a new terminal, apply database migrations:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

## Services

The application consists of three services:

1. **PostgreSQL Database**
   - Database: `social_media_poster`
   - User: `app-user`
   - Port: 5432
   - Data is persisted in a Docker volume

2. **Flask Backend**
   - Port: 5000
   - Handles:
     - User authentication
     - Google Photos OAuth
     - Photo metadata storage
     - AI-powered photo ranking
     - Social media post scheduling

3. **Next.js Frontend**
   - Port: 3000
   - Displays top-ranked photos
   - Manages social media posts
   - Proxies API requests to the backend

## Database Schema

### Users
- `id`: Primary key
- `email`: User's email (unique)
- `display_name`: User's display name
- `created_at`, `updated_at`: Timestamps

### OAuth Credentials
- `id`: Primary key
- `user_id`: Foreign key to users
- `provider`: OAuth provider (e.g., 'google_photos')
- `access_token`, `refresh_token`: OAuth tokens
- `token_type`: Token type (default: 'Bearer')
- `id_token`: Google OAuth ID token
- `token_expires_at`: Token expiration time
- `scope`: OAuth scopes

### Media Items
- `id`: Primary key
- `user_id`: Foreign key to users
- `google_media_id`: Google Photos media ID
- `base_url`: Photo URL
- `filename`: Original filename
- `mime_type`: File type
- `description`: Photo description
- `creation_time`: Photo creation time
- `width`, `height`: Photo dimensions
- `exif_json`: EXIF metadata
- `tags_json`: AI-generated tags

### Ranking Sessions
- `id`: Primary key
- `user_id`: Foreign key to users
- `initiated_at`: Session start time
- `completed_at`: Session completion time
- `method`: Ranking method used
- `status`: Session status (pending/completed/failed)
- `error_message`: Error details if failed

### Media Rankings
- `id`: Primary key
- `ranking_session_id`: Foreign key to ranking sessions
- `media_item_id`: Foreign key to media items
- `technical_score`: Technical quality score
- `aesthetic_score`: Aesthetic quality score
- `combined_score`: Overall score
- `llm_reasoning`: AI reasoning about the photo
- `tags_json`: AI-generated tags

## API Endpoints

### Photos
- `GET /api/photos`: List all photos
- `GET /api/photo/<photo_id>`: Get single photo details
- `GET /api/photos/top-picks`: Get top 20 ranked photos
- `POST /api/photos/sync`: Sync photos from Google Photos
- `POST /api/photos/rank`: Start a new ranking session

### Health Check
- `GET /api/health`: Check API health status

## Features

- Google Photos Integration (OAuth 2.0)
- AI-powered Image Ranking
- Photo Metadata Extraction
- Social Media Post Scheduling
- Analytics Dashboard

## Tech Stack

### Backend
- Python 3.10
- Flask
- SQLAlchemy
- Alembic
- Google Photos API
- AI/ML Libraries (TensorFlow, CLIP)

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- React
- Heroicons

### Database
- PostgreSQL 15
- JSONB for flexible data storage
- Array types for tags

## Development

- Backend code is in the `backend` directory
- Frontend code is in the `frontend` directory
- Database migrations are in `backend/alembic/versions`
- Use `docker-compose up --build` for development
- Use `docker-compose exec backend alembic revision --autogenerate -m "description"` for new migrations

## License

MIT 