import client from "../client";
import type { AuthResponse } from "@/types";

export const authService = {
  login: async (email: string, password: string): Promise<AuthResponse> => {
    const { data } = await client.post("/api/auth/admin/login/", { email, password });
    return data;
  },
};
