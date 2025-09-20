'use client';

import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { useRoomConfigurations } from '@/hooks/room-configurations/useRoomConfigurations';
import { Settings } from 'lucide-react';

interface RoomConfigurationsTableProps {
  includeInactive?: boolean;
}

export const RoomConfigurationsTable = ({ includeInactive = false }: RoomConfigurationsTableProps) => {
  const { data: configurations, isLoading, error } = useRoomConfigurations(includeInactive);


  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-4 bg-gray-300 rounded w-1/4"></div>
            </CardHeader>
            <CardContent>
              <div className="h-20 bg-gray-200 rounded"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center text-red-600">
            Error loading room configurations: {error.message}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!configurations || configurations.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center text-gray-500">
            No room configurations found. Create some configurations to get started.
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {configurations.map((config) => (
        <Card key={config.id} className="relative">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="w-5 h-5" />
              <span className="capitalize">
                {config.room_name.replace('-', ' ')}
              </span>
              <Badge variant={config.is_active ? "default" : "secondary"}>
                {config.is_active ? "Active" : "Inactive"}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Entry Policy */}
              <div>
                <h4 className="font-semibold mb-2">Entry Policy</h4>
                <div className="flex items-center gap-2">
                  <div className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                    {Object.values(config.equipment_weights).some(level => level === "required") ? "REQUIRED ITEMS MUST BE PRESENT" : "ALL ITEMS RECOMMENDED ONLY"}
                  </div>
                </div>
              </div>

              {/* Equipment Requirements */}
              <div>
                <h4 className="font-semibold mb-2">Equipment Requirements</h4>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(config.equipment_weights).map(([equipment, level]) => (

  
                    <Badge 
                      key={equipment} 
                      variant={level === "required" ? "destructive" : "secondary"} 
                      className="capitalize"
                    >
                      {equipment.replace('_', ' ')}: {level}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>

            {config.description && (
              <>
                <Separator className="my-4" />
                <p className="text-sm text-gray-600">{config.description}</p>
              </>
            )}

            <Separator className="my-4" />
            <div className="flex justify-between text-xs text-gray-500">
              <span>Created: {config.created_at ? new Date(config.created_at).toLocaleDateString() : 'Not set'}</span>
              <span>Updated: {config.updated_at ? new Date(config.updated_at).toLocaleDateString() : 'Not set'}</span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};


