
# flacjacket: Shazam-Like Audio Recognition and Track Extraction  
*(Project Prompt in Markdown for Sections 1–13, updated to emphasize high-quality audio)*

---

## 1. Project Overview

The goal of **flacjacket** is to analyze lengthy music files (e.g., DJ mixes, long sets, live concert recordings) from SoundCloud or YouTube, automatically detect the individual tracks (songs) within that long recording, and provide an interface for selecting and downloading those identified tracks.

In addition to basic segmentation (finding track boundaries), the primary aim is to **accurately identify the specific songs**—similar to how Shazam recognizes a track by its audio “fingerprint.” The system must also prioritize **highest possible audio quality** at each stage.

Key points:

1. **React** front-end where users provide a SoundCloud or YouTube URL.  
2. **Flask** backend to handle:  
   - Download of source audio with tools like `scdl` (SoundCloud) or `yt-dlp` (YouTube) at the **highest available quality**.  
   - Feeding the audio into a **Shazam-like** open-source audio recognition mechanism to identify each track by name/artist.  
3. **Track list** displayed on the front-end with identified metadata and links to:  
   - Download the recognized sub-track directly (if feasible) in **high-quality audio** or from a relevant source.  
4. **Administrative panel** to view history of processed sets and recognized tracks.  
5. **Dockerized** deployment for easy setup and reproducibility.  
6. **Audio Quality** preservation from the original download through final conversions.

---

## 2. High-Level Requirements

1. **User Input**  
   - A text field for entering SoundCloud or YouTube URLs.  
   - A “Submit/Analyze” button to start the retrieval and recognition process.

2. **Audio Retrieval**  
   - Automatically download the **highest quality** audio from the given URL using `scdl` (SoundCloud) or `yt-dlp` (YouTube).  
   - Must handle large file sizes (1–2+ hour sets).

3. **Shazam-Like Recognition**  
   - Use an open-source audio fingerprinting solution to:  
     1. Identify unique track boundaries or timestamps.  
     2. Match each segment to a known song in a fingerprint database or an external service (e.g., AcoustID/MusicBrainz).  
   - Return recognized metadata (track title, artist).

4. **Presentation of Tracks**  
   - Show a list of recognized tracks with their metadata, timestamps, and high-quality download links.  
   - Each track has a “Download” button (if available) or “Download All.”

5. **Progress Indicators**  
   - Show a loading status while the system downloads and processes the audio.

6. **Administrative Panel**  
   - Allows an admin to see a list of processed URLs, the identified tracks, and any logs or error messages.

7. **Dockerization**  
   - Provide Dockerfiles and/or a docker-compose setup to easily deploy the app and its dependencies.

8. **Audio Quality Preservation**  
   - Ensure that any sub-track or segmented download is encoded or stored in **high-quality** format (e.g., FLAC, WAV, or highest bitrate MP3/AAC feasible).  
   - Maintain or minimize loss of quality throughout the recognition pipeline.  
   - Consider user-selectable quality settings (e.g., original FLAC vs. high-bitrate MP3).

---

## 3. Detailed Use Cases

1. **User Submits a SoundCloud URL**  
   1. User enters the URL and clicks “Analyze.”  
   2. Backend downloads audio using `scdl` at highest possible quality.  
   3. Audio is processed by the fingerprinting library to identify embedded tracks.  
   4. Recognized tracks are returned (title, artist, start time, end time, etc.).  
   5. User can download individual tracks or “Download All” in **high-quality** format.

2. **User Submits a YouTube URL**  
   1. Similar to above, except audio is downloaded with `yt-dlp` in the highest available quality.  
   2. Same recognition pipeline applies.

3. **Admin Panel Usage**  
   1. Admin logs in.  
   2. A list of previously processed URLs is shown.  
   3. Admin can review recognized tracks, re-download, or re-run the process, ensuring high-quality outputs.

---

## 4. Functional Requirements

1. **File Download**  
   - Capable of fetching large audio/video content without timing out.  
   - **Always attempt highest quality or lossless** audio if possible.  
   - Store downloaded files temporarily or permanently, depending on design choices.

