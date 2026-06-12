import { create } from "zustand";
import { Guard } from "@/types";

interface GuardStore {
  guard: Guard | null;
  isOnline: boolean;
  isAuthenticated: boolean;
  onboardingComplete: boolean;
  setGuard: (guard: Guard) => void;
  setOnline: () => void;
  setOffline: () => void;
  setAuthenticated: (value: boolean) => void;
  setOnboardingComplete: (value: boolean) => void;
  reset: () => void;
}

export const useGuardStore = create<GuardStore>((set) => ({
  guard: null,
  isOnline: false,
  isAuthenticated: false,
  onboardingComplete: false,
  setGuard: (guard) => set({ guard, isOnline: guard.isOnline }),
  setOnline: () => set({ isOnline: true }),
  setOffline: () => set({ isOnline: false }),
  setAuthenticated: (value) => set({ isAuthenticated: value }),
  setOnboardingComplete: (value) => set({ onboardingComplete: value }),
  reset: () => set({ guard: null, isOnline: false, isAuthenticated: false, onboardingComplete: false }),
}));
