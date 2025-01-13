import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  Alert,
} from '@mui/material';
import axios from 'axios';

function Home() {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await axios.post('/api/analyze', { url });
      navigate(`/analysis/${response.data.id}`);
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to start analysis');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', mt: 4 }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Audio Track Analyzer
        </Typography>
        <Typography variant="body1" sx={{ mb: 4 }}>
          Enter a SoundCloud or YouTube URL to analyze and extract individual tracks
          from long audio files.
        </Typography>

        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="SoundCloud or YouTube URL"
            variant="outlined"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            sx={{ mb: 2 }}
            required
          />

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
            disabled={loading}
            sx={{ mt: 2 }}
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </Button>
        </form>

        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            Supported Platforms:
          </Typography>
          <Typography variant="body2" paragraph>
            • SoundCloud: Long mixes, DJ sets, and live recordings
          </Typography>
          <Typography variant="body2" paragraph>
            • YouTube: Music videos, concert recordings, and live streams
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
}

export default Home;
