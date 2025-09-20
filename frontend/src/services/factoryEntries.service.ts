import axiosInstance from "@/lib/axiosClient";

type FactoryEntries = {
  room_name: string;
  equipment: Record<string, boolean>;
  image_url: string;
  id: number;
  user_id: number;
  entered_at: Date;
  created_at: Date;
  is_compliant: boolean;
  missing_equipment: string[];
};

export const GetFactoryEntries = async () => {
  const { data } = await axiosInstance<FactoryEntries[]>("/entries");
  return data;
};
