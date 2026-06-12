import { create } from "zustand";

interface LocationState {
  latitude: number | null;
  longitude: number | null;
  setLocation: (lat: number, lng: number) => void;
}

export const useLocationStore = create<LocationState>((set) => ({
  latitude: null,
  longitude: null,
  setLocation: (latitude, longitude) => set({ latitude, longitude }),
}));
