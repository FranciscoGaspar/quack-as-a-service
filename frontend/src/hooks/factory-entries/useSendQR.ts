import { getQueryClient } from '@/lib/getQueryClient';
import { SendUserQR } from '@/services/factoryEntries.service';
import { useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';

export const useSendQR = () => {
  const toastID = `sendQR`;

  return useMutation({
    mutationFn: (data: FormData) => {
      toast.loading('Sending QR Code...', { id: toastID });
      return SendUserQR(data);
    },
    onSuccess: () => {
      toast.success('QR Code Detected', { id: toastID });
    },
    onError: () => {
      toast.error('Failed to detect QR Code', { id: toastID });
    },
  });
};
