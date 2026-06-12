import { useQuery } from "@tanstack/react-query";
import { earningsService } from "@/api/services/earnings";
import { useEarningsStore } from "@/stores/earnings";
import { useEffect } from "react";

export function useEarnings() {
  const { setSummary } = useEarningsStore();

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["earnings", "summary"],
    queryFn: earningsService.getSummary,
    refetchInterval: 60000,
  });

  useEffect(() => {
    if (data) setSummary(data);
  }, [data]);

  return { summary: data, isLoading, refetch };
}

export function usePayoutHistory(page: number = 1) {
  return useQuery({
    queryKey: ["payouts", page],
    queryFn: () => earningsService.getPayoutHistory(page),
  });
}
