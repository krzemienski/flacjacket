'use client';

import { Track } from '@/types';
import { GetApp, MusicNote } from '@mui/icons-material';
import Button from './Button';

interface TrackItemProps {
  track: Track;
  onDownload: (trackId: number) => void;
  isDownloading?: boolean;
}

export default function TrackItem({ track, onDownload, isDownloading = false }: TrackItemProps) {
  // Format track duration in MM:SS
  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  // Calculate confidence percentage
  const confidencePercent = Math.round(track.confidence * 100);

  return (
    <div className="bg-white dark:bg-card-dark rounded-lg shadow-md overflow-hidden transition-all hover:shadow-lg border border-gray-100 dark:border-gray-800">
      <div className="p-4">
        <div className="flex justify-between items-start">
          <div className="flex items-start space-x-3">
            <div className="bg-primary-100 dark:bg-primary-900 rounded-full p-2 mt-1">
              <MusicNote className="text-primary-600 dark:text-primary-300" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900 dark:text-white">{track.title}</h3>
              <div className="mt-1 flex flex-wrap gap-2 text-sm text-gray-500 dark:text-gray-400">
                <span className="flex items-center">
                  Duration: {formatTime(track.end_time - track.start_time)}
                </span>
                <span className="flex items-center">
                  Start: {formatTime(track.start_time)}
                </span>
                <span className="flex items-center">
                  Confidence: {confidencePercent}%
                </span>
              </div>
            </div>
          </div>

          <Button
            variant="primary"
            size="sm"
            onClick={() => onDownload(track.id)}
            disabled={isDownloading || !track.file_path}
            loading={isDownloading}
            startIcon={<GetApp />}
          >
            Download
          </Button>
        </div>
      </div>

      {/* Progress bar representing confidence */}
      <div className="w-full bg-gray-200 dark:bg-gray-700 h-1">
        <div 
          className={`h-1 ${
            confidencePercent >= 80 
              ? 'bg-success-light dark:bg-success-dark' 
              : confidencePercent >= 50 
                ? 'bg-warning-light dark:bg-warning-dark' 
                : 'bg-error-light dark:bg-error-dark'
          }`} 
          style={{ width: `${confidencePercent}%` }}
        ></div>
      </div>
    </div>
  );
}
