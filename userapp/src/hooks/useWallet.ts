import { useQuery } from "@tanstack/react-query";
import { getWallet, getTransactions } from "@/api/services/wallet";

export const useWallet = () => {
  return useQuery({
    queryKey: ["wallet"],
    queryFn: getWallet,
    staleTime: 30000,
  });
};

export const useTransactions = (page: number = 1) => {
  return useQuery({
    queryKey: ["transactions", page],
    queryFn: () => getTransactions(page),
    staleTime: 30000,
  });
};
