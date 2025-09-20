import axiosInstance from "@/lib/axiosClient";

export type FallDetectionResult = {
  fall_detected: boolean;
  total_detections: number;
  confidence_scores: number[];
  video_duration: number;
  processing_time: number;
  analysis_timestamp: string;
  model_version: string;
};

export type FallDetectionResponse = {
  id?: number;
  user_id?: number;
  location?: string;
  detection_result: FallDetectionResult;
  original_video_url?: string;
  processed_video_url?: string;
  processing_timestamp: string;
  video_filename?: string;
  created_at?: string;
};

export type FallDetectionStatus = {
  status: string;
  service: string;
  model_file?: string;
  is_initialized: boolean;
  model_available: boolean;
  dependencies_available: boolean;
  supported_formats?: string[];
  max_file_size?: string;
  reason?: string;
};

export const GetFallDetectionStatus = async (): Promise<FallDetectionStatus> => {
  const { data } = await axiosInstance<FallDetectionStatus>("/fall-detection/status");
  return data;
};

export const AnalyzeVideoForFalls = async (
  video: File,
  userId?: number,
  location?: string
): Promise<FallDetectionResponse> => {
  const formData = new FormData();
  formData.append("video", video);
  
  if (userId) {
    formData.append("user_id", userId.toString());
  }
  
  if (location) {
    formData.append("location", location);
  }

  const { data } = await axiosInstance<FallDetectionResponse>("/fall-detection/analyze-video", {
    method: "POST",
    data: formData,
    headers: {
      "Content-Type": "multipart/form-data",
    },
    timeout: 300000, // 5 minutes timeout for video processing
  });

  return data;
};

export const InitializeFallDetectionModel = async () => {
  const { data } = await axiosInstance("/fall-detection/initialize", {
    method: "POST",
  });
  return data;
};

export const GetFallDetectionHealth = async () => {
  const { data } = await axiosInstance("/fall-detection/health");
  return data;
};
