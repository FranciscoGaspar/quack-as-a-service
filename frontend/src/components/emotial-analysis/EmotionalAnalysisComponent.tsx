"use client";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import {
  EmotionalAIAnalysisResponse,
  EmotionalAnalysisSummary,
  GetEmotionalAIAnalysis,
  GetEmotionalAnalysisSummary
} from "@/services/emotionalAnalysis.service";
import {
  AlertCircle,
  BarChart3,
  Brain,
  Calendar,
  Eye,
  Filter,
  MapPin,
  RefreshCw,
  TrendingUp,
  User,
  Users
} from "lucide-react";
import { useEffect, useState } from "react";
import { EmotionalAnalysisDialog } from "./EmotionalAnalysisDialog";

const EmotionBadge = ({ emotion, count }: { emotion: string; count: number }) => {
  const getEmotionColor = (emotion: string) => {
    switch (emotion.toLowerCase()) {
      case 'happy':
      case 'joy':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'sad':
      case 'sorrow':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'angry':
      case 'anger':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'fear':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'surprise':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'disgust':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'neutral':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <Badge className={`${getEmotionColor(emotion)} font-medium`}>
      {emotion} ({count})
    </Badge>
  );
};

const LoadingSkeleton = () => (
  <div className="space-y-6">
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {[1, 2, 3].map((i) => (
        <Card key={i}>
          <CardHeader className="pb-2">
            <Skeleton className="h-4 w-24" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-8 w-full mb-2" />
            <Skeleton className="h-4 w-16" />
          </CardContent>
        </Card>
      ))}
    </div>
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-32" />
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </div>
      </CardContent>
    </Card>
  </div>
);

export const EmotionalAnalysisComponent = () => {
  const [data, setData] = useState<EmotionalAnalysisSummary | null>(null);
  const [aiAnalysis, setAiAnalysis] = useState<EmotionalAIAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [aiLoading, setAiLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [aiError, setAiError] = useState<string | null>(null);
  const [filters, setFilters] = useState({
    limit: 100,
    emotionFilter: '',
    minConfidence: ''
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await GetEmotionalAnalysisSummary(
        filters.limit,
        filters.emotionFilter || undefined,
        filters.minConfidence ? parseFloat(filters.minConfidence) : undefined
      );
      
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch emotional analysis data');
    } finally {
      setLoading(false);
    }
  };

  const fetchAIAnalysis = async () => {
    try {
      setAiLoading(true);
      setAiError(null);
      
      const result = await GetEmotionalAIAnalysis(filters.limit);
      setAiAnalysis(result);
    } catch (err) {
      setAiError(err instanceof Error ? err.message : 'Failed to fetch AI emotional analysis');
    } finally {
      setAiLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    fetchAIAnalysis();
  }, []);

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleApplyFilters = () => {
    fetchData();
  };

  const handleResetFilters = () => {
    setFilters({
      limit: 100,
      emotionFilter: '',
      minConfidence: ''
    });
    // Fetch with default filters
    setTimeout(() => {
      setFilters({
        limit: 100,
        emotionFilter: '',
        minConfidence: ''
      });
      fetchData();
    }, 0);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return <LoadingSkeleton />;
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          {error}
        </AlertDescription>
      </Alert>
    );
  }

  if (!data || data.status === 'no_data') {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <Brain className="h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Emotional Analysis Data</h3>
          <p className="text-gray-500 text-center mb-4">
            No entries with emotional analysis found. Upload images with faces to see emotional analysis results.
          </p>
          <Button onClick={fetchData} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Filters */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-blue-600" />
              Emotional Analysis Overview
            </CardTitle>
            <Button onClick={fetchData} variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4 items-end">
            <div className="flex-1 min-w-[200px]">
              <label className="text-sm font-medium mb-2 block">Limit Results</label>
              <Select 
                value={filters.limit.toString()} 
                onValueChange={(value) => handleFilterChange('limit', value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="50">50 entries</SelectItem>
                  <SelectItem value="100">100 entries</SelectItem>
                  <SelectItem value="200">200 entries</SelectItem>
                  <SelectItem value="500">500 entries</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex-1 min-w-[200px]">
              <label className="text-sm font-medium mb-2 block">Filter by Emotion</label>
              <Select 
                value={filters.emotionFilter} 
                onValueChange={(value) => handleFilterChange('emotionFilter', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All emotions" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="HAPPY">Happy</SelectItem>
                  <SelectItem value="SAD">Sad</SelectItem>
                  <SelectItem value="ANGRY">Angry</SelectItem>
                  <SelectItem value="FEAR">Fear</SelectItem>
                  <SelectItem value="SURPRISE">Surprise</SelectItem>
                  <SelectItem value="DISGUST">Disgust</SelectItem>
                  <SelectItem value="NEUTRAL">Neutral</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex-1 min-w-[200px]">
              <label className="text-sm font-medium mb-2 block">Min Confidence (%)</label>
              <Input
                type="number"
                placeholder="e.g., 80"
                value={filters.minConfidence}
                onChange={(e) => handleFilterChange('minConfidence', e.target.value)}
                min="0"
                max="100"
              />
            </div>

            <div className="flex gap-2">
              <Button onClick={handleApplyFilters} size="sm">
                <Filter className="h-4 w-4 mr-2" />
                Apply Filters
              </Button>
              <Button onClick={handleResetFilters} variant="outline" size="sm">
                Reset
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Total Entries</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.summary.total_entries}</div>
            <p className="text-xs text-gray-500">
              {data.summary.entries_with_analysis} with analysis
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Average Confidence</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.summary.average_confidence}%</div>
            <p className="text-xs text-gray-500">
              {data.summary.filtered_results} filtered results
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Most Common Emotion</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {data.summary.most_common_emotion || 'N/A'}
            </div>
            <p className="text-xs text-gray-500">
              {data.summary.most_common_emotion_count} occurrences
            </p>
          </CardContent>
        </Card>
      </div>


      {/* AI Emotional Analysis */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-purple-600" />
              AI Emotional Analysis
            </CardTitle>
            <Button 
              onClick={fetchAIAnalysis} 
              variant="outline" 
              size="sm"
              disabled={aiLoading}
            >
              {aiLoading ? (
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4 mr-2" />
              )}
              Refresh AI Analysis
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {aiError && (
            <Alert variant="destructive" className="mb-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                {aiError}
              </AlertDescription>
            </Alert>
          )}
          
          {aiLoading ? (
            <div className="space-y-4">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
              <div className="space-y-2">
                <Skeleton className="h-3 w-full" />
                <Skeleton className="h-3 w-full" />
                <Skeleton className="h-3 w-2/3" />
              </div>
            </div>
          ) : aiAnalysis ? (
            <div className="space-y-6">
              {/* Summary */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Executive Summary</h4>
                <p className="text-gray-700 leading-relaxed">{aiAnalysis.emotional_analysis.summary}</p>
              </div>

              {/* Risk Level */}
              <div className="flex items-center gap-3">
                <h4 className="font-semibold text-gray-900">Risk Level:</h4>
                <Badge 
                  variant={aiAnalysis.emotional_analysis.risk_level.toLowerCase() === 'high' ? 'destructive' : 
                          aiAnalysis.emotional_analysis.risk_level.toLowerCase() === 'medium' ? 'default' : 'secondary'}
                  className="font-medium"
                >
                  {aiAnalysis.emotional_analysis.risk_level}
                </Badge>
                <span className="text-sm text-gray-600">
                  Confidence: {aiAnalysis.emotional_analysis.confidence_score}%
                </span>
              </div>

              {/* Key Findings */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Key Findings</h4>
                <ul className="space-y-2">
                  {aiAnalysis.emotional_analysis.key_findings.map((finding, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0" />
                      <span className="text-gray-700">{finding}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Recommendations */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Actionable Recommendations</h4>
                <ul className="space-y-2">
                  {aiAnalysis.emotional_analysis.recommendations.map((recommendation, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <div className="w-2 h-2 bg-green-600 rounded-full mt-2 flex-shrink-0" />
                      <span className="text-gray-700">{recommendation}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Analysis Metadata */}
              <div className="pt-4 border-t border-gray-200">
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <span>Generated: {new Date(aiAnalysis.emotional_analysis.generated_at).toLocaleString()}</span>
                  <span>Data Period: {aiAnalysis.emotional_analysis.data_period}</span>
                  <span>Entries Analyzed: {aiAnalysis.data_summary.entries_analyzed}</span>
                </div>
                {aiAnalysis.cache_info && (
                  <div className="mt-2 flex items-center justify-center">
                    <Badge 
                      variant={aiAnalysis.cache_info.cached ? "secondary" : "outline"}
                      className="text-xs"
                    >
                      {aiAnalysis.cache_info.cached ? "📦 Cached" : "🔄 Fresh Analysis"}
                    </Badge>
                    <span className="ml-2 text-xs text-gray-500">
                      Cache expires in {Math.round(aiAnalysis.cache_info.cache_duration_seconds / 60)} minutes
                    </span>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">AI Analysis Loading...</h3>
              <p className="text-gray-500 mb-4">
                AI analysis is being generated automatically. Please wait...
              </p>
              <Button onClick={fetchAIAnalysis} variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Retry AI Analysis
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Emotion Distribution */}
      {Object.keys(data.summary.emotion_distribution).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-blue-600" />
              Emotion Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {Object.entries(data.summary.emotion_distribution).map(([emotion, count]) => (
                <EmotionBadge key={emotion} emotion={emotion} count={count} />
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Analysis Results */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Eye className="h-5 w-5 text-blue-600" />
            Analysis Results ({data.summary.filtered_results})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {data.emotional_analysis.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No results match the current filters.
            </div>
          ) : (
            <div className="space-y-4">
              {data.emotional_analysis.map((item) => (
                <div key={item.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-4 mb-2">
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <User className="h-4 w-4" />
                          <span>User {item.entry.user_id}</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <MapPin className="h-4 w-4" />
                          <span>{item.entry.room_name}</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <Calendar className="h-4 w-4" />
                          <span>{formatDate(item.entry.entered_at)}</span>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                          <Users className="h-4 w-4 text-gray-500" />
                          <span className="text-sm">{item.faces_detected} face(s)</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Brain className="h-4 w-4 text-gray-500" />
                          <span className="text-sm font-medium">
                            {item.dominant_emotion || 'N/A'}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <TrendingUp className="h-4 w-4 text-gray-500" />
                          <span className="text-sm">
                            {item.overall_confidence?.toFixed(1) || 'N/A'}% confidence
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <EmotionalAnalysisDialog 
                      analysis={item} 
                      entryInfo={item.entry}
                    >
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4 mr-2" />
                        View Details
                      </Button>
                    </EmotionalAnalysisDialog>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
