import { useSendEPI } from "@/hooks/factory-entries/useSendEPI";
import { useSendQR } from "@/hooks/factory-entries/useSendQR";
import { useCallback, useEffect, useRef, useState } from "react";
import { toast } from "sonner";

type UserType = {
  user_id: string;
  name: string;
};

export const useCameraFeed = (location: string) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const [idState, setIdState] = useState(0);
  const [countdown, setCountdown] = useState<number | null>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [user, setUser] = useState<UserType | null>(null);

  const [complianceData, setComplianceData] = useState<any>(null);
  const [showComplianceDialog, setShowComplianceDialog] = useState(false);

  const { mutateAsync: sendQR, isPending: pendingQR } = useSendQR();
  const { mutateAsync: sendEPI, isPending: pendingEPI } = useSendEPI();

  const isUploading = pendingQR || pendingEPI;

  const initCamera = useCallback(async () => {
    const mediaStream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        facingMode: "environment",
      },
      audio: false,
    });

    setStream(mediaStream);

    if (videoRef.current) {
      videoRef.current.srcObject = mediaStream;
    }
  }, []);

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
  };

  const startCountdown = () => {
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

  const uploadImage = async () => {
    if (!capturedImage) return;

    const response = await fetch(capturedImage);
    const blob = await response.blob();
    const file = new File([blob], "captured-image.jpg", {
      type: "image/jpeg",
    });

    const formData = new FormData();

    if (idState === 0) {
      formData.append("file", file);

      const user = await sendQR(formData);
      setUser(user);
      setIdState(1);
      setCapturedImage(null);

      setTimeout(() => {
        startCountdown();
      }, 1000);

      return;
    }

    if (idState === 1) {
      formData.append("image", file);
      formData.append("room_name", location);
      formData.append("user_id", user?.user_id ?? "");

      // Upload to backend
      const data = await sendEPI(formData);
      // Store compliance data from response and show dialog
      if (data) {
        setComplianceData(data);
        setShowComplianceDialog(true);
        setCapturedImage(null);
        setIdState(0);
        setUser(null);
      }
    }
  };

  // biome-ignore lint/correctness/useExhaustiveDependencies: No Dependencies
  useEffect(() => {
    try {
      initCamera();
    } catch {
      toast.error("Unable to access camera. Please check permissions.");
    }

    // Cleanup on unmount
    return () => {
      if (stream) {
        for (const track of stream.getTracks()) {
          track.stop();
        }
      }
    };
  }, []);

  return {
    videoRef,
    canvasRef,
    state: idState,
    countdown,
    setCountdown,
    capturedImage,
    user,
    complianceData,
    showComplianceDialog,
    setShowComplianceDialog,
    captureImage,
    uploadImage,
    isUploading,
  };
};
