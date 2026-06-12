import { apiClient } from "../client";
import { ActiveBooking, BookingHistoryItem } from "@/types";

export const bookingsService = {
  acceptBooking: async (id: string): Promise<ActiveBooking> => {
    const { data } = await apiClient.post(`/api/bookings/${id}/accept/`);
    return data;
  },

  declineBooking: async (id: string): Promise<void> => {
    await apiClient.post(`/api/bookings/${id}/decline/`);
  },

  markArrived: async (id: string): Promise<ActiveBooking> => {
    const { data } = await apiClient.post(`/api/bookings/${id}/arrived/`);
    return data;
  },

  startBooking: async (id: string): Promise<ActiveBooking> => {
    const { data } = await apiClient.post(`/api/bookings/${id}/start/`);
    return data;
  },

  completeBooking: async (id: string): Promise<ActiveBooking> => {
    const { data } = await apiClient.post(`/api/bookings/${id}/complete/`);
    return data;
  },

  getActiveBooking: async (): Promise<ActiveBooking | null> => {
    try {
      const { data } = await apiClient.get("/api/bookings/active/");
      return data;
    } catch {
      return null;
    }
  },

  getBookingDetail: async (id: string): Promise<ActiveBooking> => {
    const { data } = await apiClient.get(`/api/bookings/${id}/`);
    return data;
  },

  getHistory: async (page: number = 1, filter?: string): Promise<{ results: BookingHistoryItem[]; count: number }> => {
    const params: Record<string, string | number> = { status: "completed", page };
    if (filter) params.period = filter;
    const { data } = await apiClient.get("/api/bookings/", { params });
    return data;
  },
};
