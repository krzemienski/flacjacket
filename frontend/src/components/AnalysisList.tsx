'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Analysis } from '@/types';
import Card from './Card';
import { CheckCircle, ErrorOutline, Pending, PlayArrow } from '@mui/icons-material';

export default function AnalysisList() {
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalyses = async () => {
      try {
        const response = await fetch('/api/analyses');
        if (!response.ok) {
          throw new Error('Failed to fetch analyses');
        }
        const data = await response.json();
        setAnalyses(data.analyses);
      } catch (error) {
        console.error('Failed to fetch analyses:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalyses();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 dark:border-primary-400"></div>
      </div>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="text-success-light dark:text-success-dark" />;
      case 'failed':
        return <ErrorOutline className="text-error-light dark:text-error-dark" />;
      case 'processing':
        return <PlayArrow className="text-primary-600 dark:text-primary-400" />;
      default:
        return <Pending className="text-warning-light dark:text-warning-dark" />;
    }
  };

  const getStatusClass = (status: string) => {
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
    <Card title="Recent Analyses" elevation={2}>
      {analyses.length === 0 ? (
        <div className="py-4 text-center text-gray-500 dark:text-gray-400">
          No analyses found. Start by analyzing an audio URL.
        </div>
      ) : (
        <div className="space-y-4">
          {analyses.map((analysis) => (
            <Link
              key={analysis.id}
              href={`/analysis/${analysis.id}`}
              className="block transition-all"
            >
              <div className="border dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                <div className="flex justify-between items-start">
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 dark:text-white truncate">{analysis.url}</p>
                    <div className="mt-2 flex flex-wrap items-center gap-2">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusClass(analysis.status)}`}>
                        {getStatusIcon(analysis.status)}
                        <span>{analysis.status}</span>
                      </span>
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        {new Date(analysis.created_at).toLocaleString()}
                      </span>
                    </div>
                  </div>
                  <div className="ml-4">
                    <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900">
                      <PlayArrow className="text-primary-600 dark:text-primary-400" />
                    </span>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </Card>
  );
}
