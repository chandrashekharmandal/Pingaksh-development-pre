import { create } from "zustand";
import { EarningsSummary } from "@/types";

interface EarningsStore {
  summary: EarningsSummary | null;
  todayEarnings: number;
  weekEarnings: number;
  totalEarnings: number;
  setSummary: (summary: EarningsSummary) => void;
  reset: () => void;
}

export const useEarningsStore = create<EarningsStore>((set) => ({
  summary: null,
  todayEarnings: 0,
  weekEarnings: 0,
  totalEarnings: 0,
  setSummary: (summary) =>
    set({
      summary,
      todayEarnings: summary.today,
      weekEarnings: summary.thisWeek,
      totalEarnings: summary.total,
    }),
  reset: () => set({ summary: null, todayEarnings: 0, weekEarnings: 0, totalEarnings: 0 }),
}));
