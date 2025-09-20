import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getRoomConfigurations,
  getRoomConfiguration,
  createRoomConfiguration,
  updateRoomConfiguration,
  deleteRoomConfiguration,
  getRoomConfigurationsAnalytics,
  testRoomConfiguration,
  recalculateEntriesForRoom,
  createDefaultConfigurations,
  type RoomEquipmentConfigurationCreate,
  type RoomEquipmentConfigurationUpdate,
} from "@/services/roomConfigurations.service";

// Query keys
const ROOM_CONFIGS_KEY = "room-configurations";
const ROOM_CONFIG_KEY = "room-configuration";
const ROOM_CONFIG_ANALYTICS_KEY = "room-configurations-analytics";

// Get all room configurations
export const useRoomConfigurations = (includeInactive = false) => {
  return useQuery({
    queryKey: [ROOM_CONFIGS_KEY, includeInactive],
    queryFn: async () => {
      const configs = await getRoomConfigurations(includeInactive);

      // Sort rooms to match sidebar menu order: production-floor, assembly-line, packaging-area
      const roomOrder = ["production-floor", "assembly-line", "packaging-area"];

      return configs.sort((a, b) => {
        const indexA = roomOrder.indexOf(a.room_name);
        const indexB = roomOrder.indexOf(b.room_name);

        // If both rooms are in our predefined order, sort by that order
        if (indexA !== -1 && indexB !== -1) {
          return indexA - indexB;
        }

        // If only one is in the predefined order, put it first
        if (indexA !== -1) return -1;
        if (indexB !== -1) return 1;

        // If neither is in predefined order, sort alphabetically
        return a.room_name.localeCompare(b.room_name);
      });
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Get single room configuration
export const useRoomConfiguration = (id: number) => {
  return useQuery({
    queryKey: [ROOM_CONFIG_KEY, id],
    queryFn: () => getRoomConfiguration(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
};

// Get room configurations analytics
export const useRoomConfigurationsAnalytics = () => {
  return useQuery({
    queryKey: [ROOM_CONFIG_ANALYTICS_KEY],
    queryFn: async () => {
      const analytics = await getRoomConfigurationsAnalytics();

      // Sort room analytics to match sidebar menu order: production-floor, assembly-line, packaging-area
      const roomOrder = ["production-floor", "assembly-line", "packaging-area"];

      const sortedRooms = analytics.rooms.sort((a, b) => {
        const indexA = roomOrder.indexOf(a.room_name);
        const indexB = roomOrder.indexOf(b.room_name);

        // If both rooms are in our predefined order, sort by that order
        if (indexA !== -1 && indexB !== -1) {
          return indexA - indexB;
        }

        // If only one is in the predefined order, put it first
        if (indexA !== -1) return -1;
        if (indexB !== -1) return 1;

        // If neither is in predefined order, sort alphabetically
        return a.room_name.localeCompare(b.room_name);
      });

      return {
        ...analytics,
        rooms: sortedRooms,
      };
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

// Create room configuration
export const useCreateRoomConfiguration = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (config: RoomEquipmentConfigurationCreate) =>
      createRoomConfiguration(config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [ROOM_CONFIGS_KEY] });
      queryClient.invalidateQueries({ queryKey: [ROOM_CONFIG_ANALYTICS_KEY] });
    },
  });
};

// Update room configuration
export const useUpdateRoomConfiguration = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      config,
    }: {
      id: number;
      config: RoomEquipmentConfigurationUpdate;
    }) => updateRoomConfiguration(id, config),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: [ROOM_CONFIGS_KEY] });
      queryClient.invalidateQueries({ queryKey: [ROOM_CONFIG_KEY, id] });
      queryClient.invalidateQueries({ queryKey: [ROOM_CONFIG_ANALYTICS_KEY] });
    },
  });
};

// Delete room configuration
export const useDeleteRoomConfiguration = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => deleteRoomConfiguration(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [ROOM_CONFIGS_KEY] });
      queryClient.invalidateQueries({ queryKey: [ROOM_CONFIG_ANALYTICS_KEY] });
    },
  });
};

// Test room configuration
export const useTestRoomConfiguration = () => {
  return useMutation({
    mutationFn: ({
      id,
      testEquipment,
    }: {
      id: number;
      testEquipment: Record<string, boolean>;
    }) => testRoomConfiguration(id, testEquipment),
  });
};

// Recalculate entries for room
export const useRecalculateEntriesForRoom = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => recalculateEntriesForRoom(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["factory-entries"] });
      queryClient.invalidateQueries({ queryKey: [ROOM_CONFIG_ANALYTICS_KEY] });
    },
  });
};

// Create default configurations
export const useCreateDefaultConfigurations = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createDefaultConfigurations,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [ROOM_CONFIGS_KEY] });
      queryClient.invalidateQueries({ queryKey: [ROOM_CONFIG_ANALYTICS_KEY] });
    },
  });
};
