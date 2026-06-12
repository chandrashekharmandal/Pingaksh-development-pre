import { create } from "zustand";
import { ActiveBooking, IncomingRequest } from "@/types";

interface ActiveBookingStore {
  activeBooking: ActiveBooking | null;
  incomingRequest: IncomingRequest | null;
  setActiveBooking: (booking: ActiveBooking | null) => void;
  setIncomingRequest: (request: IncomingRequest | null) => void;
  updateStatus: (status: ActiveBooking["status"]) => void;
  clear: () => void;
}

export const useActiveBookingStore = create<ActiveBookingStore>((set) => ({
  activeBooking: null,
  incomingRequest: null,
  setActiveBooking: (booking) => set({ activeBooking: booking }),
  setIncomingRequest: (request) => set({ incomingRequest: request }),
  updateStatus: (status) =>
    set((state) => ({
      activeBooking: state.activeBooking ? { ...state.activeBooking, status } : null,
    })),
  clear: () => set({ activeBooking: null, incomingRequest: null }),
}));
