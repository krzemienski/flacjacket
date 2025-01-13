
Windsurf File for Project - flacjacket

## Project Overview
- **Project Name:** flacjacket
- **Description:** flacjacket is a web application designed to analyze lengthy music files, such as DJ mixes or live concert recordings, from SoundCloud or YouTube. The project employs Shazam-like audio recognition technologies to identify individual tracks and provides users the ability to download these tracks in high-quality formats.
- **Tech Stack:**
  - Frontend: React
  - Backend: Flask
  - Database: PostgreSQL/MySQL/SQLite
  - Audio Download: scdl/yt-dlp
  - Audio Recognition: Dejavu/audfprint/Chromaprint + AcoustID
- **Key Features:**
  - High-quality audio downloads and processing
  - Accurate track recognition using open-source fingerprinting solutions
  - Metadata display and track download capability
  - Administrative panel for tracking and logs
  - Dockerized deployment for streamlined setup

## Project Structure
### Root Directory:
- Contains main configuration files and documentation.

### /frontend:
- Contains all frontend-related code, including components, styles, and assets.

### /components:
- URL input form
- Track list display with metadata
- Download buttons
- Loading indicators

### /assets:
- Audio files for testing
- UI/UX design mockups

### /styles:
- Global stylesheets for consistent theming
- Component-specific styles

### /backend:
- Contains all backend-related code, including API routes and database models.

### /controllers:
- Audio download control logic (scdl/yt-dlp integrations)
- Fingerprinting process handlers

### /models:
- Analysis job model
- Track metadata model

### /routes:
- POST /api/analyze
- GET /api/status/:analysis_id
- GET /api/tracks/:analysis_id
- (Optional) POST /api/download/:track_id

### /config:
- Configuration files for Flask settings, environment variables, and database connections.

### /tests:
- Contains unit and integration tests for both frontend and backend.

## Development Guidelines
- **Coding Standards:**
  - Follow PEP 8 guidelines for Python code
  - Use ESLint and Prettier for JavaScript code in React
- **Component Organization:**
  - Each component should have its own directory with JSX, CSS, and test files if applicable.

## Windsurf IDE Integration
- **Setup Instructions:**
  1. Clone the repository
  2. Use Docker to set up the development environment
  3. Ensure all dependencies are installed within the container
  4. Start the server using predefined scripts
- **Key Commands:**
  - `docker-compose up` to start entire application stack
  - `npm start` in frontend directory for React development
  - `flask run` in backend directory for API testing

## Additional Context
- **User Roles:**
  - General users access audio recognition and track downloads.
  - Admin users can view logs and manage backend processes.
- **Accessibility Considerations:**
  - Ensure high contrast and large button interfaces for easy navigation.
  - Provide clear audio quality descriptions for each downloadable track.