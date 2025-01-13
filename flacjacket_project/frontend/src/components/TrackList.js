import React from 'react';

function TrackList({ tracks }) {
    return (
        <div>
            <h2>Recognized Tracks</h2>
            <ul>
                {tracks.map((track, index) => (
                    <li key={index}>
                        <strong>{track.track_name}</strong> by {track.artist} ({track.start_time} - {track.end_time})
                        <button>Download</button>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default TrackList;