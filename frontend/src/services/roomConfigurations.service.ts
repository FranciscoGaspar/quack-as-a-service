import axiosInstance from "@/lib/axiosClient";

export type RoomEquipmentConfiguration = {
  id: number;
  room_name: string;
  equipment_weights: Record<string, number>;
  entry_threshold: number;
  is_active: boolean;
  description: string | null;
  created_at: string;
  updated_at: string;
};

export type RoomEquipmentConfigurationCreate = {
  room_name: string;
  equipment_weights: Record<string, number>;
  entry_threshold: number;
  description?: string | null;
  is_active?: boolean;
};

export type RoomEquipmentConfigurationUpdate = {
  equipment_weights?: Record<string, number>;
  entry_threshold?: number;
  description?: string | null;
  is_active?: boolean;
};

export type RoomAnalytics = {
  total_configurations: number;
  active_configurations: number;
  inactive_configurations: number;
  rooms: Array<{
    room_name: string;
    is_active: boolean;
    entry_threshold: number;
    equipment_weights: Record<string, number>;
    total_entries: number;
    approved_entries: number;
    denied_entries: number;
    pending_entries: number;
    approval_rate: number;
  }>;
};

// Get all room configurations
export const getRoomConfigurations = async (
  includeInactive = false
): Promise<RoomEquipmentConfiguration[]> => {
  const { data } = await axiosInstance<RoomEquipmentConfiguration[]>(
    "/room-configurations",
    {
      params: { include_inactive: includeInactive },
    }
  );
  return data;
};

// Get single room configuration
export const getRoomConfiguration = async (
  id: number
): Promise<RoomEquipmentConfiguration> => {
  const { data } = await axiosInstance<RoomEquipmentConfiguration>(
    `/room-configurations/${id}`
  );
  return data;
};

// Get room configuration by room name
export const getRoomConfigurationByName = async (
  roomName: string
): Promise<RoomEquipmentConfiguration> => {
  const { data } = await axiosInstance<RoomEquipmentConfiguration>(
    `/room-configurations/by-room/${roomName}`
  );
  return data;
};

// Create room configuration
export const createRoomConfiguration = async (
  config: RoomEquipmentConfigurationCreate
): Promise<RoomEquipmentConfiguration> => {
  const { data } = await axiosInstance<RoomEquipmentConfiguration>(
    "/room-configurations",
    {
      method: "POST",
      data: config,
    }
  );
  return data;
};

// Update room configuration
export const updateRoomConfiguration = async (
  id: number,
  config: RoomEquipmentConfigurationUpdate
): Promise<RoomEquipmentConfiguration> => {
  const { data } = await axiosInstance<RoomEquipmentConfiguration>(
    `/room-configurations/${id}`,
    {
      method: "PUT",
      data: config,
    }
  );
  return data;
};

// Delete room configuration
export const deleteRoomConfiguration = async (id: number): Promise<void> => {
  await axiosInstance(`/room-configurations/${id}`, {
    method: "DELETE",
  });
};

// Create default configurations
export const createDefaultConfigurations = async () => {
  const { data } = await axiosInstance("/room-configurations/create-defaults", {
    method: "POST",
  });
  return data;
};

// Test configuration
export const testRoomConfiguration = async (
  id: number,
  testEquipment: Record<string, boolean>
) => {
  const { data } = await axiosInstance(`/room-configurations/${id}/test`, {
    method: "POST",
    data: testEquipment,
  });
  return data;
};

// Recalculate entries for room
export const recalculateEntriesForRoom = async (id: number) => {
  const { data } = await axiosInstance(
    `/room-configurations/${id}/recalculate-entries`,
    {
      method: "POST",
    }
  );
  return data;
};

// Get room configurations analytics
export const getRoomConfigurationsAnalytics =
  async (): Promise<RoomAnalytics> => {
    const { data } = await axiosInstance<RoomAnalytics>(
      "/room-configurations/analytics/summary"
    );
    return data;
  };


