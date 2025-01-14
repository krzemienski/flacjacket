# FlacJacket

FlacJacket is a web application that analyzes long audio files (like DJ mixes and live concert recordings) from platforms such as SoundCloud or YouTube. It identifies individual tracks within these recordings using audio fingerprinting technology and allows users to download them in high-quality formats.

## Features

- URL input support for SoundCloud and YouTube
- High-quality audio downloading
- Advanced audio fingerprinting and track detection
- Track metadata display
- High-quality track downloads
- Real-time analysis status updates

## Tech Stack

### Backend
- Flask (Python web framework)
- SQLAlchemy (Database ORM)
- Celery (Async task processing)
- yt-dlp (YouTube/SoundCloud downloading)
- librosa (Audio processing)

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- Axios for API calls

## Setup

### Prerequisites
- Python 3.8+
- Node.js 18+
- Redis (for Celery)
- PostgreSQL (recommended) or SQLite

### Backend Setup

1. Create a Python virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
flask db upgrade
```

5. Start the Flask development server:
```bash
flask run
```

6. Start Celery worker:
```bash
celery -A app.celery worker --loglevel=info
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

The application will be available at http://localhost:3000

## API Endpoints

- `POST /api/analyze` - Start a new analysis
- `GET /api/analysis/:id` - Get analysis status and results
- `GET /api/analysis` - List all analyses
- `GET /api/tracks/:id` - Get track details
- `GET /api/tracks/:id/download` - Download a track

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
