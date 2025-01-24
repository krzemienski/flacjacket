export interface Track {
  id: number;
  analysis_id: number;
  title: string;
  start_time: number;
  end_time: number;
  confidence: number;
  track_type: 'full_track' | 'onset_based' | 'final_segment';
  file_path: string | null;
  created_at: string;
}

export interface Analysis {
  id: number;
  url: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  duration: number | null;
  error_message: string | null;
  tracks: Track[];
}
