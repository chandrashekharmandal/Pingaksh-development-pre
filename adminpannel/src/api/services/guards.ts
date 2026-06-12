import client from "../client";
import type { Guard, GuardDetail, PaginatedResponse } from "@/types";

export const guardsService = {
  getGuards: async (params?: { page?: number; search?: string; tier?: string; status?: string }): Promise<PaginatedResponse<Guard>> => {
    const { data } = await client.get("/api/admin/guards/", { params });
    return data;
  },
  getGuardDetail: async (id: string): Promise<GuardDetail> => {
    const { data } = await client.get(`/api/admin/guards/${id}/`);
    return data;
  },
  approveGuard: async (id: string): Promise<void> => {
    await client.post(`/api/admin/guards/${id}/approve/`);
  },
  suspendGuard: async (id: string): Promise<void> => {
    await client.post(`/api/admin/guards/${id}/suspend/`);
  },
  changeGuardTier: async (id: string, tier: string): Promise<void> => {
    await client.patch(`/api/admin/guards/${id}/tier/`, { tier });
  },
};
