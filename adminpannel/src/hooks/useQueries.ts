import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { dashboardService } from "@/api/services/dashboard";
import { guardsService } from "@/api/services/guards";
import { usersService } from "@/api/services/users";
import { bookingsService } from "@/api/services/bookings";
import { paymentsService } from "@/api/services/payments";
import { sosService } from "@/api/services/sos";
import { analyticsService } from "@/api/services/analytics";
import { verificationsService } from "@/api/services/verifications";
import { settingsService } from "@/api/services/settings";

// Dashboard
export const useMetrics = () => useQuery({ queryKey: ["metrics"], queryFn: dashboardService.getMetrics, refetchInterval: 30000 });
export const useRecentSOS = () => useQuery({ queryKey: ["recent-sos"], queryFn: dashboardService.getRecentSOS, refetchInterval: 10000 });
export const useHourlyBookings = () => useQuery({ queryKey: ["hourly-bookings"], queryFn: dashboardService.getHourlyBookings });

// Guards
export const useGuards = (params?: { page?: number; search?: string; tier?: string; status?: string }) =>
  useQuery({ queryKey: ["guards", params], queryFn: () => guardsService.getGuards(params) });
export const useGuardDetail = (id: string) =>
  useQuery({ queryKey: ["guard", id], queryFn: () => guardsService.getGuardDetail(id), enabled: !!id });
export const useApproveGuard = () => {
  const qc = useQueryClient();
  return useMutation({ mutationFn: guardsService.approveGuard, onSuccess: () => { qc.invalidateQueries({ queryKey: ["guards"] }); } });
};
export const useSuspendGuard = () => {
  const qc = useQueryClient();
  return useMutation({ mutationFn: guardsService.suspendGuard, onSuccess: () => { qc.invalidateQueries({ queryKey: ["guards"] }); } });
};
export const useChangeGuardTier = () => {
  const qc = useQueryClient();
  return useMutation({ mutationFn: ({ id, tier }: { id: string; tier: string }) => guardsService.changeGuardTier(id, tier), onSuccess: () => { qc.invalidateQueries({ queryKey: ["guards"] }); } });
};

// Users
export const useUsers = (params?: { page?: number; search?: string }) =>
  useQuery({ queryKey: ["users", params], queryFn: () => usersService.getUsers(params) });
export const useUserDetail = (id: string) =>
  useQuery({ queryKey: ["user", id], queryFn: () => usersService.getUserDetail(id), enabled: !!id });
export const useSuspendUser = () => {
  const qc = useQueryClient();
  return useMutation({ mutationFn: usersService.suspendUser, onSuccess: () => { qc.invalidateQueries({ queryKey: ["users"] }); } });
};

// Bookings
export const useBookings = (params?: { page?: number; status?: string; date_from?: string; date_to?: string }) =>
  useQuery({ queryKey: ["bookings", params], queryFn: () => bookingsService.getBookings(params) });
export const useBookingDetail = (id: string) =>
  useQuery({ queryKey: ["booking", id], queryFn: () => bookingsService.getBookingDetail(id), enabled: !!id });
export const useForceCancelBooking = () => {
  const qc = useQueryClient();
  return useMutation({ mutationFn: bookingsService.forceCancelBooking, onSuccess: () => { qc.invalidateQueries({ queryKey: ["bookings"] }); } });
};
export const useRefundBooking = () => {
  const qc = useQueryClient();
  return useMutation({ mutationFn: bookingsService.refundBooking, onSuccess: () => { qc.invalidateQueries({ queryKey: ["bookings"] }); } });
};

// Payments
export const useTransactions = (params?: { page?: number; type?: string }) =>
  useQuery({ queryKey: ["transactions", params], queryFn: () => paymentsService.getTransactions(params) });
export const useRevenueSummary = () => useQuery({ queryKey: ["revenue-summary"], queryFn: paymentsService.getRevenueSummary });
export const usePayouts = (params?: { page?: number; status?: string }) =>
  useQuery({ queryKey: ["payouts", params], queryFn: () => paymentsService.getPayouts(params) });
export const useApprovePayout = () => {
  const qc = useQueryClient();
  return useMutation({ mutationFn: paymentsService.approvePayout, onSuccess: () => { qc.invalidateQueries({ queryKey: ["payouts"] }); } });
};
export const useBulkApprovePayouts = () => {
  const qc = useQueryClient();
  return useMutation({ mutationFn: paymentsService.bulkApprovePayouts, onSuccess: () => { qc.invalidateQueries({ queryKey: ["payouts"] }); } });
};

// SOS
export const useActiveSOS = () => useQuery({ queryKey: ["active-sos"], queryFn: sosService.getActiveSOS, refetchInterval: 5000 });
export const useSOSHistory = (params?: { page?: number }) =>
  useQuery({ queryKey: ["sos-history", params], queryFn: () => sosService.getSOSHistory(params) });
export const useResolveSOS = () => {
  const qc = useQueryClient();
  return useMutation({ mutationFn: ({ id, notes }: { id: string; notes: string }) => sosService.resolveSOS(id, notes), onSuccess: () => { qc.invalidateQueries({ queryKey: ["active-sos"] }); qc.invalidateQueries({ queryKey: ["sos-history"] }); } });
};

// Analytics
export const useBookingAnalytics = (period?: string) =>
  useQuery({ queryKey: ["analytics-bookings", period], queryFn: () => analyticsService.getBookingAnalytics({ period }) });
export const useRevenueAnalytics = (period?: string) =>
  useQuery({ queryKey: ["analytics-revenue", period], queryFn: () => analyticsService.getRevenueAnalytics({ period }) });
export const useGuardAnalytics = () => useQuery({ queryKey: ["analytics-guards"], queryFn: analyticsService.getGuardAnalytics });
export const usePeakHours = () => useQuery({ queryKey: ["peak-hours"], queryFn: analyticsService.getPeakHours });

// Verifications
export const useVerificationQueue = (params?: { page?: number; status?: string }) =>
  useQuery({ queryKey: ["verifications", params], queryFn: () => verificationsService.getQueue(params) });
export const useVerificationStats = () => useQuery({ queryKey: ["verification-stats"], queryFn: verificationsService.getStats });
export const useApproveDocument = () => {
  const qc = useQueryClient();
  return useMutation({ mutationFn: verificationsService.approveDocument, onSuccess: () => { qc.invalidateQueries({ queryKey: ["verifications"] }); qc.invalidateQueries({ queryKey: ["verification-stats"] }); } });
};
export const useRejectDocument = () => {
  const qc = useQueryClient();
  return useMutation({ mutationFn: ({ id, reason }: { id: string; reason: string }) => verificationsService.rejectDocument(id, reason), onSuccess: () => { qc.invalidateQueries({ queryKey: ["verifications"] }); qc.invalidateQueries({ queryKey: ["verification-stats"] }); } });
};

// Settings
export const useSettings = () => useQuery({ queryKey: ["settings"], queryFn: settingsService.getSettings });
export const useUpdateSettings = () => {
  const qc = useQueryClient();
  return useMutation({ mutationFn: settingsService.updateSettings, onSuccess: () => { qc.invalidateQueries({ queryKey: ["settings"] }); } });
};
