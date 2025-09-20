"use client";

import { CameraFeed } from "@/components/live-capture/CameraFeed";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { getRequiredEPIs } from "@/constants/requiredEPIs";

type LiveCaptureProps = {
  location: string;
};

export const LiveCapture = ({ location }: LiveCaptureProps) => {
  const requiredEPIs = getRequiredEPIs(location);

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

      <CameraFeed location={location} />
    </div>
  );
};
