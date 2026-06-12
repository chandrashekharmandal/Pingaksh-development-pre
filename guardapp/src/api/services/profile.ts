import { apiClient } from "../client";
import { Guard } from "@/types";

export const profileService = {
  getMyProfile: async (): Promise<Guard> => {
    const { data } = await apiClient.get("/api/guards/me/");
    return data;
  },

  updateProfile: async (payload: Partial<Guard>): Promise<Guard> => {
    const { data } = await apiClient.patch("/api/guards/me/", payload);
    return data;
  },

  setOnlineStatus: async (status: boolean): Promise<{ isOnline: boolean }> => {
    const { data } = await apiClient.post("/api/guards/me/status/", { isOnline: status });
    return data;
  },

  getAvailability: async () => {
    const { data } = await apiClient.get("/api/guards/me/availability/");
    return data;
  },

  updateAvailability: async (payload: Record<string, unknown>) => {
    const { data } = await apiClient.put("/api/guards/me/availability/", payload);
    return data;
  },
};
