# Cursor Rules for Project

## Project Overview
### Project Name: flacjacket
- **Description:**
  flacjacket enables users to analyze lengthy music files from SoundCloud or YouTube. It detects and extracts individual tracks within these recordings using Shazam-like audio recognition techniques while preserving high audio quality.
- **Tech Stack:**
  - Frontend: React
  - Backend: Flask
  - Database: PostgreSQL/MySQL/SQLite
  - Audio Tools: scdl, yt-dlp
  - Audio Recognition: Dejavu, audfprint, Chromaprint + AcoustID
  - Deployment: Docker
- **Key Features:**
  - Audio analysis and track identification
  - High-quality audio extraction
  - Administrative panel for process oversight
  - User-friendly interface for entering URLs and downloading tracks

## Project Structure
### Root Directory:
Contains the main configuration files (Dockerfile, docker-compose.yml) and documentation README.md.

### /frontend:
Handles all frontend-related code and UI components.
- /components:
  - TrackList
  - URLForm
  - DownloadButton
- /assets:
  - Logo
  - Icons
- /styles:
  - App.css
  - Components.css

### /backend:
Includes backend logic for API routes and audio processing functionalities.
- /controllers:
  - analysisController.py
  - trackController.py
- /models:
  - analysisModel.py
  - trackModel.py
- /routes:
  - api.py
- /config:
  - settings.py
- /tests:
  - test_analysis.py
  - test_tracks.py

## Development Guidelines
- **Coding Standards:** Use PEP 8 for Python; follow Airbnb’s style guide for React/JavaScript.
- **Component Organization:** Separate components logically based on function; reuse common components across the application.

## Cursor IDE Integration
- **Setup Instructions:**
  1. Clone the repository.
  2. Run docker-compose up to start the application.
  3. Use Windsurf or VS Code for editing; ensure Docker is running for API calls.
- **Key Commands:**
  - `npm start` for the frontend
  - `flask run` or through Docker for the backend

## Additional Context
- **User Roles:** Admins can access backend logs and rerun analysis; users input URLs and download tracks.
- **Accessibility Considerations:** Ensure text readability and keyboard navigability to enhance usability.