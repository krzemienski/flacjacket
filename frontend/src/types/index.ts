export interface Track {
  id: number;
  title: string;
  artist: string;
  start_time: number;
  end_time: number;
  confidence: number;
  duration: number;
  created_at: string;
}

export interface Analysis {
  id: number;
  url: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  completed_at: string | null;
  error_message: string | null;
  tracks: Track[];
}
