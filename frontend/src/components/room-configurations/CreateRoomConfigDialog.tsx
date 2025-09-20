'use client';

import { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Slider } from '@/components/ui/slider';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Plus, Minus, Settings } from 'lucide-react';

interface CreateRoomConfigDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (config: any) => void;
  isLoading?: boolean;
}

const EQUIPMENT_OPTIONS = [
  { key: 'mask', label: 'Face Mask' },
  { key: 'gloves', label: 'Gloves' },
  { key: 'hairnet', label: 'Hair Net' },
  { key: 'safety_glasses', label: 'Safety Glasses' },
  { key: 'hard_hat', label: 'Hard Hat' },
  { key: 'safety_vest', label: 'Safety Vest' },
  { key: 'boots', label: 'Safety Boots' },
];

export const CreateRoomConfigDialog = ({ 
  open, 
  onOpenChange, 
  onSubmit, 
  isLoading = false 
}: CreateRoomConfigDialogProps) => {
  const [roomName, setRoomName] = useState('');
  const [description, setDescription] = useState('');
  const [entryThreshold, setEntryThreshold] = useState([7]);
  const [equipmentWeights, setEquipmentWeights] = useState<Record<string, number>>({});

  const handleReset = () => {
    setRoomName('');
    setDescription('');
    setEntryThreshold([7]);
    setEquipmentWeights({});
  };

  const handleSubmit = () => {
    const config = {
      room_name: roomName.toLowerCase().replace(/\s+/g, '-'),
      description: description,
      entry_threshold: entryThreshold[0],
      equipment_weights: equipmentWeights,
    };
    
    onSubmit(config);
    handleReset();
  };

  const addEquipment = (equipmentKey: string) => {
    setEquipmentWeights(prev => ({
      ...prev,
      [equipmentKey]: 5 // Default weight of 5
    }));
  };

  const removeEquipment = (equipmentKey: string) => {
    setEquipmentWeights(prev => {
      const { [equipmentKey]: removed, ...rest } = prev;
      return rest;
    });
  };

  const updateEquipmentWeight = (equipmentKey: string, weight: number) => {
    setEquipmentWeights(prev => ({
      ...prev,
      [equipmentKey]: weight
    }));
  };

  const getTotalWeight = () => {
    return Object.values(equipmentWeights).reduce((sum, weight) => sum + weight, 0);
  };

  const isValid = roomName.trim() && Object.keys(equipmentWeights).length > 0;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Create Room Configuration
          </DialogTitle>
          <DialogDescription>
            Define equipment requirements and entry thresholds for a new room.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-6">
          {/* Basic Info */}
          <div className="space-y-4">
            <div>
              <Label htmlFor="room-name">Room Name *</Label>
              <Input
                id="room-name"
                placeholder="e.g., Quality Control Lab"
                value={roomName}
                onChange={(e) => setRoomName(e.target.value)}
              />
            </div>
            
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                placeholder="Brief description of safety requirements..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={2}
              />
            </div>
          </div>

          {/* Entry Threshold */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Entry Threshold</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <Label>Minimum Score Required: {entryThreshold[0]}/10</Label>
                  <Slider
                    value={entryThreshold}
                    onValueChange={setEntryThreshold}
                    max={10}
                    min={1}
                    step={0.5}
                    className="mt-2"
                  />
                </div>
                <p className="text-sm text-gray-600">
                  Workers must achieve this score or higher to enter the room.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Equipment Requirements */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Equipment Requirements</CardTitle>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">
                  Total Weight: {getTotalWeight()}/10
                </span>
                {getTotalWeight() > 10 && (
                  <Badge variant="destructive" className="text-xs">
                    Over Limit
                  </Badge>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Add Equipment */}
                <div>
                  <Label>Add Equipment</Label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {EQUIPMENT_OPTIONS.filter(eq => !equipmentWeights[eq.key]).map(equipment => (
                      <Button
                        key={equipment.key}
                        variant="outline"
                        size="sm"
                        onClick={() => addEquipment(equipment.key)}
                      >
                        <Plus className="w-3 h-3 mr-1" />
                        {equipment.label}
                      </Button>
                    ))}
                  </div>
                </div>

                {/* Current Equipment */}
                {Object.keys(equipmentWeights).length > 0 && (
                  <div className="space-y-3">
                    <Label>Equipment Weights</Label>
                    {Object.entries(equipmentWeights).map(([key, weight]) => {
                      const equipment = EQUIPMENT_OPTIONS.find(eq => eq.key === key);
                      return (
                        <div key={key} className="flex items-center gap-3 p-3 border rounded-lg">
                          <div className="flex-1">
                            <div className="flex items-center justify-between mb-2">
                              <span className="font-medium">{equipment?.label || key}</span>
                              <div className="flex items-center gap-2">
                                <span className="text-sm">{weight}/10</span>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => removeEquipment(key)}
                                >
                                  <Minus className="w-3 h-3" />
                                </Button>
                              </div>
                            </div>
                            <Slider
                              value={[weight]}
                              onValueChange={([value]) => updateEquipmentWeight(key, value)}
                              max={10}
                              min={1}
                              step={0.5}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}

                {Object.keys(equipmentWeights).length === 0 && (
                  <p className="text-sm text-gray-500 text-center py-4">
                    No equipment requirements added yet.
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button 
            onClick={handleSubmit} 
            disabled={!isValid || isLoading || getTotalWeight() > 10}
          >
            {isLoading ? 'Creating...' : 'Create Configuration'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
