import axiosInstance from "@/lib/axiosClient";

export type EmotionalAnalysis = {
  id: number;
  personal_entry_id: number;
  faces_detected: number;
  dominant_emotion: string | null;
  overall_confidence: number | null;
  image_quality: string | null;
  analysis_data: {
    faces_detected: number;
    dominant_emotion: string;
    overall_confidence: number;
    image_quality: string;
    analysis_timestamp: string;
    face_analyses: Array<{
      face_id: string;
      emotions: Array<{
        emotion: string;
        confidence: number;
        label: string;
      }>;
      bounding_box: {
        left: number;
        top: number;
        width: number;
        height: number;
      };
      quality: {
        brightness: number;
        sharpness: number;
      };
      pose: {
        roll: number;
        yaw: number;
        pitch: number;
      };
      age_range: {
        low: number;
        high: number;
      };
      gender: {
        value: string;
        confidence: number;
      };
    }>;
  } | null;
  recommendations: string[] | null;
  analyzed_at: string;
  created_at: string;
};

export type EmotionalAnalysisSummary = {
  status: string;
  summary: {
    total_entries: number;
    entries_with_analysis: number;
    filtered_results: number;
    average_confidence: number;
    emotion_distribution: Record<string, number>;
    most_common_emotion: string | null;
    most_common_emotion_count: number;
  };
  filters_applied: {
    emotion_filter: string | null;
    min_confidence: number | null;
  };
  emotional_analysis: Array<EmotionalAnalysis & {
    entry: {
      id: number;
      user_id: number;
      room_name: string;
      entered_at: string;
    };
  }>;
};

export type EmotionalAnalysisResponse = {
  status: string;
  entry_id: number;
  emotional_analysis: EmotionalAnalysis | null;
};

// Get emotional analysis for a specific entry
export const GetEmotionalAnalysis = async (entryId: number): Promise<EmotionalAnalysisResponse> => {
  const { data } = await axiosInstance<EmotionalAnalysisResponse>(`/entries/${entryId}/emotional-analysis`);
  return data;
};

// Get all emotional analysis summary
export const GetEmotionalAnalysisSummary = async (
  limit?: number,
  emotionFilter?: string,
  minConfidence?: number
): Promise<EmotionalAnalysisSummary> => {
  const params = new URLSearchParams();
  if (limit) params.append('limit', limit.toString());
  if (emotionFilter) params.append('emotion_filter', emotionFilter);
  if (minConfidence) params.append('min_confidence', minConfidence.toString());

  const queryString = params.toString();
  const url = `/entries/emotional-analysis-summary${queryString ? `?${queryString}` : ''}`;
  
  const { data } = await axiosInstance<EmotionalAnalysisSummary>(url);
  return data;
};
