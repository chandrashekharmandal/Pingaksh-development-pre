import { useEffect, useRef, useCallback } from "react";
import * as Haptics from "expo-haptics";
import { useActiveBookingStore } from "@/stores/activeBooking";
import { wsService } from "@/services/websocket";
import { IncomingRequest } from "@/types";
import { bookingsService } from "@/api/services/bookings";
import { router } from "expo-router";

export function useIncomingRequest() {
  const { incomingRequest, setIncomingRequest } = useActiveBookingStore();
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const countdownRef = useRef<number>(30);

  useEffect(() => {
    const unsub = wsService.on("booking.new_request", (message) => {
      const request = message.payload as unknown as IncomingRequest;
      setIncomingRequest(request);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
      router.push("/booking/request");

      countdownRef.current = 30;
      timerRef.current = setInterval(() => {
        countdownRef.current -= 1;
        if (countdownRef.current <= 0) {
          decline();
        }
      }, 1000);
    });

    const unsubCancel = wsService.on("booking.request_cancelled", () => {
      clearTimer();
      setIncomingRequest(null);
    });

    return () => {
      unsub();
      unsubCancel();
      clearTimer();
    };
  }, []);

  const clearTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  const accept = useCallback(async () => {
    if (!incomingRequest) return;
    clearTimer();
    try {
      const booking = await bookingsService.acceptBooking(incomingRequest.id);
      useActiveBookingStore.getState().setActiveBooking(booking);
      setIncomingRequest(null);
      wsService.sendBookingAccepted(incomingRequest.id);
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      router.replace("/booking/active");
    } catch (error) {
      console.error("Accept failed:", error);
    }
  }, [incomingRequest]);

  const decline = useCallback(async () => {
    if (!incomingRequest) return;
    clearTimer();
    try {
      await bookingsService.declineBooking(incomingRequest.id);
      wsService.sendBookingDeclined(incomingRequest.id);
    } catch (error) {
      console.error("Decline failed:", error);
    }
    setIncomingRequest(null);
    router.back();
  }, [incomingRequest]);

  return { incomingRequest, accept, decline, countdown: countdownRef.current };
}
