import client from "../client";
import type { AnalyticsData, PeakHour } from "@/types";

export const analyticsService = {
  getBookingAnalytics: async (params?: { period?: string }): Promise<AnalyticsData> => {
    const { data } = await client.get("/api/admin/analytics/bookings/", { params });
    return data;
  },
  getRevenueAnalytics: async (params?: { period?: string }): Promise<AnalyticsData> => {
    const { data } = await client.get("/api/admin/analytics/revenue/", { params });
    return data;
  },
  getGuardAnalytics: async (): Promise<AnalyticsData> => {
    const { data } = await client.get("/api/admin/analytics/guards/");
    return data;
  },
  getPeakHours: async (): Promise<PeakHour[]> => {
    const { data } = await client.get("/api/admin/analytics/peak-hours/");
    return data;
  },
};
