import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { bookingsService } from "@/api/services/bookings";
import { useActiveBookingStore } from "@/stores/activeBooking";

export function useActiveBooking() {
  const { activeBooking, setActiveBooking } = useActiveBookingStore();

  const { data, isLoading } = useQuery({
    queryKey: ["activeBooking"],
    queryFn: bookingsService.getActiveBooking,
    refetchOnMount: true,
    enabled: !activeBooking,
  });

  useEffect(() => {
    if (data && !activeBooking) {
      setActiveBooking(data);
    }
  }, [data]);

  return { activeBooking, isLoading };
}
