# FlacJacket API Testing Guide

This document provides examples of how to test all FlacJacket API endpoints using curl commands.

## Base URL
All API endpoints are relative to: `http://localhost:5001`

## API Endpoints

### 1. Start New Analysis

Start a new analysis by providing a URL to a SoundCloud or YouTube track:

```bash
curl -X POST http://localhost:5001/api/analysis \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://soundcloud.com/example/track",
    "options": {
      "min_silence_len": 1000,
      "silence_thresh": -50
    }
  }'
```

Response:
```json
{
  "analysis_id": "abc123",
  "status": "pending",
  "created_at": "2025-01-13T20:16:26-05:00"
}
```

### 2. Get Analysis Status

Check the status of an ongoing analysis:

```bash
curl -X GET http://localhost:5001/api/analysis/{analysis_id}
```

Response:
```json
{
  "analysis_id": "abc123",
  "status": "processing",
  "progress": 45,
  "tracks": [],
  "created_at": "2025-01-13T20:16:26-05:00",
  "updated_at": "2025-01-13T20:16:26-05:00"
}
```

### 3. List All Analyses

Get a list of all analyses:

```bash
curl -X GET http://localhost:5001/api/analyses
```

Response:
```json
{
  "analyses": [
    {
      "analysis_id": "abc123",
      "status": "completed",
      "tracks": [
        {
          "id": "track1",
          "start_time": 0,
          "end_time": 180,
          "duration": 180
        }
      ],
      "created_at": "2025-01-13T20:16:26-05:00"
    }
  ]
}
```

### 4. Download Track

Download a processed track:

```bash
curl -X GET http://localhost:5001/api/track/{analysis_id}/{track_id} \
  -o "track.flac"
```

### 5. Delete Analysis

Delete an analysis and its associated files:

```bash
curl -X DELETE http://localhost:5001/api/analysis/{analysis_id}
```

Response:
```json
{
  "status": "success",
  "message": "Analysis deleted successfully"
}
```
