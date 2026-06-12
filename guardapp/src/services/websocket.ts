import * as SecureStore from "expo-secure-store";
import { IncomingRequest, WSMessage } from "@/types";

type MessageHandler = (message: WSMessage) => void;

class GuardWebSocketService {
  private static instance: GuardWebSocketService;
  private ws: WebSocket | null = null;
  private handlers: Map<string, Set<MessageHandler>> = new Map();
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private baseUrl = "wss://api.bsecure.app/ws/guard/";
  private isConnecting = false;

  static getInstance(): GuardWebSocketService {
    if (!GuardWebSocketService.instance) {
      GuardWebSocketService.instance = new GuardWebSocketService();
    }
    return GuardWebSocketService.instance;
  }

  async connect(): Promise<void> {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) return;
    this.isConnecting = true;

    const token = await SecureStore.getItemAsync("access_token");
    if (!token) {
      this.isConnecting = false;
      return;
    }

    this.ws = new WebSocket(`${this.baseUrl}?token=${token}`);

    this.ws.onopen = () => {
      this.isConnecting = false;
      this.reconnectAttempts = 0;
      console.log("[WS] Connected");
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WSMessage = JSON.parse(event.data);
        const handlers = this.handlers.get(message.type);
        handlers?.forEach((handler) => handler(message));

        const allHandlers = this.handlers.get("*");
        allHandlers?.forEach((handler) => handler(message));
      } catch (err) {
        console.error("[WS] Parse error:", err);
      }
    };

    this.ws.onclose = () => {
      this.isConnecting = false;
      this.scheduleReconnect();
    };

    this.ws.onerror = (error) => {
      console.error("[WS] Error:", error);
      this.isConnecting = false;
    };
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) return;

    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
    this.reconnectTimeout = setTimeout(() => {
      this.reconnectAttempts++;
      this.connect();
    }, delay);
  }

  disconnect(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    this.ws?.close();
    this.ws = null;
    this.reconnectAttempts = 0;
  }

  on(type: string, handler: MessageHandler): () => void {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, new Set());
    }
    this.handlers.get(type)!.add(handler);
    return () => this.handlers.get(type)?.delete(handler);
  }

  send(type: string, payload: Record<string, unknown>): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, payload }));
    }
  }

  sendLocationUpdate(latitude: number, longitude: number, heading: number, speed: number): void {
    this.send("location.update", { latitude, longitude, heading, speed });
  }

  sendBookingAccepted(bookingId: string): void {
    this.send("booking.accepted", { bookingId });
  }

  sendBookingDeclined(bookingId: string): void {
    this.send("booking.declined", { bookingId });
  }
}

export const wsService = GuardWebSocketService.getInstance();
