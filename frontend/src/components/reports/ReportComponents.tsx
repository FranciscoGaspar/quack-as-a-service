"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useFactoryEntries } from "@/hooks/factory-entries/useFactoryEntries";
import type { FactoryEntries } from "@/services/factoryEntries.service";
import { format, isWithinInterval, subDays } from "date-fns";
import { pt } from "date-fns/locale";
import {
  AlertTriangle,
  BarChart3,
  Building,
  Calendar as CalendarIcon,
  CheckCircle,
  Clock,
  Download,
  Filter,
  Shield,
  TrendingUp,
  Users
} from "lucide-react";
import { useMemo, useState } from "react";
import type { DateRange } from "react-day-picker";

interface ComplianceStats {
  totalEntries: number;
  compliantEntries: number;
  nonCompliantEntries: number;
  complianceRate: number;
  mostCommonViolations: Array<{ equipment: string; count: number }>;
  roomStats: Array<{ room: string; entries: number; complianceRate: number }>;
  hourlyStats: Array<{ hour: number; entries: number; complianceRate: number }>;
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

export const ReportsComponent = () => {
  const { data: factoryEntries = [], isLoading } = useFactoryEntries();
  const [dateRange, setDateRange] = useState<DateRange | undefined>({
    from: subDays(new Date(), 30),
    to: new Date()
  });
  const [selectedRoom, setSelectedRoom] = useState<string>("all");
  const [selectedEntry, setSelectedEntry] = useState<FactoryEntries | null>(null);

  // Filter data based on date range and room
  const filteredData = useMemo(() => {
    if (!factoryEntries.length) return [];
    
    return factoryEntries.filter(entry => {
      const entryDate = new Date(entry.entered_at);
      
      // Date range filter
      if (dateRange?.from && dateRange?.to) {
        if (!isWithinInterval(entryDate, { start: dateRange.from, end: dateRange.to })) {
          return false;
        }
      }
      
      // Room filter
      if (selectedRoom !== "all" && entry.room_name !== selectedRoom) {
        return false;
      }
      
      return true;
    });
  }, [factoryEntries, dateRange, selectedRoom]);

  // Calculate compliance statistics
  const complianceStats: ComplianceStats = useMemo(() => {
    if (!filteredData.length) {
      return {
        totalEntries: 0,
        compliantEntries: 0,
        nonCompliantEntries: 0,
        complianceRate: 0,
        mostCommonViolations: [],
        roomStats: [],
        hourlyStats: []
      };
    }

    const totalEntries = filteredData.length;
    const compliantEntries = filteredData.filter(entry => entry.is_compliant).length;
    const nonCompliantEntries = totalEntries - compliantEntries;
    const complianceRate = (compliantEntries / totalEntries) * 100;

    // Calculate most common violations
    const violationCounts: Record<string, number> = {};
    filteredData.forEach(entry => {
      Object.entries(entry.equipment).forEach(([equipment, isPresent]) => {
        if (!isPresent) {
          violationCounts[equipment] = (violationCounts[equipment] || 0) + 1;
        }
      });
    });

    const mostCommonViolations = Object.entries(violationCounts)
      .map(([equipment, count]) => ({ equipment, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);

    // Calculate room statistics
    const roomStatsMap: Record<string, { entries: number; compliant: number }> = {};
    filteredData.forEach(entry => {
      if (!roomStatsMap[entry.room_name]) {
        roomStatsMap[entry.room_name] = { entries: 0, compliant: 0 };
      }
      roomStatsMap[entry.room_name].entries++;
      if (entry.is_compliant) {
        roomStatsMap[entry.room_name].compliant++;
      }
    });

    const roomStats = Object.entries(roomStatsMap).map(([room, stats]) => ({
      room,
      entries: stats.entries,
      complianceRate: (stats.compliant / stats.entries) * 100
    }));

    // Calculate hourly statistics
    const hourlyStatsMap: Record<number, { entries: number; compliant: number }> = {};
    filteredData.forEach(entry => {
      const hour = new Date(entry.entered_at).getHours();
      if (!hourlyStatsMap[hour]) {
        hourlyStatsMap[hour] = { entries: 0, compliant: 0 };
      }
      hourlyStatsMap[hour].entries++;
      if (entry.is_compliant) {
        hourlyStatsMap[hour].compliant++;
      }
    });

    const hourlyStats = Object.entries(hourlyStatsMap).map(([hour, stats]) => ({
      hour: parseInt(hour),
      entries: stats.entries,
      complianceRate: (stats.compliant / stats.entries) * 100
    })).sort((a, b) => a.hour - b.hour);

    return {
      totalEntries,
      compliantEntries,
      nonCompliantEntries,
      complianceRate,
      mostCommonViolations,
      roomStats,
      hourlyStats
    };
  }, [filteredData]);

  const uniqueRooms = useMemo(() => {
    return Array.from(new Set(factoryEntries.map(entry => entry.room_name))).sort();
  }, [factoryEntries]);

  const handleViewCompliance = (entry: FactoryEntries) => {
    setSelectedEntry(entry);
  };

  const exportData = () => {
    const csvContent = [
      ["ID", "User ID", "Room", "Entered At", "Compliant", "Equipment Status"].join(","),
      ...filteredData.map(entry => [
        entry.id,
        entry.user_id,
        entry.room_name,
        entry.entered_at,
        entry.is_compliant ? "Yes" : "No",
        Object.entries(entry.equipment).map(([key, value]) => `${key}:${value}`).join(";")
      ].join(","))
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `compliance-report-${format(new Date(), "yyyy-MM-dd")}.csv`;
    link.click();
    window.URL.revokeObjectURL(url);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p>Loading reports...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-2 justify-end">
        <Button onClick={exportData} variant="outline" size="sm">
          <Download className="h-4 w-4 mr-2" />
          Export CSV
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <CalendarIcon className="h-4 w-4" />
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline" className="w-64 justify-start text-left font-normal">
                    {dateRange?.from ? (
                      dateRange.to ? (
                        <>
                          {format(dateRange.from, "dd/MM/yyyy", { locale: pt })} -{" "}
                          {format(dateRange.to, "dd/MM/yyyy", { locale: pt })}
                        </>
                      ) : (
                        format(dateRange.from, "dd/MM/yyyy", { locale: pt })
                      )
                    ) : (
                      <span>Select date range</span>
                    )}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <Calendar
                    initialFocus
                    mode="range"
                    defaultMonth={dateRange?.from}
                    selected={dateRange}
                    onSelect={setDateRange}
                    numberOfMonths={2}
                  />
                </PopoverContent>
              </Popover>
            </div>
            
            <div className="flex items-center gap-2">
              <Building className="h-4 w-4" />
              <Select value={selectedRoom} onValueChange={setSelectedRoom}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Select room" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Rooms</SelectItem>
                  {uniqueRooms.map(room => (
                    <SelectItem key={room} value={room}>{room}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Entries</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{complianceStats.totalEntries}</div>
            <p className="text-xs text-muted-foreground">
              {dateRange ? "In selected period" : "All time"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Compliance Rate</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{complianceStats.complianceRate.toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">
              {complianceStats.compliantEntries} of {complianceStats.totalEntries} entries
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Compliant Entries</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{complianceStats.compliantEntries}</div>
            <p className="text-xs text-muted-foreground">
              Fully compliant entries
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Non-Compliant</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{complianceStats.nonCompliantEntries}</div>
            <p className="text-xs text-muted-foreground">
              Missing equipment
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Analytics */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="violations">Violations</TabsTrigger>
          <TabsTrigger value="rooms">Room Analysis</TabsTrigger>
          <TabsTrigger value="timeline">Timeline</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Compliance Trend
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Overall Compliance</span>
                    <Badge variant={complianceStats.complianceRate >= 80 ? "default" : "destructive"}>
                      {complianceStats.complianceRate.toFixed(1)}%
                    </Badge>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-primary h-2 rounded-full transition-all duration-300"
                      style={{ width: `${complianceStats.complianceRate}%` }}
                    />
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Target: 95% compliance rate
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  Peak Hours
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {complianceStats.hourlyStats
                    .sort((a, b) => b.entries - a.entries)
                    .slice(0, 5)
                    .map(({ hour, entries, complianceRate }) => (
                      <div key={hour} className="flex items-center justify-between">
                        <span className="text-sm">{hour}:00 - {hour + 1}:00</span>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-muted-foreground">{entries} entries</span>
                          <Badge variant="outline" className="text-xs">
                            {complianceRate.toFixed(0)}%
                          </Badge>
                        </div>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="violations" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Most Common Violations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {complianceStats.mostCommonViolations.length > 0 ? (
                  complianceStats.mostCommonViolations.map(({ equipment, count }) => (
                    <div key={equipment} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <AlertTriangle className="h-4 w-4 text-red-600" />
                        <span className="font-medium">
                          {equipmentLabels[equipment] || equipment}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="destructive">{count}</Badge>
                        <span className="text-sm text-muted-foreground">
                          {((count / complianceStats.totalEntries) * 100).toFixed(1)}% of entries
                        </span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-600" />
                    <p>No violations found in the selected period!</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="rooms" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building className="h-5 w-5" />
                Room Performance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {complianceStats.roomStats
                  .sort((a, b) => b.complianceRate - a.complianceRate)
                  .map(({ room, entries, complianceRate }) => (
                    <div key={room} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <Building className="h-4 w-4 text-blue-600" />
                        <span className="font-medium">{room}</span>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="text-sm text-muted-foreground">{entries} entries</span>
                        <Badge 
                          variant={complianceRate >= 80 ? "default" : "destructive"}
                        >
                          {complianceRate.toFixed(1)}%
                        </Badge>
                      </div>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="timeline" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Hourly Compliance Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-6 gap-2">
                {Array.from({ length: 24 }, (_, hour) => {
                  const hourData = complianceStats.hourlyStats.find(h => h.hour === hour);
                  const entries = hourData?.entries || 0;
                  const complianceRate = hourData?.complianceRate || 0;
                  
                  return (
                    <div key={hour} className="text-center p-2 border rounded">
                      <div className="text-xs font-medium">{hour}:00</div>
                      <div className="text-xs text-muted-foreground">{entries}</div>
                      <div className={`text-xs font-medium ${
                        complianceRate >= 80 ? "text-green-600" : 
                        complianceRate >= 60 ? "text-yellow-600" : "text-red-600"
                      }`}>
                        {entries > 0 ? `${complianceRate.toFixed(0)}%` : "-"}
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Compliance Dialog */}
      {selectedEntry && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Compliance Details</span>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => setSelectedEntry(null)}
                >
                  Close
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Room</p>
                    <p className="text-lg font-semibold">{selectedEntry.room_name}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Status</p>
                    <Badge 
                      variant={selectedEntry.is_compliant ? "default" : "destructive"}
                      className="text-sm"
                    >
                      {selectedEntry.is_compliant ? "Compliant" : "Non-Compliant"}
                    </Badge>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Entry Time</p>
                    <p className="text-sm">{format(new Date(selectedEntry.entered_at), "PPpp")}</p>
                  </div>
                </div>

                {selectedEntry.image_url && (
                  <div>
                    <p className="text-sm font-medium text-muted-foreground mb-2">Captured Image</p>
                    <img
                      src={selectedEntry.image_url}
                      alt="Equipment compliance check"
                      className="max-w-full h-auto rounded-lg border"
                    />
                  </div>
                )}

                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-2">Equipment Status</p>
                  <div className="space-y-2">
                    {Object.entries(selectedEntry.equipment).map(([key, isPresent]) => {
                      const label = equipmentLabels[key] || key;
                      
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
                                <AlertTriangle className="h-4 w-4 text-red-600" />
                                <span className="text-sm text-red-700">Missing</span>
                              </>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};
