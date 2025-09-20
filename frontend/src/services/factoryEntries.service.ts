import axiosInstance from "@/lib/axiosClient";

export type FactoryEntries = {
  room_name: string;
  equipment: Record<string, boolean>;
  image_url: string;
  id: number;
  user_id: number;
  entered_at: string;
  created_at: string;
  is_compliant: boolean;
  missing_equipment: string[];
};

export const GetFactoryEntries = async () => {
  const { data } = await axiosInstance<FactoryEntries[]>("/entries");
  return data;
};

export const DeleteFactoryEntry = async (id: number) => {
  await axiosInstance(`/entries/${id}`, { method: "DELETE" });
};
