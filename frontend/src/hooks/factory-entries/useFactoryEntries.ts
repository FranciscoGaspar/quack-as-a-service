import { KEYS } from "@/constants/queryKeys";
import { GetFactoryEntries } from "@/services/factoryEntries.service";
import { useQuery } from "@tanstack/react-query";

export const useFactoryEntries = () => {
  return useQuery({
    queryKey: KEYS.factoryEntries,
    queryFn: () => {
      return GetFactoryEntries();
    },
  });
};
