"use client";

import { useState } from "react";
import { 
  FileText, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Brain,
  Download,
  Copy,
  Star,
  BarChart3,
  Shield,
  TrendingUp,
  X
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import type { AIVideoReport } from "@/services/fallDetection.service";

interface AIReportDialogProps {
  report: AIVideoReport | null;
  isOpen: boolean;
  onClose: () => void;
}

export const AIReportDialog = ({ report, isOpen, onClose }: AIReportDialogProps) => {
  const [isExporting, setIsExporting] = useState(false);
  const { toast } = useToast();

  if (!report) return null;

  const getRiskLevelConfig = (riskLevel: string) => {
    switch (riskLevel.toLowerCase()) {
      case 'high':
        return {
          color: 'destructive' as const,
          icon: AlertTriangle,
          bgColor: 'bg-red-50 border-red-200',
          textColor: 'text-red-700'
        };
      case 'medium':
        return {
          color: 'secondary' as const,
          icon: Clock,
          bgColor: 'bg-yellow-50 border-yellow-200',
          textColor: 'text-yellow-700'
        };
      case 'low':
        return {
          color: 'default' as const,
          icon: CheckCircle,
          bgColor: 'bg-green-50 border-green-200',
          textColor: 'text-green-700'
        };
      default:
        return {
          color: 'secondary' as const,
          icon: Clock,
          bgColor: 'bg-gray-50 border-gray-200',
          textColor: 'text-gray-700'
        };
    }
  };

  const riskConfig = getRiskLevelConfig(report.risk_level);
  const RiskIcon = riskConfig.icon;

  const handleCopyReport = async () => {
    try {
      const reportText = `
AI VIDEO ANALYSIS REPORT
========================

Video: ${report.video_context.video_filename || 'Unknown'}
Generated: ${new Date(report.generated_at).toLocaleString()}
Model: ${report.model_used}

EXECUTIVE SUMMARY
${report.executive_summary}

KEY FINDINGS
${report.key_findings.map(finding => `• ${finding}`).join('\n')}

RECOMMENDATIONS
${report.recommendations.map(rec => `• ${rec}`).join('\n')}

RISK LEVEL: ${report.risk_level.toUpperCase()}
CONFIDENCE: ${report.confidence_score}%

TECHNICAL DETAILS
• Video Duration: ${report.video_context.video_duration || 0}s
• Fall Detected: ${report.video_context.fall_detected ? 'Yes' : 'No'}
• Total Detections: ${report.video_context.total_detections || 0}
• Processing Time: ${report.video_context.processing_time || 0}s
      `.trim();

      await navigator.clipboard.writeText(reportText);
      toast({
        title: "Report copied",
        description: "The AI report has been copied to your clipboard",
      });
    } catch (error) {
      toast({
        title: "Copy failed",
        description: "Failed to copy report to clipboard",
        variant: "destructive",
      });
    }
  };

  const handleExportReport = async () => {
    setIsExporting(true);
    try {
      const reportContent = `
<!DOCTYPE html>
<html>
<head>
    <title>AI Video Analysis Report - ${report.video_context.video_filename || 'Unknown'}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        .header { border-bottom: 3px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
        .section { margin: 30px 0; }
        .risk-high { color: #dc2626; font-weight: bold; }
        .risk-medium { color: #d97706; font-weight: bold; }
        .risk-low { color: #059669; font-weight: bold; }
        .metadata { background: #f9fafb; padding: 20px; border-radius: 8px; }
        ul { list-style-type: disc; margin-left: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>AI Video Analysis Report</h1>
        <p><strong>Video:</strong> ${report.video_context.video_filename || 'Unknown'}</p>
        <p><strong>Generated:</strong> ${new Date(report.generated_at).toLocaleString()}</p>
        <p><strong>Model:</strong> ${report.model_used}</p>
    </div>

    <div class="section">
        <h2>Executive Summary</h2>
        <p>${report.executive_summary}</p>
    </div>

    <div class="section">
        <h2>Risk Assessment</h2>
        <p class="risk-${report.risk_level.toLowerCase()}">Risk Level: ${report.risk_level.toUpperCase()}</p>
        <p>Confidence Score: ${report.confidence_score}%</p>
    </div>

    <div class="section">
        <h2>Key Findings</h2>
        <ul>
            ${report.key_findings.map(finding => `<li>${finding}</li>`).join('')}
        </ul>
    </div>

    <div class="section">
        <h2>Recommendations</h2>
        <ul>
            ${report.recommendations.map(rec => `<li>${rec}</li>`).join('')}
        </ul>
    </div>

    <div class="section">
        <h2>Detailed Analysis</h2>
        <p>${report.detailed_analysis.replace(/\n/g, '<br>')}</p>
    </div>

    <div class="metadata">
        <h3>Technical Details</h3>
        <p><strong>Video Duration:</strong> ${report.video_context.video_duration || 0}s</p>
        <p><strong>Fall Detected:</strong> ${report.video_context.fall_detected ? 'Yes' : 'No'}</p>
        <p><strong>Total Detections:</strong> ${report.video_context.total_detections || 0}</p>
        <p><strong>Processing Time:</strong> ${report.video_context.processing_time || 0}s</p>
        ${report.video_context.location ? `<p><strong>Location:</strong> ${report.video_context.location}</p>` : ''}
    </div>
</body>
</html>
      `;

      const blob = new Blob([reportContent], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `ai-report-${report.video_context.video_filename || 'unknown'}-${new Date().toISOString().split('T')[0]}.html`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      toast({
        title: "Report exported",
        description: "The AI report has been saved as an HTML file",
      });
    } catch (error) {
      toast({
        title: "Export failed",
        description: "Failed to export the report",
        variant: "destructive",
      });
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh]">
        <DialogHeader className="pb-4">
          <div className="flex items-center justify-between">
            <DialogTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-blue-600" />
              AI Video Analysis Report
            </DialogTitle>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleCopyReport}
              >
                <Copy className="mr-2 h-4 w-4" />
                Copy
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleExportReport}
                disabled={isExporting}
              >
                <Download className="mr-2 h-4 w-4" />
                Export
              </Button>
            </div>
          </div>
        </DialogHeader>
        
        <div className="max-h-[calc(90vh-120px)] overflow-y-auto pr-2">
          <div className="space-y-6">
            {/* Report Metadata */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center p-3 rounded-lg border">
                <Badge variant={riskConfig.color} className="mb-2">
                  <RiskIcon className="mr-1 h-3 w-3" />
                  {report.risk_level.toUpperCase()}
                </Badge>
                <p className="text-xs text-muted-foreground">Risk Level</p>
              </div>
              
              <div className="text-center p-3 rounded-lg border">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Star className="h-4 w-4 text-yellow-500" />
                  <span className="text-lg font-bold">{report.confidence_score}%</span>
                </div>
                <p className="text-xs text-muted-foreground">Confidence</p>
              </div>
              
              <div className="text-center p-3 rounded-lg border">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <BarChart3 className="h-4 w-4 text-blue-500" />
                  <span className="text-lg font-bold">{report.video_context.total_detections || 0}</span>
                </div>
                <p className="text-xs text-muted-foreground">Detections</p>
              </div>
              
              <div className="text-center p-3 rounded-lg border">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Clock className="h-4 w-4 text-green-500" />
                  <span className="text-lg font-bold">{(report.video_context.video_duration || 0).toFixed(1)}s</span>
                </div>
                <p className="text-xs text-muted-foreground">Duration</p>
              </div>
            </div>

            {/* Executive Summary */}
            <div className={`p-4 rounded-lg border ${riskConfig.bgColor}`}>
              <h3 className={`font-semibold mb-2 flex items-center gap-2 ${riskConfig.textColor}`}>
                <FileText className="h-4 w-4" />
                Executive Summary
              </h3>
              <p className={`text-sm ${riskConfig.textColor}`}>
                {report.executive_summary}
              </p>
            </div>

            {/* Key Findings */}
            <div className="space-y-3">
              <h3 className="font-semibold flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                Key Findings
              </h3>
              <ul className="space-y-2">
                {report.key_findings.map((finding, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm">
                    <CheckCircle className="h-3 w-3 mt-1 text-green-600 flex-shrink-0" />
                    <span>{finding}</span>
                  </li>
                ))}
              </ul>
            </div>

            <Separator />

            {/* Recommendations */}
            <div className="space-y-3">
              <h3 className="font-semibold flex items-center gap-2">
                <Shield className="h-4 w-4" />
                Safety Recommendations
              </h3>
              <ul className="space-y-2">
                {report.recommendations.map((recommendation, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm">
                    <AlertTriangle className="h-3 w-3 mt-1 text-orange-600 flex-shrink-0" />
                    <span>{recommendation}</span>
                  </li>
                ))}
              </ul>
            </div>

            <Separator />

            {/* Detailed Analysis */}
            <div className="space-y-3">
              <h3 className="font-semibold">Detailed Analysis</h3>
              <div className="text-sm text-muted-foreground whitespace-pre-wrap">
                {report.detailed_analysis}
              </div>
            </div>

            <Separator />

            {/* Technical Information */}
            <div className="space-y-3">
              <h3 className="font-semibold">Technical Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="font-medium">Video File:</span>
                    <span className="text-muted-foreground">{report.video_context.video_filename || 'Unknown'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Fall Detected:</span>
                    <Badge variant={report.video_context.fall_detected ? "destructive" : "default"} className="text-xs">
                      {report.video_context.fall_detected ? "Yes" : "No"}
                    </Badge>
                  </div>
                  {report.video_context.location && (
                    <div className="flex justify-between">
                      <span className="font-medium">Location:</span>
                      <span className="text-muted-foreground">{report.video_context.location}</span>
                    </div>
                  )}
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="font-medium">AI Model:</span>
                    <span className="text-muted-foreground">{report.model_used}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Processing Time:</span>
                    <span className="text-muted-foreground">{(report.video_context.processing_time || 0).toFixed(1)}s</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Generated:</span>
                    <span className="text-muted-foreground">{new Date(report.generated_at).toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Model Version:</span>
                    <span className="text-muted-foreground">{report.video_context.model_version || 'Unknown'}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
