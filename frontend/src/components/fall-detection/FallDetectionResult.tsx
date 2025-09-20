"use client";

import { useState } from "react";
import { 
  AlertTriangle, 
  CheckCircle, 
  MapPin, 
  User, 
  Eye,
  Download,
  RotateCcw,
  FileText,
  Brain,
  Loader2
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import type { FallDetectionResponse } from "@/services/fallDetection.service";
import { type CustomAnalysisResponse } from "@/services/aiAnalytics.service";
import { GenerateAIReportFromDetection, type AIVideoReport } from "@/services/fallDetection.service";
import { AIReportDialog } from "./AIReportDialog";

interface FallDetectionResultProps {
  result: FallDetectionResponse;
  onNewAnalysis: () => void;
}

export const FallDetectionResult = ({ result, onNewAnalysis }: FallDetectionResultProps) => {
  const [showVideoDialog, setShowVideoDialog] = useState(false);
  const [selectedVideoUrl, setSelectedVideoUrl] = useState<string>("");
  const [videoTitle, setVideoTitle] = useState<string>("");
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [aiReport, setAiReport] = useState<AIVideoReport | null>(null);
  const [showAIReport, setShowAIReport] = useState(false);

  const { detection_result } = result;
  const { toast } = useToast();

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const handleViewVideo = (url: string, title: string) => {
    setSelectedVideoUrl(url);
    setVideoTitle(title);
    setShowVideoDialog(true);
  };

  const handleDownloadVideo = (url: string, filename: string) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleGenerateAIReport = async () => {
    setIsGeneratingReport(true);
    try {
      const response = await GenerateAIReportFromDetection(result);
      setAiReport(response.ai_report);
      setShowAIReport(true);
      
      toast({
        title: "AI Report Generated",
        description: `Comprehensive analysis completed with ${response.ai_report.confidence_score}% confidence`,
        variant: "default",
      });
    } catch (error) {
      console.error("Error generating AI report:", error);
      toast({
        title: "Report generation failed",
        description: error instanceof Error ? error.message : "An error occurred during analysis",
        variant: "destructive",
      });
    } finally {
      setIsGeneratingReport(false);
    }
  };

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              {detection_result.fall_detected ? (
                <AlertTriangle className="h-5 w-5 text-red-600" />
              ) : (
                <CheckCircle className="h-5 w-5 text-green-600" />
              )}
              Fall Detection Results
            </CardTitle>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleGenerateAIReport}
                disabled={isGeneratingReport}
                className="bg-blue-50 hover:bg-blue-100 text-blue-700 border-blue-200"
              >
                {isGeneratingReport ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Brain className="mr-2 h-4 w-4" />
                    Generate AI Report
                  </>
                )}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={onNewAnalysis}
              >
                <RotateCcw className="mr-2 h-4 w-4" />
                New Analysis
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Status Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 rounded-lg border">
              <Badge
                variant={detection_result.fall_detected ? "destructive" : "default"}
                className="text-sm mb-2"
              >
                {detection_result.fall_detected ? "FALL DETECTED" : "NO FALL DETECTED"}
              </Badge>
              <p className="text-xs text-muted-foreground">Detection Status</p>
            </div>
            
            <div className="text-center p-4 rounded-lg border">
              <div className="text-2xl font-bold text-red-600">
                {detection_result.total_detections}
              </div>
              <p className="text-xs text-muted-foreground">Total Detections</p>
            </div>
            
            <div className="text-center p-4 rounded-lg border">
              <div className="text-2xl font-bold">
                {detection_result.processing_time.toFixed(1)}s
              </div>
              <p className="text-xs text-muted-foreground">Processing Time</p>
            </div>
          </div>

          {/* Video Information */}
          <div className="space-y-3">
            <h4 className="font-medium">Video Information</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              {result.video_filename && (
                <div className="flex items-center gap-2">
                  <span className="font-medium">Filename:</span>
                  <span className="text-muted-foreground">{result.video_filename}</span>
                </div>
              )}
              
              {result.location && (
                <div className="flex items-center gap-2">
                  <MapPin className="h-4 w-4" />
                  <span className="font-medium">Location:</span>
                  <span className="text-muted-foreground">{result.location}</span>
                </div>
              )}
              
              {result.user_id && (
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4" />
                  <span className="font-medium">User ID:</span>
                  <span className="text-muted-foreground">{result.user_id}</span>
                </div>
              )}
            </div>
          </div>

          {/* Technical Details */}
          <div className="space-y-3">
            <h4 className="font-medium">Technical Details</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="flex items-center gap-2">
                <span className="font-medium">Model:</span>
                <span className="text-muted-foreground">{detection_result.model_version}</span>
              </div>
              
              <div className="flex items-center gap-2">
                <span className="font-medium">Analysis Time:</span>
                <span className="text-muted-foreground">
                  {formatDateTime(detection_result.analysis_timestamp)}
                </span>
              </div>
            </div>
          </div>

          <Separator />

          {/* Video Actions */}
          <div className="space-y-3">
            <h4 className="font-medium">Video Files</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Original Video */}
              {result.original_video_url && (
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h5 className="font-medium">Original Video</h5>
                        <p className="text-sm text-muted-foreground">
                          Uploaded footage
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleViewVideo(result.original_video_url!, "Original Video")}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDownloadVideo(
                            result.original_video_url!, 
                            `original_${result.video_filename || 'video.mp4'}`
                          )}
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Processed Video */}
              {result.processed_video_url && (
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h5 className="font-medium">Processed Video</h5>
                        <p className="text-sm text-muted-foreground">
                          With detection markers
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleViewVideo(result.processed_video_url!, "Processed Video")}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDownloadVideo(
                            result.processed_video_url!, 
                            `processed_${result.video_filename || 'video.mp4'}`
                          )}
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Video Preview Dialog */}
      <Dialog open={showVideoDialog} onOpenChange={setShowVideoDialog}>
        <DialogContent className="max-w-4xl h-[80vh] flex flex-col">
          <DialogHeader className="flex-shrink-0">
            <DialogTitle>{videoTitle}</DialogTitle>
          </DialogHeader>
          <div className="flex-1 flex items-center justify-center bg-black rounded-lg overflow-hidden">
            {selectedVideoUrl && (
              <video
                controls
                className="max-w-full max-h-full"
                preload="metadata"
              >
                <source src={selectedVideoUrl} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* AI Report Dialog */}
      <AIReportDialog
        report={aiReport}
        isOpen={showAIReport}
        onClose={() => setShowAIReport(false)}
      />
    </>
  );
};
