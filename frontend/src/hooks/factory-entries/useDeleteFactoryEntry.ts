import { KEYS } from "@/constants/queryKeys";
import { getQueryClient } from "@/lib/getQueryClient";
import { DeleteFactoryEntry } from "@/services/factoryEntries.service";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";

export const useDeleteFactoryEntry = (id: string) => {
  const queryClient = getQueryClient();
  const toastID = `delete-factoryEntry-${id}`;

  return useMutation({
    mutationFn: () => {
      toast.loading("Deleting factory entry...", { id: toastID });
      return DeleteFactoryEntry(id);
    },
    onSuccess: () => {
      toast.success("Factory entry deleted", { id: toastID });
      queryClient.invalidateQueries({ queryKey: KEYS.factoryEntries });
    },
    onError: () => {
      toast.error("Failed to delete factory entry", { id: toastID });
    },
  });
};
