# FlacJacket Testing Documentation

This directory contains tests for the FlacJacket application, including both API tests, frontend tests, and audio analysis unit tests.

## Test Types

### API Tests
The `test_api.sh` script tests basic functionality of the FlacJacket API:

- **Health check**: Verifies the API is up and running
- **Create analysis**: Tests the creation of a new analysis with a valid SoundCloud URL
- **Get analysis status**: Retrieves status information for an analysis
- **List analyses**: Tests retrieving a list of analyses
- **Delete analysis**: Tests deleting an existing analysis

### Running API Tests

```bash
./tests/test_api.sh
```

The API tests use real SoundCloud URLs that have been confirmed to work with our system:

```
https://soundcloud.com/sparrowandbarbossa/maggies1
https://soundcloud.com/soundnightclub/sparrow-barbossa-live-at-sound-on-031624
https://soundcloud.com/sweetmusicofc/sweet-mixtape-135-sparrow-barbossa
```

### Frontend Tests
Frontend tests are built with Cypress and test the user interface and interaction:

#### Running Frontend Tests

```bash
cd frontend
npm run test
```

or for interactive testing:

```bash
cd frontend
npm run cypress:open
```

#### Key Frontend Test Files

- `homepage.cy.ts`: Tests basic homepage functionality, theme toggling, and analysis list
- `analysis-flow.cy.ts`: Tests the complete analysis workflow from submission to viewing results
- `material-theme.cy.ts`: Tests the theme implementation and dark/light mode
- `soundcloud-urls.cy.ts`: Tests the application's functionality with specific SoundCloud URLs

### Audio Analysis Unit Tests

Backend tests verify the audio analysis pipeline functions correctly:

```bash
cd backend
pytest
```

The test `test_audio_analysis.py` will:
- Download audio from a real SoundCloud URL
- Process the audio to detect tracks
- Verify the analysis results
- Check that track detection is working properly

These tests now use real SoundCloud URLs that are confirmed to work with our audio download system, which
has been updated to use yt-dlp for more reliable audio downloading from SoundCloud.

## Running Tests

### Running All Tests
To run all tests together (API, frontend, and SoundCloud URL tests):

```bash
./tests/run_all_tests.sh
```

### Running API Tests Only
To run just the API tests:

```bash
./tests/test_api.sh
```

### Running Frontend Tests Only
To run just the frontend tests:

```bash
cd frontend
npm run cypress
# OR for headless mode
npm run cypress:headless
```

### Running SoundCloud URL Tests Only
To run just the SoundCloud URL tests:

```bash
./tests/test_soundcloud_urls.sh
```

## Test Structure

### API Tests
API tests are contained in the `test_api.sh` script and use `curl` to make HTTP requests to the backend API.

### Frontend Tests
Frontend tests are organized in the `frontend/cypress/e2e` directory:

- `homepage.cy.ts`: Tests for the homepage functionality
- `analysis-flow.cy.ts`: Tests for the analysis submission and viewing flow
- `material-theme.cy.ts`: Tests specifically for the Material Design theme implementation
- `soundcloud-urls.cy.ts`: Comprehensive tests for the application's functionality with specific SoundCloud URLs, including:
  - Submitting each URL for analysis
  - Verifying analysis creation via API
  - Testing the complete analysis flow for each URL
  - Handling different analysis states

## Adding New Tests

### Adding New API Tests
To add new API tests, modify the `test_api.sh` script and add new test cases following the existing pattern.

### Adding New Frontend Tests
To add new frontend tests:

1. Create a new test file in the `frontend/cypress/e2e` directory
2. Write your tests using the Cypress API
3. If needed, add custom commands in `frontend/cypress/support/commands.ts`

## Continuous Integration

When setting up CI, you can use the `run_all_tests.sh` script to run all tests as part of your CI pipeline.
