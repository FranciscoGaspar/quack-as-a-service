// AI Analytics Service for frontend
// This service handles all AI-powered analytics endpoints

export interface AIInsight {
  type: string;
  title: string;
  summary: string;
  detailed_analysis: string;
  key_findings: string[];
  recommendations: string[];
  risk_level: string;
  confidence_score: number;
  generated_at: string;
  data_period: string;
}

export interface ExecutiveReport {
  executive_summary: string;
  compliance_overview: Record<string, any>;
  trend_analysis: string;
  risk_assessment: string;
  action_items: Array<{ title: string; description: string; priority: string }>;
  generated_at: string;
}

export interface QuickInsights {
  summary: string;
  risk_level: string;
  confidence: number;
  top_recommendations: string[];
  key_findings: string[];
  generated_at: string;
}

export interface AIStatus {
  status: string;
  service: string;
  model?: string;
  region?: string;
  is_initialized: boolean;
  capabilities: string[];
  error?: string;
}

export interface AnomalyData {
  type: string;
  description: string;
  severity: string;
  timestamp: string;
  affected_users?: number[];
  room?: string;
}

export interface CustomAnalysisResponse {
  status: string;
  analysis?: AIInsight;
  user_prompt: string;
  data_summary?: {
    entries_analyzed: number;
    analysis_type: string;
    ai_service: string;
  };
}

export interface QuickAnswerResponse {
  status: string;
  question: string;
  answer: string;
  data_summary?: {
    entries_analyzed: number;
    analysis_type: string;
  };
}

class AIAnalyticsService {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`AI Analytics API Error (${endpoint}):`, error);
      throw error;
    }
  }

  // Check AI service status
  async getAIStatus(): Promise<AIStatus> {
    return this.request<AIStatus>('/entries/ai/status');
  }

  // Get quick insights for dashboard
  async getQuickInsights(limit: number = 50): Promise<{
    status: string;
    quick_insights?: QuickInsights;
    fallback_data?: QuickInsights;
    data_summary?: {
      entries_analyzed: number;
      analysis_type: string;
    };
  }> {
    return this.request(`/entries/ai/quick-insights?limit=${limit}`);
  }

  // Get comprehensive insights
  async getComprehensiveInsights(limit: number = 100): Promise<{
    status: string;
    insight?: AIInsight;
    data_summary?: {
      entries_analyzed: number;
      analysis_type: string;
      ai_service: string;
    };
  }> {
    return this.request(`/entries/ai/insights?insight_type=comprehensive&limit=${limit}`);
  }

  // Get executive insights
  async getExecutiveInsights(limit: number = 200): Promise<{
    status: string;
    insight?: AIInsight;
    data_summary?: {
      entries_analyzed: number;
      analysis_type: string;
      ai_service: string;
    };
  }> {
    return this.request(`/entries/ai/insights?insight_type=executive&limit=${limit}`);
  }

  // Get anomaly insights
  async getAnomalyInsights(limit: number = 100): Promise<{
    status: string;
    insight?: AIInsight;
    data_summary?: {
      entries_analyzed: number;
      analysis_type: string;
      ai_service: string;
    };
  }> {
    return this.request(`/entries/ai/insights?insight_type=anomaly&limit=${limit}`);
  }

  // Get trend insights
  async getTrendInsights(limit: number = 150): Promise<{
    status: string;
    insight?: AIInsight;
    data_summary?: {
      entries_analyzed: number;
      analysis_type: string;
      ai_service: string;
    };
  }> {
    return this.request(`/entries/ai/insights?insight_type=trend&limit=${limit}`);
  }

  // Generate executive report
  async getExecutiveReport(limit: number = 200): Promise<{
    status: string;
    report?: ExecutiveReport;
    metadata?: {
      entries_analyzed: number;
      report_type: string;
      ai_service: string;
    };
  }> {
    return this.request(`/entries/ai/executive-report?limit=${limit}`);
  }

  // Analyze anomalies
  async analyzeAnomalies(anomalies: AnomalyData[], limit: number = 100): Promise<{
    status: string;
    analysis?: AIInsight;
    anomaly_summary?: {
      total_anomalies: number;
      entries_analyzed: number;
      analysis_type: string;
      ai_service: string;
    };
  }> {
    return this.request('/entries/ai/anomaly-analysis', {
      method: 'POST',
      body: JSON.stringify(anomalies),
    });
  }

  // Custom Analysis - New NLP Feature
  async generateCustomAnalysis(userPrompt: string, limit: number = 100): Promise<CustomAnalysisResponse> {
    const formData = new FormData();
    formData.append('user_prompt', userPrompt);
    formData.append('limit', limit.toString());

    const response = await fetch(`${this.baseUrl}/entries/ai/custom-analysis`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  }

  // Quick Answer - New NLP Feature
  async getQuickAnswer(question: string, limit: number = 50): Promise<QuickAnswerResponse> {
    const formData = new FormData();
    formData.append('question', question);
    formData.append('limit', limit.toString());

    const response = await fetch(`${this.baseUrl}/entries/ai/quick-answer`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  }
}

export const aiAnalyticsService = new AIAnalyticsService();
