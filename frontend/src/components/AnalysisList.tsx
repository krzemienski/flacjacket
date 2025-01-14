'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Analysis } from '@/types';

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
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-4">Recent Analyses</h2>
      <div className="space-y-4">
        {analyses.map((analysis) => (
          <Link
            key={analysis.id}
            href={`/analysis/${analysis.id}`}
            className="block border rounded-lg p-4 hover:bg-gray-50"
          >
            <div className="flex justify-between items-start">
              <div>
                <p className="font-medium truncate">{analysis.url}</p>
                <div className="mt-2 flex items-center space-x-2">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                    ${analysis.status === 'completed' ? 'bg-green-100 text-green-800' :
                      analysis.status === 'failed' ? 'bg-red-100 text-red-800' :
                      'bg-yellow-100 text-yellow-800'}`}>
                    {analysis.status}
                  </span>
                  <span className="text-sm text-gray-500">
                    {new Date(analysis.created_at).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
