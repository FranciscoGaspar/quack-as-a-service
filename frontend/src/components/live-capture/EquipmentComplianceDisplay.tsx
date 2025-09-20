"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle, CheckCircle, Shield, XCircle } from "lucide-react";

interface EquipmentComplianceData {
  room_name: string;
  equipment: {
    mask: boolean;
    boots: boolean;
    hairnet: boolean;
    hard_hat: boolean;
    left_glove: boolean;
    right_glove: boolean;
    safety_vest: boolean;
    safety_glasses: boolean;
  };
  image_url: string;
  id: number;
  user_id: number;
  entered_at: string;
  created_at: string;
  is_compliant: boolean;
  missing_equipment: string[];
}

interface EquipmentComplianceDisplayProps {
  complianceData: EquipmentComplianceData;
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
  safety_glasses: "Safety Glasses"
};

export const EquipmentComplianceDisplay = ({ complianceData }: EquipmentComplianceDisplayProps) => {
  const { equipment, image_url, is_compliant, missing_equipment, room_name, entered_at } = complianceData;

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Equipment Compliance Report
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Room</p>
              <p className="text-lg font-semibold">{room_name}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Status</p>
              <Badge 
                variant={is_compliant ? "default" : "destructive"}
                className="text-sm"
              >
                {is_compliant ? "Compliant" : "Non-Compliant"}
              </Badge>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Entry Time</p>
              <p className="text-sm">{formatDateTime(entered_at)}</p>
            </div>
          </div>
        </CardContent>
      </Card>

        {/* Captured Image */}
        <Card>
          <CardHeader>
            <CardTitle>Captured Image</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex justify-center">
              <img
                src={image_url}
                alt="Equipment compliance check"
                className="max-w-full h-auto rounded-lg border"
              />
            </div>
          </CardContent>
        </Card>

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
                const isMissing = missing_equipment.includes(key);
                
                return (
                  <div 
                    key={key}
                    className={`flex items-center justify-between p-3 rounded-lg border ${
                      isPresent 
                        ? "bg-green-50 border-green-200" 
                        : "bg-red-50 border-red-200"
                    }`}
                  >
                    <span className="font-medium">{label}</span>
                    <div className="flex items-center gap-2">
                      {isPresent ? (
                        <>
                          <CheckCircle className="h-4 w-4 text-green-600" />
                          <span className="text-sm text-green-700">Present</span>
                        </>
                      ) : (
                        <>
                          <XCircle className="h-4 w-4 text-red-600" />
                          <span className="text-sm text-red-700">Missing</span>
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
  );
};