2. **Audio Fingerprinting & Identification**  
   - Use a library (detailed in [Section 9](#9-potential-open-source-shazam-like-libraries--fingerprinting-services)) that can generate an audio fingerprint and match it against a database or external service.  
   - If a match is found, retrieve metadata: track title, artist, possibly album, etc.  
   - If no match is found, label track as “Unknown #” or “Track #.”

3. **Track Segmentation**  
   - Not simply identifying “silence” to guess a boundary, but actually using a fingerprint-based approach to pinpoint where one recognized track ends and the next begins.  
   - Alternatively, chunk the audio in small windows, fingerprint each chunk, and group them by recognized track ID.

4. **Metadata Storage**  
   - Save recognized track metadata to a database (artist, title, any external IDs).  
   - Associate each recognized track with the main analysis job.

5. **Download Management**  
   - Provide endpoints or direct links for downloading recognized sub-tracks in high-quality format.  
   - Optionally re-encode sub-tracks using `ffmpeg`, `pydub`, or a similar tool, **prioritizing minimal quality loss**.

6. **History & Logging**  
   - Maintain logs of each analysis: date/time, duration, recognized tracks, errors.  
   - Include detail on the format/quality of downloads for admin oversight.

---

## 5. Non-Functional Requirements

1. **Scalability**  
   - The fingerprinting process can be CPU-intensive; consider a job queue if concurrency is high.

2. **Performance**  
   - Use efficient fingerprinting libraries that can handle large inputs without excessive memory usage.  
   - High-quality audio files are large; ensure adequate bandwidth and storage.

3. **Security**  
   - Admin panel protected by authentication/authorization.  
   - Input validation to avoid malicious URL injection or command vulnerabilities.

4. **Maintainability**  
   - Clean separation between front-end, back-end, and the fingerprinting library integration.  
   - Document audio quality best practices and defaults.

---

## 6. Architecture Overview

1. **Front-End (React)**  
   - Renders input forms for URLs.  
   - Shows recognized track lists and allows high-quality downloads.  
   - Connects to Flask APIs using RESTful endpoints.

2. **Back-End (Flask)**  
   - API endpoints:  
     - `POST /api/analyze` → initiates audio download and recognition.  
     - `GET /api/status/:analysis_id` → returns progress.  
     - `GET /api/tracks/:analysis_id` → fetches recognized track data.  
     - `POST /api/download/:track_id` (or `GET`) → returns sub-track audio data in high-quality format or triggers sub-track creation.  
   - Integration with external tools (`scdl`, `yt-dlp`) for downloads.  
   - Invokes audio fingerprinting solution (Section 9) for recognition.  
   - Persists job data in the database.

3. **Database**  
   - Could be PostgreSQL, MySQL, or SQLite.  
   - Entities:  
     - `analyses` (tracks each job’s status, created_at, etc.).  
     - `tracks` (references analysis, recognized track ID, metadata, timestamps, format details).

4. **Docker**  
   - `Dockerfile` for the Flask server, including fingerprinting and audio libraries.  
   - `Dockerfile` (or multi-stage build) for the React front-end.  
   - `docker-compose.yml` to spin up the entire stack together.

---

## 7. Data Model (Example)

```plaintext
analyses
---------
id (PK)
url (string)
source (enum: 'soundcloud', 'youtube', etc.)
status (enum: 'pending', 'in_progress', 'completed', 'failed')
created_at (datetime)
updated_at (datetime)

tracks
---------
id (PK)
analysis_id (FK -> analyses.id)
external_track_id (string or int)   // e.g., MusicBrainz ID, etc.
track_name (string, nullable)
artist (string, nullable)
start_time (float)
end_time (float)
download_path (string, nullable)    // if sub-track is stored locally
audio_format (string, nullable)     // e.g., flac, mp3, wav
bitrate (int, nullable)            // e.g., 320 for 320kbps
created_at (datetime)
updated_at (datetime)
```

---

## 8. Integration Details

- **SoundCloud Integration**  
  - Download with `scdl` or other utilities. Manage authentication if needed for certain content.  
  - Always retrieve the highest possible quality audio.

- **YouTube Integration**  
  - Download with `yt-dlp` in the highest available audio format.  
  - Parse URL patterns (watch links, short links, etc.).

- **Admin Panel**  
  - Could be built as a React route or a separate admin library.  
  - Displays analysis jobs, recognized tracks, logs, and possibly shows the format or bitrate used.

- **Sub-Track Download**  
  - Programmatically slice the recognized segments using `ffmpeg` or `pydub`.  
  - **Ensure minimal quality loss**—prefer a lossless or high-bitrate output format.

---

## 9. Potential Open-Source “Shazam-Like” Libraries / Fingerprinting Services

Because the system is intended as an alternative to Shazam, the focus is on audio fingerprinting and matching to a known database. Options include:

- **[Dejavu](https://github.com/worldveil/dejavu)**  
  Python-based audio fingerprinting and recognition library. You can build your own local database of fingerprints. Identifies tracks when they are played from a microphone or file.

- **[audfprint](https://github.com/dpwe/audfprint)**  
  A tool from Dan Ellis (Columbia University) for robust audio fingerprinting. Generates a hash-based fingerprint and can match segments of audio to known references.

- **AcoustID / Chromaprint**  
  - **[Chromaprint](https://acoustid.org/chromaprint)** generates acoustic fingerprints.  
  - **[AcoustID](https://acoustid.org/)** is an online service that can match these fingerprints to MusicBrainz metadata.  
  Potentially powerful if you want to leverage a large, crowdsourced database to identify tracks.

- **[MusicBrainz](https://musicbrainz.org/)** with AcoustID  
  Integrating Chromaprint with AcoustID yields track IDs from MusicBrainz, which can then provide track names, artists, albums, etc.

- **[AudioMatcher](https://github.com/rabitt/AudioMatcher)**  
  Less commonly used, but another open-source possibility.

**Implementation Approach**  
- For an “always updated” database, rely on AcoustID + MusicBrainz. This requires stable internet connectivity and an AcoustID API key.  
- If you want to store and match only specific tracks (e.g., a custom database of known content), a self-contained library like Dejavu or audfprint might suffice.  
- **Note:** The fingerprinting process can be done with compressed or uncompressed audio, but starting with highest quality audio can improve matching accuracy.

---

## 10. User Flows and UI/UX Considerations

- **Main Page**  
  - Input box for SoundCloud/YouTube URL.  
  - “Analyze” button triggers the process.  
  - Display progress or spinner while downloading and fingerprinting.  
  - Show recognized tracks with Title, Artist, Time Range, Download Button.  
  - Provide details about audio quality or default to highest.

- **Admin Panel**  
  - Protected login to ensure only authorized access.  
  - List of analyses with statuses (complete, in-progress, failed).  
  - On each analysis detail page, show recognized tracks, logs, format used, potential re-run option.

- **Error Handling**  
  - Handle download failures with user-friendly error messages.  
  - If no tracks are recognized, inform the user (e.g., “No match found for these segments”).

---

## 11. Implementation Steps

1. **Project Setup**  
   - Initialize Flask + React projects (could be a monorepo or separate repos).  
   - Docker setup for each service.

2. **File Download Module**  
   - Invoke `scdl` or `yt-dlp` to download audio at **highest quality**.  
   - Store the downloaded file path in the database.

3. **Fingerprinting & Matching**  
   - Integrate your chosen library (Dejavu, audfprint, or Chromaprint + AcoustID).  
   - For a large DJ set, consider chunking the audio or applying a sliding window to identify each track.

4. **Track Data Storage**  
   - Create `analyses` and `tracks` tables.  
   - Persist recognized metadata (title, artist, timestamps, audio format/bitrate).

5. **Sub-Track Extraction (Optional)**  
   - If you want to provide direct downloads for each recognized track, integrate `pydub` or `ffmpeg` to slice out the segments.  
   - **Maintain highest quality possible** (e.g., FLAC or high-bitrate MP3).

6. **API Endpoints**  
   - `POST /api/analyze` (start the job).  
   - `GET /api/status/:analysis_id` (progress).  
   - `GET /api/tracks/:analysis_id` (recognized tracks).  
   - (Optional) `GET /api/download/:track_id` for sub-track downloads, ensuring high-quality output.

7. **React Front-End**  
   - A form to submit URLs.  
   - A loading indicator during analysis.  
   - Display recognized tracks with metadata, times, and high-quality download buttons.

8. **Admin Panel**  
   - Implement a login flow (JWT or session-based).  
   - Show past analyses, track details, logs, formats, and bitrates.

9. **Testing & Validation**  
   - Test with short and long sets, verifying fingerprint accuracy and audio output quality.  
   - Confirm recognized metadata is correct and files are playable.

10. **Deployment**  
   - Use `docker-compose` or a similar solution.  
   - Document environment variables (DB credentials, AcoustID keys, etc.).

---

## 12. Additional Considerations

- **Job Queuing / Background Processing**  
  - Large sets can take time to fingerprint and slice. Consider Celery or RQ to handle tasks asynchronously.

- **Metadata Completeness**  
  - With external databases (MusicBrainz/AcoustID), metadata quality depends on user contributions. Some obscure tracks may remain unidentified.

- **License & Legal**  
  - Confirm that fingerprinting or downloading third-party content is allowed under relevant laws and platform terms of service.  
  - High-quality downloads may be subject to additional scrutiny.

- **Scaling**  
  - Fingerprinting large files at high fidelity can be CPU-intensive; consider horizontally scaling worker containers or implementing load balancing.  
  - Sufficient storage and bandwidth for large, high-quality files is critical.

---

## 13. Conclusion

This prompt emphasizes an audio recognition approach akin to Shazam, focusing on robust fingerprinting and track identification **and** ensuring **highest possible audio quality** throughout the pipeline. By leveraging open-source libraries (Dejavu, audfprint, Chromaprint + AcoustID, etc.) and a well-structured architecture (React front-end, Flask backend, Dockerized deployment), **flacjacket** can offer a user-friendly experience for automatically detecting and labeling tracks within long audio recordings from SoundCloud or YouTube, **while preserving audio quality**.

Use this prompt as the blueprint for generating the actual code or for guiding your development team’s implementation.
