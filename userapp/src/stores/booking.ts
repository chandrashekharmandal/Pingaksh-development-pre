import { create } from "zustand";
import { Booking } from "@/types";

interface BookingState {
  activeBooking: Booking | null;
  setActiveBooking: (booking: Booking | null) => void;
  clearActiveBooking: () => void;
}

export const useBookingStore = create<BookingState>((set) => ({
  activeBooking: null,
  setActiveBooking: (booking) => set({ activeBooking: booking }),
  clearActiveBooking: () => set({ activeBooking: null }),
}));
