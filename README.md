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

## Track Detection

The system uses advanced audio analysis to detect individual tracks within a mix:

1. **Download Phase**
   - Downloads audio from SoundCloud using `scdl`
   - Converts to WAV format for analysis
   - Logs file sizes and conversion details

2. **Analysis Phase**
   - Uses `librosa` for audio processing
   - Detects onsets (significant changes in audio)
   - Creates segments based on detected onsets
   - Assigns confidence scores based on segment duration

3. **Track Types**
   - `full_track`: When no clear segments are detected
   - `onset_based`: Segments detected between onsets
   - `final_segment`: Last segment to end of file

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

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/flacjacket.git
cd flacjacket
```

2. Start the application using Docker Compose:
```bash
docker compose up --build
```

That's it! The application will:
- Build all necessary containers
- Initialize the PostgreSQL database
- Automatically apply any pending migrations
- Start the Flask backend, Celery worker, and React frontend

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5001

## Services

The application consists of several services that run in Docker containers:

1. **Frontend (Next.js)**
   - Port: 3000
   - Development server with hot-reloading
   - Communicates with backend API
   - Modern UI with real-time updates

2. **Backend (Flask)**
   - Port: 5001
   - RESTful API endpoints
   - Handles audio analysis requests
   - Manages database operations
   - Coordinates with Celery worker

3. **PostgreSQL**
   - Port: 5432
   - Stores analysis results and track data
   - Persistent volume for data storage
   - Automatic health checks

4. **Redis**
   - Port: 6379
   - Message broker for Celery
   - Task queue management
   - Result backend storage

5. **Celery Worker**
   - Processes audio analysis tasks
   - Handles long-running operations
   - Manages file downloads and processing
   - Updates task status in real-time

## Development

### Database Migrations

The database migrations are handled automatically when the application starts. However, if you need to manage migrations manually:

1. Create a new migration:
```bash
docker compose exec backend flask db migrate -m "Description of changes"
```

2. Apply migrations manually:
```bash
docker compose exec backend flask db upgrade
```

3. Revert migrations:
```bash
docker compose exec backend flask db downgrade
```

## Testing

The project includes comprehensive tests using real SoundCloud URLs:

```python
SOUNDCLOUD_URLS = [
    "https://soundcloud.com/soundnightclub/sparrow-barbossa-live-at-sound-on-031624",
    "https://soundcloud.com/sweetmusicofc/sweet-mixtape-135-sparrow-barbossa",
    "https://soundcloud.com/sparrowandbarbossa/maggies1"
]
```

Run tests with:

```bash
docker compose exec backend pytest tests/test_audio_analysis.py -v
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

## API Usage

1. Start analysis:
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"url":"https://soundcloud.com/your-url"}' \
     http://localhost:5001/api/analysis
```

2. Check status:
```bash
curl http://localhost:5001/api/analysis/{analysis_id}
```

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

## Logging

The system provides detailed logging at every stage:

1. **Download Stage**
   - Track info fetching
   - Download progress
   - File sizes (MP3 and WAV)
   - Conversion details

2. **Analysis Stage**
   - Audio file properties
   - Onset detection results
   - Segment creation
   - Confidence calculations

3. **Processing Stage**
   - Database updates
   - Track entry creation
   - Processing duration

## Contributing

1. Fork the repository
2. Create your feature branch
3. Add tests for any new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
