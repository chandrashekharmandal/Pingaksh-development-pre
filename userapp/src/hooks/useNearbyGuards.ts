import { useQuery } from "@tanstack/react-query";
import { getNearbyGuards } from "@/api/services/guards";
import { useLocationStore } from "@/stores/location";

export const useNearbyGuards = (radius: number = 5) => {
  const { latitude, longitude } = useLocationStore();

  return useQuery({
    queryKey: ["nearbyGuards", latitude, longitude, radius],
    queryFn: () => getNearbyGuards(latitude!, longitude!, radius),
    enabled: !!latitude && !!longitude,
    refetchInterval: 30000,
    staleTime: 15000,
  });
};
