'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import AnalysisList from '@/components/AnalysisList';
import Card from '@/components/Card';
import Input from '@/components/Input';
import Button from '@/components/Button';
import { Search, Link as LinkIcon } from '@mui/icons-material';

export default function Home() {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('/api/analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error('Failed to start analysis');
      }

      const data = await response.json();
      router.push(`/analysis/${data.id}`);
    } catch (err) {
      setError('Failed to start analysis. Please check the URL and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 fade-in">
      <Card title="Analyze Audio" elevation={2} className="transition-all hover:elevation-3">
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="SoundCloud or YouTube URL"
            id="url"
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Enter a SoundCloud or YouTube URL"
            fullWidth
            required
            disabled={loading}
            startAdornment={<LinkIcon className="text-gray-400" />}
            error={!!error}
            helperText={error || "Enter the URL of a SoundCloud or YouTube audio file to analyze"}
          />
          
          <Button 
            type="submit"
            fullWidth
            disabled={loading}
            loading={loading}
            startIcon={<Search />}
          >
            {loading ? 'Processing...' : 'Start Analysis'}
          </Button>
        </form>
      </Card>

      <AnalysisList />
    </div>
  );
}
