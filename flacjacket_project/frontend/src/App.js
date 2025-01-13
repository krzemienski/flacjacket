import React, { useState } from 'react';
import TrackList from './components/TrackList';
import AdminDashboard from './components/AdminDashboard';

function App() {
    const [view, setView] = useState('user');
    const [tracks, setTracks] = useState([]);
    const [url, setUrl] = useState('');

    const analyze = async () => {
        const response = await axios.post('/api/analyze', { url });
        const analysisId = response.data.analysis_id;
        const trackResponse = await axios.get(`/api/history/${analysisId}`);
        setTracks(trackResponse.data.tracks);
    };

    return (
        <div>
            <h1>Flacjacket</h1>
            <button onClick={() => setView('user')}>User View</button>
            <button onClick={() => setView('admin')}>Admin View</button>
            {view === 'user' ? (
                <div>
                    <input type="text" placeholder="Enter URL" value={url} onChange={e => setUrl(e.target.value)} />
                    <button onClick={analyze}>Analyze</button>
                    <TrackList tracks={tracks} />
                </div>
            ) : (
                <AdminDashboard />
            )}
        </div>
    );
}

export default App;