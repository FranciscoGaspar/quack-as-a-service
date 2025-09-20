"use client";

import { EquipmentComplianceDisplay } from "@/components/live-capture/EquipmentComplianceDisplay";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useCameraFeed } from "@/hooks/useCameraFeed";
import { cn } from "@/lib/utils";
import {
  CameraIcon,
  QrCode,
  Shirt,
  UploadCloud,
  type LucideIcon,
} from "lucide-react";
import Image from "next/image";

type FeedTitleProps = { icon: LucideIcon; state: string };

const FeedTitle = ({ icon, state }: FeedTitleProps) => {
  const Icon = icon;

  return (
    <>
      <Icon />
      {state}
    </>
  );
};

type CameraFeedProps = {
  location: string;
};

export const CameraFeed = ({ location }: CameraFeedProps) => {
  const {
    videoRef,
    canvasRef,
    state,
    countdown,
    capturedImage,
    user,
    complianceData,
    showComplianceDialog,
    setShowComplianceDialog,
    captureImage,
    uploadImage,
    isUploading,
  } = useCameraFeed(location);

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {state === 0 && (
              <FeedTitle icon={QrCode} state="Show your QR Code" />
            )}
            {state === 1 && <FeedTitle icon={Shirt} state="Show your EPIs" />}
          </CardTitle>
        </CardHeader>
        <CardContent className="relative p-0">
          {capturedImage && (
            <Image
              alt="Captured"
              className="max-w-full h-auto scale-x-[-1]"
              height={720}
              src={capturedImage}
              unoptimized
              width={1280}
            />
          )}

          <video
            autoPlay
            className={cn(
              "w-full h-auto scale-x-[-1]",
              !capturedImage ? "block" : "hidden",
            )}
            muted
            playsInline
            ref={videoRef}
          />
          <canvas className="hidden" ref={canvasRef} />

          {countdown !== null && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-lg">
              <div className="text-8xl font-bold text-white animate-pulse">
                {countdown}
              </div>
            </div>
          )}

          {user !== null && (
            <div className="absolute inset-0 h-32 p-4">
              <div className="absolute flex p-4 bg-black/50 rounded-lg">
                <div className="text-3xl font-bold text-white animate-pulse">
                  {user.name}
                </div>
              </div>
            </div>
          )}
        </CardContent>
        <CardFooter className="flex items-center justify-center gap-4">
          {state === 0 && !capturedImage && (
            <Button disabled={isUploading} onClick={captureImage}>
              <CameraIcon />
              Take Photo
            </Button>
          )}

          <Button
            disabled={isUploading || !capturedImage}
            onClick={uploadImage}
          >
            <UploadCloud />
            Upload Photo
          </Button>
        </CardFooter>
      </Card>

      {complianceData && (
        <EquipmentComplianceDisplay
          complianceData={complianceData}
          setShowComplianceDialog={setShowComplianceDialog}
          showComplianceDialog={showComplianceDialog}
        />
      )}
    </>
  );
};
