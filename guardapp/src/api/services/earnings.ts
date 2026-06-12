import { apiClient } from "../client";
import { EarningsSummary, Payout } from "@/types";

export const earningsService = {
  getSummary: async (): Promise<EarningsSummary> => {
    const { data } = await apiClient.get("/api/payments/earnings/summary/");
    return data;
  },

  getPayoutHistory: async (page: number = 1): Promise<{ results: Payout[]; count: number }> => {
    const { data } = await apiClient.get("/api/payments/payouts/", { params: { page } });
    return data;
  },

  requestPayout: async (amount: number): Promise<Payout> => {
    const { data } = await apiClient.post("/api/payments/payouts/request/", { amount });
    return data;
  },
};
