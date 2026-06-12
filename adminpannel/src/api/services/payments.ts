import client from "../client";
import type { Transaction, RevenueSummary, Payout, PaginatedResponse } from "@/types";

export const paymentsService = {
  getTransactions: async (params?: { page?: number; type?: string }): Promise<PaginatedResponse<Transaction>> => {
    const { data } = await client.get("/api/admin/payments/transactions/", { params });
    return data;
  },
  getRevenueSummary: async (): Promise<RevenueSummary> => {
    const { data } = await client.get("/api/admin/payments/revenue-summary/");
    return data;
  },
  getPayouts: async (params?: { page?: number; status?: string }): Promise<PaginatedResponse<Payout>> => {
    const { data } = await client.get("/api/admin/payments/payouts/", { params });
    return data;
  },
  approvePayout: async (id: string): Promise<void> => {
    await client.post(`/api/admin/payments/payouts/${id}/approve/`);
  },
  bulkApprovePayouts: async (ids: string[]): Promise<void> => {
    await client.post("/api/admin/payments/payouts/bulk-approve/", { ids });
  },
};
