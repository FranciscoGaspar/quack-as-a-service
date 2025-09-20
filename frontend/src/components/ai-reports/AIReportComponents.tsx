"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAICapabilities, useComprehensiveInsights, useExecutiveReport, useQuickInsights } from "@/hooks/ai-analytics/useAIAnalytics";
import {
  AlertTriangle,
  BarChart3,
  Brain,
  CheckCircle,
  FileText,
  Lightbulb,
  RefreshCw
} from "lucide-react";
import { useState } from "react";

// AI Insights Card Component
export const AIInsightsCard = () => {
  const { data: quickInsights, isLoading, error, refetch } = useQuickInsights();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await refetch();
    setIsRefreshing(false);
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-purple-600" />
            AI Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-red-600" />
            AI Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <AlertTriangle className="h-12 w-12 mx-auto mb-4 text-red-600" />
            <p className="text-red-600 mb-4">Failed to load AI insights</p>
            <Button onClick={handleRefresh} variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  const insights = quickInsights?.quick_insights || quickInsights?.fallback_data;

  if (!insights) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-gray-600" />
            AI Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-600">
            <Brain className="h-12 w-12 mx-auto mb-4" />
            <p>No AI insights available</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel?.toLowerCase()) {
      case 'high': return 'text-red-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  const getRiskBadgeVariant = (riskLevel: string) => {
    switch (riskLevel?.toLowerCase()) {
      case 'high': return 'destructive';
      case 'medium': return 'secondary';
      case 'low': return 'default';
      default: return 'outline';
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-purple-600" />
            AI Insights
          </div>
          <Button onClick={handleRefresh} variant="outline" size="sm" disabled={isRefreshing}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Summary */}
        <div>
          <h4 className="font-medium mb-2">Summary</h4>
          <p className="text-sm text-muted-foreground">{insights.summary}</p>
        </div>

        {/* Risk Level */}
        <div className="flex items-center justify-between">
          <span className="font-medium">Risk Level</span>
          <Badge variant={getRiskBadgeVariant(insights.risk_level)}>
            {insights.risk_level || 'Unknown'}
          </Badge>
        </div>

        {/* Confidence Score */}
        {insights.confidence && (
          <div className="flex items-center justify-between">
            <span className="font-medium">Confidence</span>
            <span className="text-sm text-muted-foreground">
              {(insights.confidence).toFixed(0)}%
            </span>
          </div>
        )}

        {/* Key Findings */}
        {insights.key_findings && insights.key_findings.length > 0 && (
          <div>
            <h4 className="font-medium mb-2">Key Findings</h4>
            <ul className="space-y-1">
              {insights.key_findings.slice(0, 3).map((finding, index) => (
                <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                  <span className="text-purple-600 mt-1">•</span>
                  {finding}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Top Recommendations */}
        {insights.top_recommendations && insights.top_recommendations.length > 0 && (
          <div>
            <h4 className="font-medium mb-2">Recommendations</h4>
            <ul className="space-y-1">
              {insights.top_recommendations.slice(0, 3).map((recommendation, index) => (
                <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                  <Lightbulb className="h-3 w-3 text-yellow-600 mt-1 flex-shrink-0" />
                  {recommendation}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Generated At */}
        {insights.generated_at && (
          <div className="text-xs text-muted-foreground pt-2 border-t">
            Generated: {new Date(insights.generated_at).toLocaleString()}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Comprehensive AI Analysis Component
export const ComprehensiveAIAnalysis = () => {
  const { data: comprehensiveInsights, isLoading, error } = useComprehensiveInsights(100);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-blue-600" />
            Comprehensive AI Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !comprehensiveInsights?.insight) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-gray-600" />
            Comprehensive AI Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-600">
            <BarChart3 className="h-12 w-12 mx-auto mb-4" />
            <p>Comprehensive analysis not available</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const insight = comprehensiveInsights.insight;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-blue-600" />
          {insight.title}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Summary */}
        <div>
          <h4 className="font-medium mb-2">Summary</h4>
          <p className="text-sm text-muted-foreground">{insight.summary}</p>
        </div>

        {/* Key Findings */}
        {insight.key_findings && insight.key_findings.length > 0 && (
          <div>
            <h4 className="font-medium mb-2">Key Findings</h4>
            <ul className="space-y-2">
              {insight.key_findings.map((finding, index) => (
                <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                  {finding}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Recommendations */}
        {insight.recommendations && insight.recommendations.length > 0 && (
          <div>
            <h4 className="font-medium mb-2">Recommendations</h4>
            <ul className="space-y-2">
              {insight.recommendations.map((recommendation, index) => (
                <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                  <Lightbulb className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                  {recommendation}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Risk Assessment */}
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <span className="font-medium">Risk Assessment</span>
          <Badge variant={insight.risk_level === 'high' ? 'destructive' : insight.risk_level === 'medium' ? 'secondary' : 'default'}>
            {insight.risk_level}
          </Badge>
        </div>

        {/* Confidence Score */}
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <span className="font-medium">Confidence Score</span>
          <span className="text-sm font-medium">{(insight.confidence_score).toFixed(0)}%</span>
        </div>
      </CardContent>
    </Card>
  );
};

// Executive Report Component
export const ExecutiveReportCard = () => {
  const { data: executiveReport, isLoading, error } = useExecutiveReport(200);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-green-600" />
            Executive Report
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !executiveReport?.report) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-gray-600" />
            Executive Report
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-600">
            <FileText className="h-12 w-12 mx-auto mb-4" />
            <p>Executive report not available</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const report = executiveReport.report;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-green-600" />
          Executive Report
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Executive Summary */}
        <div>
          <h4 className="font-medium mb-2">Executive Summary</h4>
          <p className="text-sm text-muted-foreground">{report.executive_summary}</p>
        </div>

        {/* Compliance Overview */}
        {report.compliance_overview && (
          <div>
            <h4 className="font-medium mb-2">Compliance Overview</h4>
            <div className="text-sm text-muted-foreground">
              {typeof report.compliance_overview === 'string' 
                ? report.compliance_overview 
                : JSON.stringify(report.compliance_overview, null, 2)
              }
            </div>
          </div>
        )}

        {/* Trend Analysis */}
        <div>
          <h4 className="font-medium mb-2">Trend Analysis</h4>
          <p className="text-sm text-muted-foreground">{report.trend_analysis}</p>
        </div>

        {/* Risk Assessment */}
        <div>
          <h4 className="font-medium mb-2">Risk Assessment</h4>
          <p className="text-sm text-muted-foreground">{report.risk_assessment}</p>
        </div>

        {/* Action Items */}
        {report.action_items && report.action_items.length > 0 && (
          <div>
            <h4 className="font-medium mb-2">Action Items</h4>
            <ul className="space-y-2">
              {report.action_items.map((item, index) => (
                <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                  <AlertTriangle className="h-4 w-4 text-orange-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <div className="font-medium">{item.title}</div>
                    <div>{item.description}</div>
                    {item.priority && (
                      <Badge variant="outline" className="mt-1">
                        {item.priority}
                      </Badge>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Generated At */}
        {report.generated_at && (
          <div className="text-xs text-muted-foreground pt-2 border-t">
            Generated: {new Date(report.generated_at).toLocaleString()}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// AI Status Indicator Component
export const AIStatusIndicator = () => {
  const { isAvailable, capabilities, model, isLoading } = useAICapabilities();

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
        Checking AI status...
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 text-sm">
      <div className={`flex items-center gap-2 ${isAvailable ? 'text-green-600' : 'text-red-600'}`}>
        <Brain className="h-4 w-4" />
        <span className="font-medium">
          AI Analytics {isAvailable ? 'Active' : 'Inactive'}
        </span>
      </div>
      
      {isAvailable && (
        <>
          <Badge variant="outline" className="text-xs">
            {model?.split('.')[1] || 'Claude'}
          </Badge>
          <span className="text-muted-foreground">
            {capabilities.length} capabilities
          </span>
        </>
      )}
    </div>
  );
};
