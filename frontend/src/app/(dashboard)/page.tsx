"use client";

import { AIStatusIndicator } from "@/components/ai-reports/AIReportComponents";
import { PageHeader } from "@/components/PageHeader";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ROUTES } from "@/constants/routes";
import { useQuickInsights } from "@/hooks/ai-analytics/useAIAnalytics";
import { useFactoryEntries } from "@/hooks/factory-entries/useFactoryEntries";
import { format, isWithinInterval, subDays } from "date-fns";
import {
  Activity,
  BarChart3,
  Brain,
  Calendar,
  Clock,
  RefreshCw,
  Shield,
  Users,
  Zap
} from "lucide-react";
import Link from "next/link";
import { useMemo } from "react";


const HomePage = () => {
  const { data: entries, isLoading: entriesLoading, refetch: refetchEntries } = useFactoryEntries();
  const { data: aiInsights, isLoading: aiLoading, refetch: refetchAI } = useQuickInsights();

  // Calculate key metrics
  const metrics = useMemo(() => {
    if (!entries) return null;

    const totalEntries = entries.length;
    const compliantEntries = entries.filter(entry => entry.is_compliant).length;
    const complianceRate = totalEntries > 0 ? (compliantEntries / totalEntries) * 100 : 0;

    // Today's entries
    const today = new Date();
    const todayEntries = entries.filter(entry => 
      format(new Date(entry.entered_at), 'yyyy-MM-dd') === format(today, 'yyyy-MM-dd')
    );

    // Last 7 days entries
    const lastWeekEntries = entries.filter(entry => 
      isWithinInterval(new Date(entry.entered_at), {
        start: subDays(today, 7),
        end: today
      })
    );

    // Room performance
    const roomStats = entries.reduce((acc, entry) => {
      if (!acc[entry.room_name]) {
        acc[entry.room_name] = { total: 0, compliant: 0 };
      }
      acc[entry.room_name].total++;
      if (entry.is_compliant) {
        acc[entry.room_name].compliant++;
      }
      return acc;
    }, {} as Record<string, { total: number; compliant: number }>);

    const roomPerformance = Object.entries(roomStats).map(([room, stats]) => ({
      room,
      complianceRate: stats.total > 0 ? (stats.compliant / stats.total) * 100 : 0,
      total: stats.total,
      compliant: stats.compliant
    })).sort((a, b) => b.complianceRate - a.complianceRate);

    // Equipment violations
    const equipmentStats = entries.reduce((acc, entry) => {
      Object.entries(entry.equipment).forEach(([equipment, isPresent]) => {
        if (!acc[equipment]) {
          acc[equipment] = { total: 0, violations: 0 };
        }
        acc[equipment].total++;
        if (!isPresent) {
          acc[equipment].violations++;
        }
      });
      return acc;
    }, {} as Record<string, { total: number; violations: number }>);

    const equipmentViolations = Object.entries(equipmentStats).map(([equipment, stats]) => ({
      equipment,
      violationRate: stats.total > 0 ? (stats.violations / stats.total) * 100 : 0,
      violations: stats.violations,
      total: stats.total
    })).sort((a, b) => b.violationRate - a.violationRate);

    return {
      totalEntries,
      compliantEntries,
      complianceRate,
      todayEntries: todayEntries.length,
      lastWeekEntries: lastWeekEntries.length,
      roomPerformance,
      equipmentViolations
    };
  }, [entries]);

  const handleRefresh = () => {
    refetchEntries();
    refetchAI();
  };

  const getComplianceColor = (rate: number) => {
    if (rate >= 90) return "text-green-600";
    if (rate >= 70) return "text-yellow-600";
    return "text-red-600";
  };

  const getComplianceBadgeVariant = (rate: number) => {
    if (rate >= 90) return "default";
    if (rate >= 70) return "secondary";
    return "destructive";
  };

  return (
    <div className="flex flex-1 flex-col h-full">
      <PageHeader
        description="Your Quack-as-a-Service Dashboard"
        title="Dashboard"
      />
      
      <div className="flex-1 p-6 space-y-6 overflow-y-auto">
        {/* Header Actions */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <AIStatusIndicator />
          </div>
          <Button onClick={handleRefresh} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh Data
          </Button>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {/* Total Entries */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Entries</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics?.totalEntries || 0}</div>
              <p className="text-xs text-muted-foreground">
                {metrics?.todayEntries || 0} today
              </p>
            </CardContent>
          </Card>

          {/* Compliance Rate */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Compliance Rate</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${getComplianceColor(metrics?.complianceRate || 0)}`}>
                {(metrics?.complianceRate || 0).toFixed(1)}%
              </div>
              <p className="text-xs text-muted-foreground">
                {metrics?.compliantEntries || 0} compliant entries
              </p>
            </CardContent>
          </Card>

          {/* This Week */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">This Week</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics?.lastWeekEntries || 0}</div>
              <p className="text-xs text-muted-foreground">
                entries in last 7 days
              </p>
            </CardContent>
          </Card>

          {/* AI Status */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">AI Analytics</CardTitle>
              <Brain className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Badge variant={aiInsights?.status === 'success' ? 'default' : 'secondary'}>
                  {aiInsights?.status === 'success' ? 'Active' : 'Inactive'}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Powered by AWS Bedrock
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Grid */}
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Left Column - Recent Activity (2/3 width) */}
          <div className="lg:col-span-2 space-y-6">
            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5 text-purple-600" />
                  Recent Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {entries?.slice(0, 10).map((entry, index) => (
                    <div key={entry.id} className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full ${
                        entry.is_compliant ? 'bg-green-500' : 'bg-red-500'
                      }`} />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">
                          {entry.room_name}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {format(new Date(entry.entered_at), 'MMM dd, HH:mm')}
                        </p>
                      </div>
                      <Badge variant={entry.is_compliant ? 'default' : 'destructive'} className="text-xs">
                        {entry.is_compliant ? 'Compliant' : 'Violation'}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
          {/* Right Column - Quick Actions (1/3 width) */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5 text-yellow-600" />
                  Quick Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button className="w-full justify-start" variant="outline" asChild> 
                  <Link href={ROUTES.reports}>
                    <BarChart3 className="h-4 w-4 mr-2" />
                    View Detailed Reports
                  </Link>
                </Button>
                <Button className="w-full justify-start" variant="outline" asChild>
                  <Link href={ROUTES.aiChat}>
                    <Brain className="h-4 w-4 mr-2" />
                    Ask AI Questions
                  </Link>
                </Button>
                <Button className="w-full justify-start" variant="outline" asChild>
                  <Link href={ROUTES.factoryEntries}>
                    <Users className="h-4 w-4 mr-2" />
                    Manage Entries
                  </Link>
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
