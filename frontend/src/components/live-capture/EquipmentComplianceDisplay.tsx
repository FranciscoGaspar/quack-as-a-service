"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { FactoryEntries } from "@/services/factoryEntries.service";
import { AlertTriangle, CheckCircle, Shield, XCircle } from "lucide-react";

interface EquipmentComplianceDisplayProps {
  complianceData: FactoryEntries;
  showComplianceDialog: boolean;
  setShowComplianceDialog: (show: boolean) => void;
}

const equipmentLabels: Record<string, string> = {
  mask: "Face Mask",
  boots: "Safety Boots",
  hairnet: "Hair Net",
  hard_hat: "Hard Hat",
  gloves: "Gloves",
  left_glove: "Left Glove",
  right_glove: "Right Glove",
  safety_vest: "Safety Vest",
  safety_glasses: "Safety Glasses",
};

export const EquipmentComplianceDisplay = ({
  complianceData,
  showComplianceDialog,
  setShowComplianceDialog,
}: EquipmentComplianceDisplayProps) => {
  const { equipment, image_url, is_compliant, room_name, entered_at } =
    complianceData;

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <Dialog onOpenChange={setShowComplianceDialog} open={showComplianceDialog}>
      <DialogContent className="!max-w-2xl h-[90vh] flex flex-col">
        <DialogHeader className="flex-shrink-0">
          <DialogTitle>
            <div className="flex items-center gap-2">
              <Shield />
              Equipment Compliance Report
            </div>
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-6 overflow-y-auto flex-1">
          {/* Header Card */}
          <Card>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    Room
                  </p>
                  <p className="text-lg font-semibold">{room_name}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    Status
                  </p>
                  <Badge
                    className="text-sm"
                    variant={is_compliant ? "default" : "destructive"}
                  >
                    {is_compliant ? "Compliant" : "Non-Compliant"}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    Entry Time
                  </p>
                  <p className="text-sm">{formatDateTime(entered_at)}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Captured Image */}
          <div>
            <p className="font-bold">Captured Image</p>
            <div className="flex justify-center">
              <img
                alt="Equipment compliance check"
                className="max-w-full h-auto rounded-lg"
                src={image_url}
              />
            </div>
          </div>

          {/* Equipment Status */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {is_compliant ? (
                  <CheckCircle className="h-5 w-5 text-green-600" />
                ) : (
                  <AlertTriangle className="h-5 w-5 text-red-600" />
                )}
                Equipment Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(equipment).map(([key, isPresent]) => {
                  const label = equipmentLabels[key] || key;

                  return (
                    <div
                      className={`flex items-center justify-between p-3 rounded-lg border ${
                        isPresent
                          ? "bg-green-50 border-green-200"
                          : "bg-red-50 border-red-200"
                      }`}
                      key={key}
                    >
                      <span className="font-medium">{label}</span>
                      <div className="flex items-center gap-2">
                        {isPresent ? (
                          <>
                            <CheckCircle className="h-4 w-4 text-green-600" />
                            <span className="text-sm text-green-700">
                              Present
                            </span>
                          </>
                        ) : (
                          <>
                            <XCircle className="h-4 w-4 text-red-600" />
                            <span className="text-sm text-red-700">
                              Missing
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      </DialogContent>
    </Dialog>
  );
};
