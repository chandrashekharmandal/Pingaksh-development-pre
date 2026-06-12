import client from "../client";
import type { Booking, BookingDetail, PaginatedResponse } from "@/types";

export const bookingsService = {
  getBookings: async (params?: { page?: number; status?: string; date_from?: string; date_to?: string }): Promise<PaginatedResponse<Booking>> => {
    const { data } = await client.get("/api/admin/bookings/", { params });
    return data;
  },
  getBookingDetail: async (id: string): Promise<BookingDetail> => {
    const { data } = await client.get(`/api/admin/bookings/${id}/`);
    return data;
  },
  forceCancelBooking: async (id: string): Promise<void> => {
    await client.post(`/api/admin/bookings/${id}/force-cancel/`);
  },
  refundBooking: async (id: string): Promise<void> => {
    await client.post(`/api/admin/bookings/${id}/refund/`);
  },
};
