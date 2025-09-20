"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import axiosClient from "@/lib/axiosClient";
import { AlertCircle, Camera, CheckCircle, Download, RotateCcw, Upload } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { EquipmentComplianceDisplay } from "./EquipmentComplianceDisplay";

const LoadingLiveCapture = () => {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
        <p>Loading camera...</p>
      </div>
    </div>
  );
};

const EmptyLiveCapture = () => {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="text-center">
        <Camera className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
        <p className="text-muted-foreground">Camera not available</p>
      </div>
    </div>
  );
};

export const LiveCapture = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [isCapturing, setIsCapturing] = useState(false);
  const [countdown, setCountdown] = useState<number | null>(null);
  
  // Form state for upload
  const [roomName, setRoomName] = useState("");
  const [userId, setUserId] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<"idle" | "success" | "error">("idle");
  const [uploadMessage, setUploadMessage] = useState("");
  const [complianceData, setComplianceData] = useState<any>(null);
  const [showComplianceDialog, setShowComplianceDialog] = useState(false);
  const [hideAfterUpload, setHideAfterUpload] = useState(false);

  // Initialize camera
  useEffect(() => {
    const initCamera = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: { 
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'environment' // Use back camera if available
          },
          audio: false
        });
        
        setStream(mediaStream);
        
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }
        
        setIsLoading(false);
      } catch (err) {
        console.error("Error accessing camera:", err);
        setError("Unable to access camera. Please check permissions.");
        setIsLoading(false);
      }
    };

    initCamera();

    // Cleanup on unmount
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startCountdown = () => {
    setIsCapturing(true);
    setCountdown(3);
    
    const countdownInterval = setInterval(() => {
      setCountdown(prev => {
        if (prev === null || prev <= 1) {
          clearInterval(countdownInterval);
          captureImage();
          return null;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const captureImage = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    if (!context) return;

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw the current video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert canvas to image data URL
    const imageDataUrl = canvas.toDataURL('image/jpeg', 0.8);
    setCapturedImage(imageDataUrl);
    setIsCapturing(false);
    setHideAfterUpload(false); // Reset hide state for new capture
  };

  const downloadImage = () => {
    if (!capturedImage) return;

    const link = document.createElement('a');
    link.download = `capture-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.jpg`;
    link.href = capturedImage;
    link.click();
  };

  const uploadImage = async () => {
    if (!capturedImage || !roomName.trim() || !userId.trim()) {
      setUploadStatus("error");
      setUploadMessage("Please fill in room name and user ID");
      return;
    }

    try {
      setIsUploading(true);
      setUploadStatus("idle");
      setUploadMessage("");

      // Convert data URL to File object
      const response = await fetch(capturedImage);
      const blob = await response.blob();
      const file = new File([blob], "captured-image.jpg", { type: "image/jpeg" });

      // Create FormData for multipart upload
      const formData = new FormData();
      formData.append("image", file);
      formData.append("room_name", roomName.trim());
      formData.append("user_id", userId.trim());

      // Upload to backend
      const uploadResponse = await axiosClient.post("/entries/upload-image", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setUploadStatus("success");
      setUploadMessage("Image uploaded successfully!");
      
      // Store compliance data from response and show dialog
      if (uploadResponse.data) {
        setComplianceData(uploadResponse.data);
        setShowComplianceDialog(true);
        setHideAfterUpload(true);
      }
      
      // Reset form fields after successful upload (keep dialog open)
      setTimeout(() => {
        resetFormFields();
      }, 2000);

    } catch (error: any) {
      console.error("Upload error:", error);
      setUploadStatus("error");
      setUploadMessage(
        error.response?.data?.detail || 
        error.message || 
        "Failed to upload image. Please try again."
      );
    } finally {
      setIsUploading(false);
    }
  };

  const resetCapture = () => {
    setCapturedImage(null);
    setCountdown(null);
    setIsCapturing(false);
    setUploadStatus("idle");
    setUploadMessage("");
    setComplianceData(null);
    setShowComplianceDialog(false);
    setHideAfterUpload(false);
  };

  const resetFormFields = () => {
    setRoomName("");
    setUserId("");
    setUploadStatus("idle");
    setUploadMessage("");
  };

  if (isLoading) {
    return <LoadingLiveCapture />;
  }

  if (error) {
    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardContent className="p-6">
          <div className="text-center">
            <Camera className="h-12 w-12 text-destructive mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Camera Error</h3>
            <p className="text-muted-foreground mb-4">{error}</p>
            <Button onClick={() => window.location.reload()}>
              Try Again
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Camera className="h-5 w-5" />
            Live Camera Feed
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-auto rounded-lg border"
            />
            <canvas
              ref={canvasRef}
              className="hidden"
            />
            
            {/* Countdown overlay */}
            {countdown !== null && (
              <div className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-lg">
                <div className="text-8xl font-bold text-white animate-pulse">
                  {countdown}
                </div>
              </div>
            )}
          </div>
          
          <div className="flex justify-center mt-4 gap-4">
            <Button
              onClick={startCountdown}
              disabled={isCapturing}
              size="lg"
              className="min-w-32"
            >
              {isCapturing ? "Capturing..." : "Take Photo"}
            </Button>
            
            {capturedImage && !hideAfterUpload && (
              <>
                <Button
                  onClick={downloadImage}
                  variant="outline"
                  size="lg"
                  className="min-w-32"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
                <Button
                  onClick={resetCapture}
                  variant="outline"
                  size="lg"
                  className="min-w-32"
                >
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Reset
                </Button>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Captured Image Preview */}
      {capturedImage && !hideAfterUpload && (
        <Card>
          <CardHeader>
            <CardTitle>Captured Image</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex justify-center">
              <img
                src={capturedImage}
                alt="Captured"
                className="max-w-full h-auto rounded-lg border"
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Upload Form */}
      {capturedImage && !hideAfterUpload && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5" />
              Upload to Backend
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="roomName">Room Name</Label>
                <Input
                  id="roomName"
                  type="text"
                  placeholder="e.g., Laboratory A"
                  value={roomName}
                  onChange={(e) => setRoomName(e.target.value)}
                  disabled={isUploading}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="userId">User ID</Label>
                <Input
                  id="userId"
                  type="number"
                  placeholder="e.g., 1"
                  value={userId}
                  onChange={(e) => setUserId(e.target.value)}
                  disabled={isUploading}
                />
              </div>
            </div>

            {/* Upload Status */}
            {uploadStatus !== "idle" && (
              <div className={`flex items-center gap-2 p-3 rounded-lg ${
                uploadStatus === "success" 
                  ? "bg-green-50 text-green-700 border border-green-200" 
                  : "bg-red-50 text-red-700 border border-red-200"
              }`}>
                {uploadStatus === "success" ? (
                  <CheckCircle className="h-4 w-4" />
                ) : (
                  <AlertCircle className="h-4 w-4" />
                )}
                <span className="text-sm font-medium">{uploadMessage}</span>
              </div>
            )}

            {/* Upload Button */}
            <div className="flex justify-center">
              <Button
                onClick={uploadImage}
                disabled={isUploading || !roomName.trim() || !userId.trim()}
                size="lg"
                className="min-w-40"
              >
                {isUploading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Image
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Equipment Compliance Dialog */}
      <Dialog open={showComplianceDialog} onOpenChange={setShowComplianceDialog}>
        <DialogContent className="max-w-7xl max-h-[120vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Equipment Compliance Report</DialogTitle>
          </DialogHeader>
          {complianceData && (
            <EquipmentComplianceDisplay complianceData={complianceData} />
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};
