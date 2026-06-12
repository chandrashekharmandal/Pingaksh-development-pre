import { useEffect, useRef, useCallback } from "react";
import { useBookingStore } from "@/stores/booking";
import { useAuthStore } from "@/stores/auth";
import { Booking, WebSocketMessage } from "@/types";

const WS_URL = process.env.EXPO_PUBLIC_WS_URL || "ws://localhost:8000";

export const useBookingWebSocket = (bookingId: string | null) => {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout>>();
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;
  const { setActiveBooking } = useBookingStore();
  const { token } = useAuthStore();

  const connect = useCallback(() => {
    if (!bookingId || !token) return;

    const ws = new WebSocket(
      `${WS_URL}/ws/bookings/${bookingId}/?token=${token}`
    );

    ws.onopen = () => {
      reconnectAttemptsRef.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);

        switch (message.type) {
          case "booking.update":
            setActiveBooking(message.data as unknown as Booking);
            break;
          case "guard.location":
            const booking = useBookingStore.getState().activeBooking;
            if (booking) {
              setActiveBooking({
                ...booking,
                guard_lat: message.data.latitude as number,
                guard_lng: message.data.longitude as number,
              });
            }
            break;
        }
      } catch {
        // ignore parse errors
      }
    };

    ws.onclose = () => {
      if (reconnectAttemptsRef.current < maxReconnectAttempts) {
        const delay = Math.min(
          1000 * Math.pow(2, reconnectAttemptsRef.current),
          30000
        );
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectAttemptsRef.current += 1;
          connect();
        }, delay);
      }
    };

    ws.onerror = () => {
      ws.close();
    };

    wsRef.current = ws;
  }, [bookingId, token, setActiveBooking]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  const sendMessage = useCallback((message: Record<string, unknown>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  return { sendMessage };
};
