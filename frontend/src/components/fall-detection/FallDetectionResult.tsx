"use client";

import { useState } from "react";
import { 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Clock, 
  MapPin, 
  User, 
  Eye,
  Download,
  RotateCcw
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Separator } from "@/components/ui/separator";
import type { FallDetectionResponse } from "@/services/fallDetection.service";

interface FallDetectionResultProps {
  result: FallDetectionResponse;
  onNewAnalysis: () => void;
}

export const FallDetectionResult = ({ result, onNewAnalysis }: FallDetectionResultProps) => {
  const [showVideoDialog, setShowVideoDialog] = useState(false);
  const [selectedVideoUrl, setSelectedVideoUrl] = useState<string>("");
  const [videoTitle, setVideoTitle] = useState<string>("");

  const { detection_result } = result;

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toFixed(1).padStart(4, '0')}`;
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
            <Button
              variant="outline"
              size="sm"
              onClick={onNewAnalysis}
            >
              <RotateCcw className="mr-2 h-4 w-4" />
              New Analysis
            </Button>
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
              
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4" />
                <span className="font-medium">Duration:</span>
                <span className="text-muted-foreground">
                  {formatDuration(detection_result.video_duration)}
                </span>
              </div>
              
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

          {/* Detection Details */}
          {detection_result.fall_detected && (
            <div className="space-y-3">
              <h4 className="font-medium">Detection Details</h4>
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <XCircle className="h-4 w-4 text-red-600" />
                  <span className="font-medium text-red-800">
                    {detection_result.total_detections} fall incident(s) detected
                  </span>
                </div>
                
                {detection_result.confidence_scores.length > 0 && (
                  <div className="space-y-2">
                    <span className="text-sm font-medium text-red-800">Confidence Scores:</span>
                    <div className="flex flex-wrap gap-2">
                      {detection_result.confidence_scores.map((score, index) => (
                        <Badge key={index} variant="outline" className="text-red-700 border-red-300">
                          {(score * 100).toFixed(1)}%
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

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
    </>
  );
};
