import client from "../client";
import type { PlatformSettings } from "@/types";

export const settingsService = {
  getSettings: async (): Promise<PlatformSettings> => {
    const { data } = await client.get("/api/admin/settings/");
    return data;
  },
  updateSettings: async (settings: Partial<PlatformSettings>): Promise<PlatformSettings> => {
    const { data } = await client.put("/api/admin/settings/", settings);
    return data;
  },
};
