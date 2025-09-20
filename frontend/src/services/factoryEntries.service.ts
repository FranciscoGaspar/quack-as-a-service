import axiosInstance from "@/lib/axiosClient";

export type FactoryEntries = {
  room_name: string;
  equipment: Record<string, boolean>;
  image_url: string;
  id: string;
  user_id: string;
  entered_at: Date;
  created_at: Date;
  is_compliant: boolean;
  missing_equipment: string[];
};

export const GetFactoryEntries = async () => {
  const { data } = await axiosInstance<FactoryEntries[]>("/entries");
  return data;
};

export const DeleteFactoryEntry = async (id: string) => {
  await axiosInstance(`/entries/${id}`, { method: "DELETE" });
};
