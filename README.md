# FlacJacket

FlacJacket is a web application that analyzes long audio files (like DJ mixes and live concert recordings) from platforms such as SoundCloud or YouTube. It identifies individual tracks within these recordings using audio fingerprinting technology and allows users to download them in high-quality formats.

## Features

- URL input support for SoundCloud and YouTube
- High-quality audio downloading
- Advanced audio fingerprinting and track detection
- Track metadata display
- High-quality track downloads
- Real-time analysis status updates
- Task monitoring dashboard

## Tech Stack

### Backend
- Flask (Python web framework)
- SQLAlchemy (Database ORM)
- Celery (Async task processing)
- yt-dlp (YouTube downloading)
- scdl (SoundCloud downloading)
- librosa (Audio processing)
- PostgreSQL (Database)
- Redis (Message broker)
- Flower (Celery monitoring)
- Structlog (Structured logging)

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- Material-UI components
- React Hooks for state management

## Setup

### Prerequisites
- Docker and Docker Compose
- Git

### Quick Start with Docker

1. Clone the repository:
```bash
git clone https://github.com/yourusername/flacjacket.git
cd flacjacket
```

2. Start the application:
```bash
docker compose up -d
```

The services will be available at:
- Frontend: http://localhost:3003
- Backend API: http://localhost:5001
- Task Monitor: http://localhost:5555

### Manual Development Setup

#### Backend Setup

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

7. Start Flower monitoring (optional):
```bash
celery -A app.celery flower
```

#### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

## API Endpoints

### Analysis
- `POST /api/analysis` - Start a new analysis
  ```json
  {
    "url": "https://soundcloud.com/example/track"
  }
  ```
- `GET /api/analysis/:id` - Get analysis status and results
- `GET /api/analyses` - List all analyses
- `DELETE /api/analysis/:id` - Delete an analysis

### Health Check
- `GET /api/health` - Check API health status

## Architecture

The application is composed of several Docker containers:
- `frontend`: Next.js web application
- `backend`: Flask API server
- `celery_worker`: Async task processor for audio analysis
- `postgres`: PostgreSQL database
- `redis`: Message broker for Celery
- `flower`: Celery task monitoring dashboard

### Monitoring and Logging

The application includes comprehensive monitoring and logging:

1. **Task Monitor Dashboard**
   - Access at http://localhost:5555
   - Real-time task status and progress
   - Historical task data and statistics
   - Worker status and resource usage

2. **Structured Logging**
   - Detailed task execution logs
   - Error tracking and debugging information
   - Performance metrics
   - Audit trail for all operations

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
