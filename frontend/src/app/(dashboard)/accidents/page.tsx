"use client";

import { useState } from "react";
import { AlertTriangle, Upload, VideoIcon, CheckCircle, XCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { FallDetectionUpload } from "@/components/fall-detection/FallDetectionUpload";
import { FallDetectionResult } from "@/components/fall-detection/FallDetectionResult";
import type { FallDetectionResponse } from "@/services/fallDetection.service";

export default function AccidentsPage() {
  const [detectionResult, setDetectionResult] = useState<FallDetectionResponse | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleAnalysisComplete = (result: FallDetectionResponse) => {
    setDetectionResult(result);
    setIsAnalyzing(false);
  };

  const handleAnalysisStart = () => {
    setIsAnalyzing(true);
    setDetectionResult(null);
  };

  const handleNewAnalysis = () => {
    setDetectionResult(null);
    setIsAnalyzing(false);
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <AlertTriangle className="h-8 w-8 text-red-600" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Fall Accident Detection</h1>
          <p className="text-muted-foreground">
            Upload video footage to analyze for fall incidents using AI detection
          </p>
        </div>
      </div>

      {/* Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Detection Status</CardTitle>
            <VideoIcon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isAnalyzing ? (
                <Badge variant="secondary" className="text-sm">
                  Analyzing...
                </Badge>
              ) : detectionResult ? (
                <Badge 
                  variant={detectionResult.detection_result.fall_detected ? "destructive" : "default"}
                  className="text-sm"
                >
                  {detectionResult.detection_result.fall_detected ? "Fall Detected" : "No Fall"}
                </Badge>
              ) : (
                <span className="text-muted-foreground">Ready</span>
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              Current analysis status
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">AI Model</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">YOLO</div>
            <p className="text-xs text-muted-foreground">
              Fall detection model
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Processing Time</CardTitle>
            <Upload className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {detectionResult ? 
                `${detectionResult.detection_result.processing_time.toFixed(1)}s` : 
                "--"
              }
            </div>
            <p className="text-xs text-muted-foreground">
              Last analysis duration
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="h-5 w-5" />
                Video Upload & Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <FallDetectionUpload
                onAnalysisStart={handleAnalysisStart}
                onAnalysisComplete={handleAnalysisComplete}
                disabled={isAnalyzing}
              />
            </CardContent>
          </Card>

          {/* Information Card */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Supported Formats</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex flex-wrap gap-2">
                <Badge variant="outline">MP4</Badge>
                <Badge variant="outline">AVI</Badge>
                <Badge variant="outline">MOV</Badge>
              </div>
              <p className="text-sm text-muted-foreground">
                Maximum file size: 100MB
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Results Section */}
        <div className="space-y-4">
          {isAnalyzing && (
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                Analyzing video for fall detection. This may take a few minutes depending on video length...
              </AlertDescription>
            </Alert>
          )}

          {detectionResult && (
            <FallDetectionResult 
              result={detectionResult}
              onNewAnalysis={handleNewAnalysis}
            />
          )}

          {!detectionResult && !isAnalyzing && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm text-muted-foreground">Analysis Results</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-center h-32 border-2 border-dashed border-muted rounded-lg">
                  <div className="text-center">
                    <VideoIcon className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                    <p className="text-sm text-muted-foreground">
                      Upload a video to see analysis results
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
