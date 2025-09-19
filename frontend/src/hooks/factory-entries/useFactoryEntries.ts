import { KEYS } from "@/constants/queryKeys";
import { useQuery } from "@tanstack/react-query";

export const useFactoryEntries = () => {
  return useQuery({
    queryKey: KEYS.factoryEntries,
    queryFn: () => {
      return [];
    },
  });
};
