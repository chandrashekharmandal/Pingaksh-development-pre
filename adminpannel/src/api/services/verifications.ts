import client from "../client";
import type { VerificationItem, VerificationStats, PaginatedResponse } from "@/types";

export const verificationsService = {
  getQueue: async (params?: { page?: number; status?: string }): Promise<PaginatedResponse<VerificationItem>> => {
    const { data } = await client.get("/api/admin/verifications/", { params });
    return data;
  },
  getStats: async (): Promise<VerificationStats> => {
    const { data } = await client.get("/api/admin/verifications/stats/");
    return data;
  },
  approveDocument: async (id: string): Promise<void> => {
    await client.post(`/api/admin/verifications/${id}/approve/`);
  },
  rejectDocument: async (id: string, reason: string): Promise<void> => {
    await client.post(`/api/admin/verifications/${id}/reject/`, { reason });
  },
};
