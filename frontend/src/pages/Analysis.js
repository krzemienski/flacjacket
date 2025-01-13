import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  Button,
  CircularProgress,
  Alert,
  Divider,
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import axios from 'axios';

function Analysis() {
  const { id } = useParams();
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        const response = await axios.get(`/api/analysis/${id}`);
        setAnalysis(response.data);
      } catch (error) {
        setError(error.response?.data?.error || 'Failed to fetch analysis');
      } finally {
        setLoading(false);
      }
    };

    const pollAnalysis = setInterval(() => {
      if (analysis?.status === 'completed' || analysis?.status === 'failed') {
        clearInterval(pollAnalysis);
      } else {
        fetchAnalysis();
      }
    }, 5000);

    fetchAnalysis();

    return () => clearInterval(pollAnalysis);
  }, [id, analysis?.status]);

  const handleDownload = async (trackId) => {
    try {
      const response = await axios.get(`/api/tracks/${trackId}/download`, {
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `track_${trackId}.flac`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      setError('Failed to download track');
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 4 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', mt: 4 }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom>
          Analysis Results
        </Typography>

        <Box sx={{ mb: 4 }}>
          <Typography variant="subtitle1" color="text.secondary">
            Source: {analysis.source_url}
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Status: {analysis.status}
          </Typography>
        </Box>

        {analysis.status === 'processing' && (
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 4 }}>
            <CircularProgress size={24} sx={{ mr: 2 }} />
            <Typography>Processing audio file...</Typography>
          </Box>
        )}

        {analysis.status === 'completed' && analysis.tracks.length > 0 && (
          <>
            <Typography variant="h6" gutterBottom>
              Identified Tracks
            </Typography>
            <List>
              {analysis.tracks.map((track, index) => (
                <React.Fragment key={track.id}>
                  {index > 0 && <Divider />}
                  <ListItem
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <ListItemText
                      primary={`${track.artist} - ${track.title}`}
                      secondary={`Confidence: ${Math.round(
                        track.confidence * 100
                      )}% | Time: ${formatTime(track.start_time)} - ${formatTime(
                        track.end_time
                      )}`}
                    />
                    <Button
                      variant="contained"
                      startIcon={<DownloadIcon />}
                      onClick={() => handleDownload(track.id)}
                      sx={{ ml: 2 }}
                    >
                      Download
                    </Button>
                  </ListItem>
                </React.Fragment>
              ))}
            </List>
          </>
        )}

        {analysis.status === 'completed' && analysis.tracks.length === 0 && (
          <Alert severity="info">
            No tracks were identified in this audio file.
          </Alert>
        )}

        {analysis.status === 'failed' && (
          <Alert severity="error">
            Analysis failed: {analysis.error_message}
          </Alert>
        )}
      </Paper>
    </Box>
  );
}

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

export default Analysis;
