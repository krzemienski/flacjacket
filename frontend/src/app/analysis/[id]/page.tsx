'use client';

import { useEffect, useState } from 'react';
import { Analysis } from '@/types';

export default function AnalysisPage({ params }: { params: { id: string } }) {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [error, setError] = useState('');

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
    try {
      const response = await fetch(`/api/tracks/${trackId}/download`);
      if (!response.ok) {
        throw new Error('Failed to download track');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = response.headers.get('content-disposition')?.split('filename=')[1] || 'track.flac';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download track:', err);
    }
  };

  if (error) {
    return (
      <div className="text-red-600">
        {error}
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-4">Analysis Details</h2>
      
      <div className="mb-6">
        <p className="text-gray-600">URL: {analysis.url}</p>
        <div className="mt-2">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
            ${analysis.status === 'completed' ? 'bg-green-100 text-green-800' :
              analysis.status === 'failed' ? 'bg-red-100 text-red-800' :
              'bg-yellow-100 text-yellow-800'}`}>
            {analysis.status}
          </span>
        </div>
      </div>

      {analysis.error_message && (
        <div className="mb-4 p-4 bg-red-50 text-red-600 rounded">
          Error: {analysis.error_message}
        </div>
      )}

      <h3 className="text-xl font-semibold mb-4">Detected Tracks</h3>

      <div className="space-y-4">
        {analysis.tracks.map((track) => (
          <div
            key={track.id}
            className="border rounded-lg p-4 hover:bg-gray-50"
          >
            <div className="flex justify-between items-start">
              <div>
                <h4 className="font-medium">{track.title || 'Unknown Track'}</h4>
                {track.artist && (
                  <p className="text-gray-600">Artist: {track.artist}</p>
                )}
                <p className="text-gray-600">
                  Duration: {Math.round(track.duration)}s ({Math.round(track.start_time)}s - {Math.round(track.end_time)}s)
                </p>
                <p className="text-gray-600">
                  Confidence: {Math.round(track.confidence * 100)}%
                </p>
              </div>
              <button
                onClick={() => handleDownload(track.id)}
                disabled={analysis.status !== 'completed'}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Download
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
