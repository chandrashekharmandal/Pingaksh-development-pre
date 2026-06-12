import client from "../client";
import type { SOSEvent, PaginatedResponse } from "@/types";

export const sosService = {
  getActiveSOS: async (): Promise<SOSEvent[]> => {
    const { data } = await client.get("/api/admin/sos/active/");
    return data;
  },
  getSOSHistory: async (params?: { page?: number }): Promise<PaginatedResponse<SOSEvent>> => {
    const { data } = await client.get("/api/admin/sos/history/", { params });
    return data;
  },
  resolveSOS: async (id: string, notes: string): Promise<void> => {
    await client.post(`/api/admin/sos/${id}/resolve/`, { resolution_notes: notes });
  },
};
