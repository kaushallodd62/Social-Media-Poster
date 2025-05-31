# Social Media Poster

A full-stack application for managing and scheduling social media posts with AI-powered image ranking and caption generation.

## Project Structure

```
.
├── backend/                 # Python FastAPI backend
│   ├── app.py              # Main FastAPI application
│   ├── llm_ranking_service.py  # LLM-based image ranking service
│   ├── photo_fetcher.py    # Google Photos integration
│   └── requirements.txt    # Python dependencies
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

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file with:
   ```
   COHERE_API_KEY=your_cohere_api_key
   ```

5. Run the backend server:
   ```bash
   uvicorn app:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Features

- Google Photos Integration (OAuth 2.0)
- AI-powered Image Ranking
- Photo Editing
- Caption Generation
- Post Scheduling
- Analytics Dashboard

## Tech Stack

### Backend
- Python
- FastAPI
- Cohere AI
- Google Photos API

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- React
- Heroicons 