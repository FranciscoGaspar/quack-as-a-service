import { SendUserQR } from "@/services/factoryEntries.service";
import { useMutation } from "@tanstack/react-query";

export const useSendQR = () => {
  return useMutation({
    mutationFn: (data: FormData) => SendUserQR(data),
  });
};
