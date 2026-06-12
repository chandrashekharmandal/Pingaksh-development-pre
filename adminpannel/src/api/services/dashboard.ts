import client from "../client";
import type { DashboardMetrics, SOSEvent, HourlyBooking } from "@/types";

export const dashboardService = {
  getMetrics: async (): Promise<DashboardMetrics> => {
    const { data } = await client.get("/api/admin/dashboard/metrics/");
    return data;
  },
  getRecentSOS: async (): Promise<SOSEvent[]> => {
    const { data } = await client.get("/api/admin/dashboard/recent-sos/");
    return data;
  },
  getHourlyBookings: async (): Promise<HourlyBooking[]> => {
    const { data } = await client.get("/api/admin/dashboard/hourly-bookings/");
    return data;
  },
};
