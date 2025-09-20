"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { EmotionalAnalysis } from "@/services/emotionalAnalysis.service";
import {
  AlertCircle,
  Brain,
  Calendar,
  CheckCircle,
  Info,
  MapPin,
  TrendingUp,
  User,
  Users
} from "lucide-react";
import { useState } from "react";

interface EmotionalAnalysisDialogProps {
  analysis: EmotionalAnalysis;
  entryInfo: {
    id: number;
    user_id: number;
    room_name: string;
    entered_at: string;
  };
  children: React.ReactNode;
}

const EmotionBadge = ({ emotion, confidence }: { emotion: string; confidence: number }) => {
  const getEmotionColor = (emotion: string) => {
    switch (emotion.toLowerCase()) {
      case 'happy':
      case 'joy':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'sad':
      case 'sorrow':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'angry':
      case 'anger':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'fear':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'surprise':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'disgust':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'neutral':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <Badge className={`${getEmotionColor(emotion)} font-medium`}>
      {emotion} ({confidence.toFixed(1)}%)
    </Badge>
  );
};

const QualityIndicator = ({ quality }: { quality: string }) => {
  const getQualityColor = (quality: string) => {
    switch (quality.toLowerCase()) {
      case 'excellent':
        return 'text-green-600';
      case 'good':
        return 'text-blue-600';
      case 'fair':
        return 'text-yellow-600';
      case 'poor':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getQualityIcon = (quality: string) => {
    switch (quality.toLowerCase()) {
      case 'excellent':
        return <CheckCircle className="h-4 w-4" />;
      case 'good':
        return <CheckCircle className="h-4 w-4" />;
      case 'fair':
        return <AlertCircle className="h-4 w-4" />;
      case 'poor':
        return <AlertCircle className="h-4 w-4" />;
      default:
        return <Info className="h-4 w-4" />;
    }
  };

  return (
    <div className={`flex items-center gap-2 ${getQualityColor(quality)}`}>
      {getQualityIcon(quality)}
      <span className="font-medium capitalize">{quality}</span>
    </div>
  );
};

export const EmotionalAnalysisDialog = ({ analysis, entryInfo, children }: EmotionalAnalysisDialogProps) => {
  const [isOpen, setIsOpen] = useState(false);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'text-green-600';
    if (confidence >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {children}
      </DialogTrigger>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-blue-600" />
            Emotional Analysis Details
          </DialogTitle>
          <DialogDescription>
            Detailed emotional analysis results for entry #{entryInfo.id}
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="h-[70vh] pr-4">
          <div className="space-y-6">
            {/* Overview Cards */}
            <div className="space-y-4 w-full">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Emotional Analysis Overview</CardTitle>
                </CardHeader>
                <CardContent className="p-6 space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-3">
                      <h4 className="font-semibold text-gray-800 text-sm uppercase tracking-wide">Entry Details</h4>
                      <div className="space-y-3">
                        <div className="flex items-center gap-3 p-2 bg-white rounded-lg shadow-sm border border-gray-100">
                          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                            <User className="h-4 w-4 text-blue-600" />
                          </div>
                          <div>
                            <div className="text-xs text-gray-500">User ID</div>
                            <div className="font-medium text-gray-900">{entryInfo.user_id}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-3 p-2 bg-white rounded-lg shadow-sm border border-gray-100">
                          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                            <MapPin className="h-4 w-4 text-green-600" />
                          </div>
                          <div>
                            <div className="text-xs text-gray-500">Room</div>
                            <div className="font-medium text-gray-900">{entryInfo.room_name}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-3 p-2 bg-white rounded-lg shadow-sm border border-gray-100">
                          <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                            <Calendar className="h-4 w-4 text-purple-600" />
                          </div>
                          <div>
                            <div className="text-xs text-gray-500">Entry Time</div>
                            <div className="font-medium text-gray-900">{formatDate(entryInfo.entered_at)}</div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-3">
                      <h4 className="font-semibold text-gray-800 text-sm uppercase tracking-wide">Analysis Results</h4>
                      <div className="space-y-3">
                        <div className="flex items-center gap-3 p-2 bg-white rounded-lg shadow-sm border border-gray-100">
                          <div className="w-8 h-8 bg-emerald-100 rounded-full flex items-center justify-center">
                            <Users className="h-4 w-4 text-emerald-600" />
                          </div>
                          <div>
                            <div className="text-xs text-gray-500">Faces Detected</div>
                            <div className="font-medium text-gray-900 text-lg">{analysis.faces_detected}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-3 p-2 bg-white rounded-lg shadow-sm border border-gray-100">
                          <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
                            <Brain className="h-4 w-4 text-orange-600" />
                          </div>
                          <div>
                            <div className="text-xs text-gray-500">Dominant Emotion</div>
                            <div className="font-medium text-gray-900 text-lg">{analysis.dominant_emotion || 'N/A'}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-3 p-2 bg-white rounded-lg shadow-sm border border-gray-100">
                          <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
                            <TrendingUp className="h-4 w-4 text-indigo-600" />
                          </div>
                          <div className="flex-1">
                            <div className="text-xs text-gray-500">Confidence Level</div>
                            <div className="flex items-center gap-2">
                              <div className={`font-medium text-lg ${getConfidenceColor(analysis.overall_confidence || 0)}`}>
                                {analysis.overall_confidence?.toFixed(1) || 'N/A'}%
                              </div>
                              {analysis.overall_confidence && (
                                <Progress 
                                  value={analysis.overall_confidence} 
                                  className="flex-1 h-2"
                                />
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="flex items-center justify-center">
                      <div className="text-center">
                        <div className="text-xs text-gray-500 mb-2">Image Quality Assessment</div>
                        <QualityIndicator quality={analysis.image_quality || 'unknown'} />
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>


                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Emotional Analysis</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {analysis.dominant_emotion && (
                      <div className="space-y-2">
                        <h4 className="font-medium">Dominant Emotion</h4>
                        <div className="flex items-center gap-3">
                          <EmotionBadge 
                            emotion={analysis.dominant_emotion} 
                            confidence={analysis.overall_confidence || 0} 
                          />
                          <div className="flex-1">
                            <Progress 
                              value={analysis.overall_confidence || 0} 
                              className="h-2"
                            />
                          </div>
                        </div>
                      </div>
                    )}

                    {analysis.analysis_data?.face_analyses && (
                      <div className="space-y-4">
                        <h4 className="font-medium">All Detected Emotions</h4>
                        {analysis.analysis_data.face_analyses.map((face) => (
                          <div key={face.face_id} className="border rounded-lg p-4 space-x-2">
                              {face.emotions.map((emotion, emotionIndex) => (
                                <EmotionBadge
                                  key={emotionIndex}
                                  emotion={emotion.emotion}
                                  confidence={emotion.confidence}
                                />
                              ))}
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Recommendations</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {analysis.recommendations && analysis.recommendations.length > 0 ? (
                      <ul className="space-y-2">
                        {analysis.recommendations.map((recommendation, index) => (
                          <li key={index} className="flex items-start gap-2 text-sm">
                            <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                            <span>{recommendation}</span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-gray-500 text-sm">No specific recommendations available.</p>
                    )}
                  </CardContent>
                </Card>

            {/* Analysis Metadata */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Analysis Metadata</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm text-gray-600">
                <div>Analysis performed: {formatDate(analysis.analyzed_at)}</div>
                <div>Created: {formatDate(analysis.created_at)}</div>
                {analysis.analysis_data?.analysis_timestamp && (
                  <div>Processing timestamp: {formatDate(analysis.analysis_data.analysis_timestamp)}</div>
                )}
              </CardContent>
            </Card>
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
};
