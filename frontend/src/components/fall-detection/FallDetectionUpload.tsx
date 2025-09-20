"use client";

import { useState, useRef } from "react";
import { Upload, VideoIcon, X, Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { 
  AnalyzeVideoForFalls, 
  GetFallDetectionStatus,
  type FallDetectionResponse 
} from "@/services/fallDetection.service";
import { useToast } from "@/hooks/use-toast";

interface FallDetectionUploadProps {
  onAnalysisStart: () => void;
  onAnalysisComplete: (result: FallDetectionResponse) => void;
  disabled?: boolean;
}

export const FallDetectionUpload = ({
  onAnalysisStart,
  onAnalysisComplete,
  disabled = false
}: FallDetectionUploadProps) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [userId, setUserId] = useState<string>("");
  const [location, setLocation] = useState<string>("");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/quicktime'];
    if (!validTypes.includes(file.type)) {
      toast({
        title: "Invalid file type",
        description: "Please select a video file (MP4, AVI, or MOV)",
        variant: "destructive",
      });
      return;
    }

    // Validate file size (100MB)
    const maxSize = 100 * 1024 * 1024;
    if (file.size > maxSize) {
      toast({
        title: "File too large",
        description: "Please select a video file smaller than 100MB",
        variant: "destructive",
      });
      return;
    }

    setSelectedFile(file);
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      toast({
        title: "No file selected",
        description: "Please select a video file to analyze",
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);
    onAnalysisStart();

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 500);

      const userIdNum = userId ? parseInt(userId) : undefined;
      const result = await AnalyzeVideoForFalls(selectedFile, userIdNum, location || undefined);

      clearInterval(progressInterval);
      setUploadProgress(100);

      toast({
        title: "Analysis complete",
        description: result.detection_result.fall_detected 
          ? "Fall detected in the video" 
          : "No falls detected in the video",
        variant: result.detection_result.fall_detected ? "destructive" : "default",
      });

      onAnalysisComplete(result);
      
      // Reset form
      setSelectedFile(null);
      setUserId("");
      setLocation("");
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

    } catch (error) {
      console.error("Error analyzing video:", error);
      toast({
        title: "Analysis failed",
        description: error instanceof Error ? error.message : "An error occurred during analysis",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <div className="space-y-4">
      {/* File Upload */}
      <div className="space-y-2">
        <Label htmlFor="video-upload">Video File</Label>
        <div className="border-2 border-dashed border-muted rounded-lg p-6">
          {selectedFile ? (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <VideoIcon className="h-8 w-8 text-blue-600" />
                <div>
                  <p className="font-medium">{selectedFile.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {formatFileSize(selectedFile.size)}
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleRemoveFile}
                disabled={isUploading}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            <div className="text-center">
              <Upload className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
              <div className="space-y-2">
                <p className="text-sm font-medium">Choose a video file</p>
                <p className="text-xs text-muted-foreground">
                  MP4, AVI, or MOV up to 100MB
                </p>
              </div>
            </div>
          )}
          <Input
            ref={fileInputRef}
            id="video-upload"
            type="file"
            accept="video/mp4,video/avi,video/mov,video/quicktime"
            onChange={handleFileSelect}
            disabled={isUploading || disabled}
            className="mt-2"
          />
        </div>
      </div>

      {/* Optional Fields */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="user-id">User ID (Optional)</Label>
          <Input
            id="user-id"
            type="number"
            placeholder="Enter user ID"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            disabled={isUploading || disabled}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="location">Location (Optional)</Label>
          <Input
            id="location"
            placeholder="e.g., Factory Floor, Warehouse"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            disabled={isUploading || disabled}
          />
        </div>
      </div>

      {/* Upload Progress */}
      {isUploading && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Analyzing video...</span>
            <span>{uploadProgress}%</span>
          </div>
          <Progress value={uploadProgress} className="w-full" />
        </div>
      )}

      {/* Analyze Button */}
      <Button
        onClick={handleAnalyze}
        disabled={!selectedFile || isUploading || disabled}
        className="w-full"
        size="lg"
      >
        {isUploading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Analyzing Video...
          </>
        ) : (
          <>
            <VideoIcon className="mr-2 h-4 w-4" />
            Analyze for Falls
          </>
        )}
      </Button>
    </div>
  );
};
