import client from "../client";
import type { User, UserDetail, PaginatedResponse } from "@/types";

export const usersService = {
  getUsers: async (params?: { page?: number; search?: string }): Promise<PaginatedResponse<User>> => {
    const { data } = await client.get("/api/admin/users/", { params });
    return data;
  },
  getUserDetail: async (id: string): Promise<UserDetail> => {
    const { data } = await client.get(`/api/admin/users/${id}/`);
    return data;
  },
  suspendUser: async (id: string): Promise<void> => {
    await client.post(`/api/admin/users/${id}/suspend/`);
  },
};
