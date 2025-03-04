'use client';

import { useEffect, useState } from 'react';
import { Analysis } from '@/types';
import Card from '@/components/Card';
import Button from '@/components/Button';
import TrackItem from '@/components/TrackItem';
import { ArrowBack, ErrorOutline, GetApp, MusicNote } from '@mui/icons-material';
import Link from 'next/link';

export default function AnalysisPage({ params }: { params: { id: string } }) {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [error, setError] = useState('');
  const [downloadingTrackId, setDownloadingTrackId] = useState<number | null>(null);

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        const response = await fetch(`/api/analysis/${params.id}`);
        if (!response.ok) {
          throw new Error('Failed to fetch analysis');
        }
        const data = await response.json();
        setAnalysis(data);
      } catch (err) {
        setError('Failed to fetch analysis details');
      }
    };

    const pollAnalysis = () => {
      if (analysis?.status === 'pending' || analysis?.status === 'processing') {
        const timer = setTimeout(fetchAnalysis, 5000);
        return () => clearTimeout(timer);
      }
    };

    fetchAnalysis();
    return pollAnalysis();
  }, [params.id, analysis?.status]);

  const handleDownload = async (trackId: number) => {
    setDownloadingTrackId(trackId);
    try {
      const response = await fetch(`/api/tracks/${trackId}/download`);
      if (!response.ok) {
        throw new Error('Failed to download track');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = response.headers.get('content-disposition')?.split('filename=')[1] || 'track.wav';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download track:', err);
    } finally {
      setDownloadingTrackId(null);
    }
  };

  const handleDownloadAll = async () => {
    if (!analysis || analysis.tracks.length === 0) return;
    
    // Sequential downloads to avoid overwhelming the browser
    for (const track of analysis.tracks) {
      await handleDownload(track.id);
    }
  };

  if (error) {
    return (
      <Card elevation={2} className="text-center py-8">
        <div className="flex flex-col items-center justify-center space-y-4">
          <ErrorOutline className="text-6xl text-error-light dark:text-error-dark" />
          <h3 className="text-xl font-medium text-gray-900 dark:text-white">{error}</h3>
          <Link href="/">
            <Button startIcon={<ArrowBack />} variant="primary">
              Back to Home
            </Button>
          </Link>
        </div>
      </Card>
    );
  }

  if (!analysis) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600 dark:border-primary-400"></div>
      </div>
    );
  }

  const isCompleted = analysis.status === 'completed';
  const isPending = analysis.status === 'pending' || analysis.status === 'processing';

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-success-light/10 text-success-light dark:bg-success-dark/20 dark:text-success-dark';
      case 'failed':
        return 'bg-error-light/10 text-error-light dark:bg-error-dark/20 dark:text-error-dark';
      case 'processing':
        return 'bg-primary-600/10 text-primary-600 dark:bg-primary-400/20 dark:text-primary-400';
      default:
        return 'bg-warning-light/10 text-warning-light dark:bg-warning-dark/20 dark:text-warning-dark';
    }
  };

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <Link href="/" className="text-primary-600 dark:text-primary-400 hover:underline flex items-center gap-1">
          <ArrowBack fontSize="small" />
          <span>Back to Home</span>
        </Link>
        
        {isCompleted && analysis.tracks.length > 0 && (
          <Button 
            variant="secondary" 
            startIcon={<GetApp />}
            onClick={handleDownloadAll}
          >
            Download All Tracks
          </Button>
        )}
      </div>
      
      <Card title="Analysis Details" elevation={2}>
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-1">Source URL</h3>
              <p className="text-gray-700 dark:text-gray-300 break-all">{analysis.url}</p>
            </div>
            
            <div className="flex flex-col sm:items-end gap-2">
              <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(analysis.status)}`}>
                {analysis.status}
              </span>
              
              {analysis.duration && (
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  Processed in {Math.round(analysis.duration)}s
                </span>
              )}
              
              <span className="text-sm text-gray-500 dark:text-gray-400">
                Started: {new Date(analysis.created_at).toLocaleString()}
              </span>
            </div>
          </div>
          
          {analysis.error_message && (
            <div className="p-4 bg-error-light/10 dark:bg-error-dark/10 text-error-light dark:text-error-dark rounded-lg border border-error-light/30 dark:border-error-dark/30">
              <div className="flex items-start gap-2">
                <ErrorOutline />
                <div>
                  <h4 className="font-medium">Error Occurred</h4>
                  <p>{analysis.error_message}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </Card>

      <Card 
        title={`Detected Tracks ${isPending ? '(Processing...)' : ''}`} 
        elevation={2}
      >
        {isPending && (
          <div className="flex justify-center items-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 dark:border-primary-400"></div>
          </div>
        )}
        
        {isCompleted && analysis.tracks.length === 0 && (
          <div className="py-8 text-center">
            <MusicNote className="mx-auto text-4xl text-gray-400 dark:text-gray-600 mb-2" />
            <p className="text-gray-500 dark:text-gray-400">No tracks were detected in this audio.</p>
          </div>
        )}
        
        <div className="space-y-4">
          {analysis.tracks.map((track) => (
            <TrackItem
              key={track.id}
              track={track}
              onDownload={handleDownload}
              isDownloading={downloadingTrackId === track.id}
            />
          ))}
        </div>
      </Card>
    </div>
  );
}
