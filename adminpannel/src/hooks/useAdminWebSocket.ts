import { useEffect, useRef, useState, useCallback } from "react";
import type { WebSocketMessage } from "@/types";

const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws/admin/";

export function useAdminWebSocket(onMessage?: (msg: WebSocketMessage) => void) {
  const [isConnected, setIsConnected] = useState(false);
  const [sosCount, setSOSCount] = useState(0);
  const wsRef = useRef<WebSocket | null>(null);
  const retriesRef = useRef(0);
  const timeoutRef = useRef<ReturnType<typeof setTimeout>>();

  const connect = useCallback(() => {
    const token = localStorage.getItem("admin_token");
    if (!token) return;

    const ws = new WebSocket(`${WS_URL}?token=${token}`);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      retriesRef.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const msg: WebSocketMessage = JSON.parse(event.data);
        if (msg.type === "sos.new") {
          setSOSCount((c) => c + 1);
        }
        onMessage?.(msg);
      } catch {
        // ignore parse errors
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      const delay = Math.min(1000 * Math.pow(2, retriesRef.current), 30000);
      retriesRef.current += 1;
      timeoutRef.current = setTimeout(connect, delay);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [onMessage]);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [connect]);

  const clearSOSCount = useCallback(() => setSOSCount(0), []);

  return { isConnected, sosCount, clearSOSCount };
}
