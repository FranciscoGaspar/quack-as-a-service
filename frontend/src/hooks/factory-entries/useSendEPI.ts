import { KEYS } from '@/constants/queryKeys';
import { getQueryClient } from '@/lib/getQueryClient';
import { SendUserEPI } from '@/services/factoryEntries.service';
import { useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';

export const useSendEPI = () => {
  const queryClient = getQueryClient();
  const toastID = `EPIs`;

  return useMutation({
    mutationFn: (data: FormData) => {
      toast.loading('Sending EPI Image...', { id: toastID });
      return SendUserEPI(data);
    },
    onSuccess: () => {
      toast.success('EPIs Detected', { id: toastID });
      queryClient.invalidateQueries({ queryKey: KEYS.factoryEntries });
    },
    onError: () => {
      toast.error('Failed to detect EPIs', { id: toastID });
    },
  });
};
