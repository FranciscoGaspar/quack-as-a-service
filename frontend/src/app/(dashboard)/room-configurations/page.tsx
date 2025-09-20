'use client';

import { useState } from 'react';
import { PageHeader } from "@/components/PageHeader";
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { RoomConfigurationsTable } from '@/components/room-configurations/RoomConfigurationsTable';
import { CreateRoomConfigDialog } from '@/components/room-configurations/CreateRoomConfigDialog';
import { useRoomConfigurationsAnalytics, useCreateDefaultConfigurations } from '@/hooks/room-configurations/useRoomConfigurations';
import { Plus, RefreshCw, BarChart3, Shield, Settings } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const RoomConfigurationsPage = () => {
  const [includeInactive, setIncludeInactive] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const { data: analytics, isLoading: analyticsLoading } = useRoomConfigurationsAnalytics();
  const createDefaults = useCreateDefaultConfigurations();
  const { toast } = useToast();

  const handleCreateDefaults = async () => {
    try {
      const result = await createDefaults.mutateAsync();
      toast({
        title: "Default Configurations Created",
        description: `Created ${result.configurations?.length || 0} default room configurations.`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create default configurations.",
        variant: "destructive",
      });
    }
  };

  const handleNewConfiguration = () => {
    setShowCreateDialog(true);
  };

  const handleCreateConfiguration = async (config: any) => {
    try {
      // TODO: Implement API call for creating configuration
      toast({
        title: "Configuration Created",
        description: `Room configuration for "${config.room_name}" has been created.`,
      });
      setShowCreateDialog(false);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create room configuration.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="flex flex-1 flex-col h-full">
      <div className="flex justify-between items-start mb-6">
        <PageHeader
          description="Manage room equipment configurations and entry thresholds"
          title="Room Configurations"
        />
        <div className="flex items-center gap-2">
          <Button 
            variant="outline"
            onClick={handleCreateDefaults}
            disabled={createDefaults.isPending}
          >
            {createDefaults.isPending ? (
              <RefreshCw className="w-4 h-4 animate-spin mr-2" />
            ) : (
              <Shield className="w-4 h-4 mr-2" />
            )}
            Create Defaults
          </Button>
          <Button variant="default" onClick={handleNewConfiguration}>
            <Plus className="w-4 h-4 mr-2" />
            New Configuration
          </Button>
        </div>
      </div>

      {/* Analytics Cards */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Configurations</CardTitle>
              <Settings className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{analytics.total_configurations}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Configurations</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{analytics.active_configurations}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Inactive Configurations</CardTitle>
              <Settings className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-500">{analytics.inactive_configurations}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Average Approval Rate</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {analytics.rooms.length > 0 
                  ? Math.round(analytics.rooms.reduce((acc, room) => acc + room.approval_rate, 0) / analytics.rooms.length)
                  : 0}%
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Room Analytics */}
      {analytics?.rooms && analytics.rooms.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Room Performance Overview
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analytics.rooms.map((room) => (
                <div key={room.room_name} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-semibold capitalize">
                      {room.room_name.replace('-', ' ')}
                    </h4>
                    <div className="text-right">
                      <div className="text-sm text-gray-500">Approval Rate</div>
                      <div className="text-lg font-bold text-green-600">
                        {room.approval_rate.toFixed(1)}%
                      </div>
                    </div>
                  </div>
                  <div className="grid grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="text-gray-500">Total Entries</div>
                      <div className="font-semibold">{room.total_entries}</div>
                    </div>
                    <div>
                      <div className="text-gray-500">Approved</div>
                      <div className="font-semibold text-green-600">{room.approved_entries}</div>
                    </div>
                    <div>
                      <div className="text-gray-500">Denied</div>
                      <div className="font-semibold text-red-600">{room.denied_entries}</div>
                    </div>
                    <div>
                      <div className="text-gray-500">Pending</div>
                      <div className="font-semibold text-yellow-600">{room.pending_entries}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Controls */}
      <div className="flex items-center gap-4 mb-4">
        <div className="flex items-center space-x-2">
          <Switch
            id="include-inactive"
            checked={includeInactive}
            onCheckedChange={setIncludeInactive}
          />
          <label 
            htmlFor="include-inactive"
            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
          >
            Include inactive configurations
          </label>
        </div>
      </div>

      {/* Configurations Table */}
      <div className="flex-1">
        <RoomConfigurationsTable includeInactive={includeInactive} />
      </div>

      {/* Create Configuration Dialog */}
      <CreateRoomConfigDialog
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
        onSubmit={handleCreateConfiguration}
      />
    </div>
  );
};

export default RoomConfigurationsPage;


