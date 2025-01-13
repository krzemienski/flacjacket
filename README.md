# FlacJacket

FlacJacket is a powerful audio analysis tool that can identify and extract individual tracks from lengthy audio files, such as DJ sets or mixtapes from SoundCloud or YouTube. It uses multiple audio fingerprinting methods to provide accurate track identification.

## Features

- Download high-quality audio from YouTube and SoundCloud
- Multiple audio fingerprinting methods:
  - **AcoustID/Chromaprint**: Industry-standard audio fingerprinting
    - Uses MusicBrainz database with over 40 million tracks
    - Highly accurate for commercial releases
    - Open-source fingerprinting algorithm
    - Supports partial matches and time offsets
  - **Dejavu**: Local fingerprinting solution
    - Fast fingerprint generation and matching
    - Custom database for specialized collections
    - Optimized for DJ sets and remixes
    - Handles time-stretched and pitch-shifted audio
  - **audfprint**: Landmark-based audio fingerprinting
    - Robust to audio degradation and noise
    - Efficient for large-scale matching
    - Good for live recordings and bootlegs
    - Handles audio speed variations
- Extract identified tracks in high-quality FLAC format
- RESTful API with Swagger documentation
- JWT authentication
- Docker support for easy deployment
- Comprehensive logging system:
  - Detailed download progress and file information
  - Analysis pipeline status and results
  - Performance metrics and timing data
  - JSON-formatted logs for easy parsing

## Prerequisites

- Docker and Docker Compose
- AcoustID API key (get one from [AcoustID](https://acoustid.org/))

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/flacjacket.git
   cd flacjacket
   ```

2. Create a `.env` file in the root directory:
   ```env
   ACOUSTID_API_KEY=your_acoustid_api_key
   SECRET_KEY=your_secret_key
   JWT_SECRET_KEY=your_jwt_secret
   ```

3. Build and start the services:
   ```bash
   docker-compose up --build
   ```

4. Access the services:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5001
   - API Documentation: http://localhost:5001/api/docs

## API Documentation

The API is documented using Swagger/OpenAPI and can be accessed at `/api/docs`. Here's a summary of the available endpoints:

### Authentication

#### `POST /api/auth/register`
Register a new user.
- Request body:
  ```json
  {
    "username": "string",
    "password": "string",
    "email": "string"
  }
  ```

#### `POST /api/auth/login`
Login and get JWT token.
- Request body:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```

### Analysis

#### `POST /api/analysis`
Start a new analysis job.
- Request body:
  ```json
  {
    "url": "string",
    "source": "youtube|soundcloud"
  }
  ```
- Response:
  ```json
  {
    "id": "integer",
    "status": "string",
    "results": {
      "acoustid": [
        {
          "id": "integer",
          "track_name": "string",
          "artist": "string",
          "start_time": "float",
          "end_time": "float",
          "confidence": "float",
          "fingerprint_method": "string",
          "metadata": "object"
        }
      ],
      "dejavu": [...],
      "audfprint": [...]
    }
  }
  ```

#### `GET /api/analysis/{analysis_id}`
Get analysis results by ID.

#### `POST /api/analysis/{analysis_id}/rerun`
Re-run analysis on an existing file.

### Tracks

#### `GET /api/tracks/{track_id}`
Get track details by ID.

#### `GET /api/tracks/{track_id}/download`
Download a track in FLAC format.

## Architecture

FlacJacket uses a microservices architecture:

- **Frontend**: React application
- **Backend**: Flask REST API
- **Databases**:
  - PostgreSQL: Main application database
  - MySQL: Dejavu fingerprint database

### Audio Processing Pipeline

1. Download high-quality audio using `yt-dlp` (YouTube) or `scdl` (SoundCloud)
2. Process audio with multiple fingerprinting methods:
   - AcoustID: Matches against MusicBrainz database
   - Dejavu: Builds and matches against local database
   - audfprint: Alternative algorithm for verification
3. Extract identified tracks using `ffmpeg`
4. Store results in database with confidence scores

## Development

### Backend Development

1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   ```

2. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   flask db upgrade
   ```

4. Start the development server:
   ```bash
   flask run
   ```

### Frontend Development

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
