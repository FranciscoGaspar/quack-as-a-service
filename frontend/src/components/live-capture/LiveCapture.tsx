"use client";

import { ErrorAlert } from "@/components/ErrorAlert";
import { Alert, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { getRequiredEPIs } from "@/constants/requiredEPIs";
import { useSendEPI } from "@/hooks/factory-entries/useSendEPI";
import { useSendQR } from "@/hooks/factory-entries/useSendQR";
import { Camera, Download, Loader2, QrCode, Shirt } from "lucide-react";
import Image from "next/image";
import { useEffect, useRef, useState } from "react";
import { EquipmentComplianceDisplay } from "./EquipmentComplianceDisplay";

const LoadingLiveCapture = () => {
  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <Loader2 className="animate-spin text-primary" size={64} />
      <p className="text-muted-foreground">Loading camera...</p>
    </div>
  );
};

type LiveCaptureProps = {
  location: string;
};

export const LiveCapture = ({ location }: LiveCaptureProps) => {
  const [idState, setIdState] = useState(0);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [isCapturing, setIsCapturing] = useState(false);
  const [countdown, setCountdown] = useState<number | null>(null);

  // Form state for upload
  const [userId, setUserId] = useState("");

  const [complianceData, setComplianceData] = useState<any>(null);
  const [showComplianceDialog, setShowComplianceDialog] = useState(false);
  const [hideAfterUpload, setHideAfterUpload] = useState(false);

  const { mutateAsync: sendQR, isPending: pendingQR } = useSendQR();
  const { mutateAsync: sendEPI, isPending: pendingEPI } = useSendEPI();

  const isUploading = pendingQR || pendingEPI;
  const requiredEPIs = getRequiredEPIs(location);

  // Initialize camera
  // biome-ignore lint/correctness/useExhaustiveDependencies: No Dependencies
  useEffect(() => {
    const initCamera = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: "environment", // Use back camera if available
          },
          audio: false,
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
        for (const track of stream.getTracks()) {
          track.stop();
        }
      }
    };
  }, []);

  const startCountdown = () => {
    setIsCapturing(true);
    setCountdown(3);

    const countdownInterval = setInterval(() => {
      setCountdown((prev) => {
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
    const context = canvas.getContext("2d");

    if (!context) return;

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw the current video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert canvas to image data URL
    const imageDataUrl = canvas.toDataURL("image/jpeg", 0.8);
    setCapturedImage(imageDataUrl);
    setIsCapturing(false);
    setHideAfterUpload(false); // Reset hide state for new capture
  };

  const downloadImage = () => {
    if (!capturedImage) return;

    const link = document.createElement("a");
    link.download = `capture-${new Date()
      .toISOString()
      .slice(0, 19)
      .replace(/:/g, "-")}.jpg`;
    link.href = capturedImage;
    link.click();
  };

  const uploadImage = async () => {
    if (!capturedImage) return;

    if (idState === 0) {
      const response = await fetch(capturedImage);
      const blob = await response.blob();
      const file = new File([blob], "captured-image.jpg", {
        type: "image/jpeg",
      });

      const formData = new FormData();
      formData.append("file", file);

      const { user_id } = await sendQR(formData);
      setUserId(user_id);
      setIdState(1);

      return;
    }

    if (idState === 1) {
      const response = await fetch(capturedImage);
      const blob = await response.blob();
      const file = new File([blob], "captured-image.jpg", {
        type: "image/jpeg",
      });

      // Create FormData for multipart upload
      const formData = new FormData();
      formData.append("image", file);
      formData.append("room_name", location);
      formData.append("user_id", userId);

      // Upload to backend
      const data = await sendEPI(formData);
      // Store compliance data from response and show dialog
      if (data) {
        setComplianceData(data);
        setShowComplianceDialog(true);
        setHideAfterUpload(true);
      }
    }
  };

  if (isLoading) {
    return <LoadingLiveCapture />;
  }

  if (error) {
    return <ErrorAlert />;
  }

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Location Required EPIs</CardTitle>
          <CardDescription>
            <span className="capitalize">{location.replaceAll("-", " ")}</span>{" "}
            required EPIs are:
          </CardDescription>
        </CardHeader>
        <CardContent className="flex gap-8">
          {requiredEPIs.map((epi) => {
            return (
              <div className="flex items-center gap-2" key={epi}>
                <Switch checked disabled />
                {epi}
              </div>
            );
          })}
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Camera />
            Live Camera Feed
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {idState === 0 && (
            <Alert>
              <QrCode />
              <AlertTitle>Show your QR Code</AlertTitle>
            </Alert>
          )}

          {idState === 1 && (
            <Alert>
              <Shirt />
              <AlertTitle>Show your EPIs</AlertTitle>
            </Alert>
          )}
          <div className="relative">
            <video
              autoPlay
              className="w-full h-auto rounded-lg border"
              muted
              playsInline
              ref={videoRef}
            />
            <canvas className="hidden" ref={canvasRef} />

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
              className="min-w-32"
              disabled={isCapturing}
              onClick={startCountdown}
              size="lg"
            >
              {isCapturing ? "Capturing..." : "Take Photo"}
            </Button>

            {capturedImage && !hideAfterUpload && (
              <>
                <Button
                  className="min-w-32"
                  onClick={downloadImage}
                  size="lg"
                  variant="outline"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
                <Button
                  className="min-w-40"
                  disabled={isUploading}
                  onClick={uploadImage}
                  size="lg"
                >
                  {isUploading ? (
                    <Loader2 className="animate-spin mr-2 text-white" />
                  ) : (
                    "Upload Image"
                  )}
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
              <Image
                alt="Captured"
                className="max-w-full h-auto rounded-lg border"
                height={720}
                src={capturedImage}
                unoptimized
                width={1280}
              />
            </div>
          </CardContent>
        </Card>
      )}

      {complianceData && (
        <EquipmentComplianceDisplay
          complianceData={complianceData}
          setShowComplianceDialog={setShowComplianceDialog}
          showComplianceDialog={showComplianceDialog}
        />
      )}
    </div>
  );
};
