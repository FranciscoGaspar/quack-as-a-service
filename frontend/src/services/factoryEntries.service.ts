import axiosInstance from "@/lib/axiosClient";

export type FactoryEntries = {
  room_name: string;
  equipment: Record<string, boolean>;
  image_url: string;
  id: number;
  user_id: number;
  user_name: string;
  entered_at: string;
  created_at: string;
  is_compliant: boolean;
  // New approval fields
  is_approved: boolean | null; // true=approved, false=denied, null=pending
  equipment_score: number | null; // 0-100 compliance score
  approval_reason: string | null; // reason for approval/denial
  missing_equipment: string[]; // list of missing equipment
};

export const GetFactoryEntries = async () => {
  const { data } = await axiosInstance<FactoryEntries[]>("/entries");
  return data;
};

export const DeleteFactoryEntry = async (id: number) => {
  await axiosInstance(`/entries/${id}`, { method: "DELETE" });
};

export const SendUserQR = async (formData: FormData) => {
  const { data } = await axiosInstance("/users/detect", {
    method: "POST",
    data: formData,
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return data;
};

export const SendUserEPI = async (formData: FormData) => {
  const { data } = await axiosInstance("/entries/upload-image", {
    method: "POST",
    data: formData,
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return data;
};
