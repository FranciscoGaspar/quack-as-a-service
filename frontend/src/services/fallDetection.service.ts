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

export type AIVideoReport = {
  report_type: string;
  executive_summary: string;
  detailed_analysis: string;
  key_findings: string[];
  recommendations: string[];
  risk_level: string;
  confidence_score: number;
  generated_at: string;
  model_used: string;
  video_context: any;
};

export type AIReportResponse = {
  status: string;
  ai_report: AIVideoReport;
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

export const GenerateAIReportFromDetection = async (
  detectionResult: FallDetectionResponse
): Promise<AIReportResponse> => {
  // Prepare video data for AI analysis
  const videoData = {
    video_filename: detectionResult.video_filename,
    user_id: detectionResult.user_id,
    location: detectionResult.location,
    fall_detected: detectionResult.detection_result.fall_detected,
    total_detections: detectionResult.detection_result.total_detections,
    confidence_scores: detectionResult.detection_result.confidence_scores,
    video_duration: detectionResult.detection_result.video_duration,
    processing_time: detectionResult.detection_result.processing_time,
    analysis_timestamp: detectionResult.detection_result.analysis_timestamp,
    model_version: detectionResult.detection_result.model_version,
    original_video_url: detectionResult.original_video_url,
    processed_video_url: detectionResult.processed_video_url
  };

  const { data } = await axiosInstance<AIReportResponse>("/fall-detection/generate-ai-report", {
    method: "POST",
    data: videoData,
    headers: {
      "Content-Type": "application/json",
    },
    timeout: 120000, // 2 minutes timeout for AI analysis
  });

  return data;
};
