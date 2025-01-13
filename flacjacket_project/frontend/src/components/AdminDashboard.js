import React, { useEffect, useState } from 'react';
import axios from 'axios';

function AdminDashboard() {
    const [history, setHistory] = useState([]);

    useEffect(() => {
        const fetchHistory = async () => {
            const response = await axios.get('/api/history');
            setHistory(response.data);
        };

        fetchHistory();
    }, []);

    return (
        <div>
            <h2>Processing History</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>URL</th>
                        <th>Status</th>
                        <th>Tracks</th>
                    </tr>
                </thead>
                <tbody>
                    {history.map(job => (
                        <tr key={job.id}>
                            <td>{job.id}</td>
                            <td>{job.url}</td>
                            <td>{job.status}</td>
                            <td>
                                <ul>
                                    {job.tracks.map((track, index) => (
                                        <li key={index}>{track.track_name} by {track.artist}</li>
                                    ))}
                                </ul>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default AdminDashboard;