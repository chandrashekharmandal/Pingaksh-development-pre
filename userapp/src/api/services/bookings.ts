import client from "../client";
import { Booking, BookingStatus } from "@/types";

interface BookingListResponse {
  results: Booking[];
  count: number;
  next: string | null;
}

interface CreateBookingData {
  guard_id: string;
  start_time: string;
  duration_hours: number;
  location_lat: number;
  location_lng: number;
  location_address: string;
  notes?: string;
}

export const createBooking = async (data: CreateBookingData): Promise<Booking> => {
  const { data: response } = await client.post("/api/bookings/", data);
  return response;
};

export const getBooking = async (id: string): Promise<Booking> => {
  const { data } = await client.get(`/api/bookings/${id}/`);
  return data;
};

export const getBookingList = async (
  status?: BookingStatus,
  page: number = 1
): Promise<BookingListResponse> => {
  const { data } = await client.get("/api/bookings/", {
    params: { status, page },
  });
  return data;
};

export const cancelBooking = async (id: string): Promise<Booking> => {
  const { data } = await client.post(`/api/bookings/${id}/cancel/`);
  return data;
};

export const endBooking = async (id: string): Promise<Booking> => {
  const { data } = await client.post(`/api/bookings/${id}/end/`);
  return data;
};
