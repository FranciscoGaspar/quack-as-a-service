// AI Analytics Hooks
// Custom hooks for AI-powered analytics endpoints

import { aiAnalyticsService, type AnomalyData } from '@/services/aiAnalytics.service';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

// Query keys for AI analytics
export const aiQueryKeys = {
  status: ['ai', 'status'] as const,
  quickInsights: (limit: number) => ['ai', 'quick-insights', limit] as const,
  comprehensiveInsights: (limit: number) => ['ai', 'comprehensive-insights', limit] as const,
  executiveInsights: (limit: number) => ['ai', 'executive-insights', limit] as const,
  anomalyInsights: (limit: number) => ['ai', 'anomaly-insights', limit] as const,
  trendInsights: (limit: number) => ['ai', 'trend-insights', limit] as const,
  executiveReport: (limit: number) => ['ai', 'executive-report', limit] as const,
};

// Hook to check AI service status
export const useAIStatus = () => {
  return useQuery({
    queryKey: aiQueryKeys.status,
    queryFn: () => aiAnalyticsService.getAIStatus(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });
};

// Hook for quick insights (dashboard)
export const useQuickInsights = (limit: number = 50) => {
  return useQuery({
    queryKey: aiQueryKeys.quickInsights(limit),
    queryFn: () => aiAnalyticsService.getQuickInsights(limit),
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 2,
    enabled: true, // Always enabled for dashboard
  });
};

// Hook for comprehensive insights
export const useComprehensiveInsights = (limit: number = 100, enabled: boolean = true) => {
  return useQuery({
    queryKey: aiQueryKeys.comprehensiveInsights(limit),
    queryFn: () => aiAnalyticsService.getComprehensiveInsights(limit),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
    enabled,
  });
};

// Hook for executive insights
export const useExecutiveInsights = (limit: number = 200, enabled: boolean = true) => {
  return useQuery({
    queryKey: aiQueryKeys.executiveInsights(limit),
    queryFn: () => aiAnalyticsService.getExecutiveInsights(limit),
    staleTime: 10 * 60 * 1000, // 10 minutes
    retry: 2,
    enabled,
  });
};

// Hook for anomaly insights
export const useAnomalyInsights = (limit: number = 100, enabled: boolean = true) => {
  return useQuery({
    queryKey: aiQueryKeys.anomalyInsights(limit),
    queryFn: () => aiAnalyticsService.getAnomalyInsights(limit),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
    enabled,
  });
};

// Hook for trend insights
export const useTrendInsights = (limit: number = 150, enabled: boolean = true) => {
  return useQuery({
    queryKey: aiQueryKeys.trendInsights(limit),
    queryFn: () => aiAnalyticsService.getTrendInsights(limit),
    staleTime: 10 * 60 * 1000, // 10 minutes
    retry: 2,
    enabled,
  });
};

// Hook for executive report
export const useExecutiveReport = (limit: number = 200, enabled: boolean = true) => {
  return useQuery({
    queryKey: aiQueryKeys.executiveReport(limit),
    queryFn: () => aiAnalyticsService.getExecutiveReport(limit),
    staleTime: 15 * 60 * 1000, // 15 minutes
    retry: 2,
    enabled,
  });
};

// Hook for anomaly analysis (mutation)
export const useAnomalyAnalysis = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ anomalies, limit }: { anomalies: AnomalyData[]; limit?: number }) => 
      aiAnalyticsService.analyzeAnomalies(anomalies, limit || 100),
    onSuccess: () => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['ai'] });
    },
  });
};

// Hook to refresh all AI data
export const useRefreshAIData = () => {
  const queryClient = useQueryClient();
  
  return () => {
    queryClient.invalidateQueries({ queryKey: ['ai'] });
  };
};

// Hook to get AI capabilities status
export const useAICapabilities = () => {
  const { data: status, isLoading, error } = useAIStatus();
  
  return {
    isAvailable: status?.is_initialized || false,
    capabilities: status?.capabilities || [],
    model: status?.model,
    region: status?.region,
    isLoading,
    error,
  };
};
