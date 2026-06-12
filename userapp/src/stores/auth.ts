import { create } from "zustand";
import * as SecureStore from "expo-secure-store";
import { User } from "@/types";

interface AuthState {
  token: string | null;
  refreshToken: string | null;
  user: User | null;
  isAuthenticated: boolean;
  isHydrated: boolean;
  login: (tokens: { access: string; refresh: string }, user: User) => Promise<void>;
  logout: () => Promise<void>;
  hydrate: () => Promise<void>;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  refreshToken: null,
  user: null,
  isAuthenticated: false,
  isHydrated: false,

  login: async (tokens, user) => {
    await SecureStore.setItemAsync("access_token", tokens.access);
    await SecureStore.setItemAsync("refresh_token", tokens.refresh);
    await SecureStore.setItemAsync("user", JSON.stringify(user));
    set({
      token: tokens.access,
      refreshToken: tokens.refresh,
      user,
      isAuthenticated: true,
    });
  },

  logout: async () => {
    await SecureStore.deleteItemAsync("access_token");
    await SecureStore.deleteItemAsync("refresh_token");
    await SecureStore.deleteItemAsync("user");
    set({
      token: null,
      refreshToken: null,
      user: null,
      isAuthenticated: false,
    });
  },

  hydrate: async () => {
    try {
      const token = await SecureStore.getItemAsync("access_token");
      const refreshToken = await SecureStore.getItemAsync("refresh_token");
      const userStr = await SecureStore.getItemAsync("user");
      const user = userStr ? JSON.parse(userStr) : null;

      set({
        token,
        refreshToken,
        user,
        isAuthenticated: !!token,
        isHydrated: true,
      });
    } catch {
      set({ isHydrated: true });
    }
  },

  setUser: (user) => {
    SecureStore.setItemAsync("user", JSON.stringify(user));
    set({ user });
  },
}));
