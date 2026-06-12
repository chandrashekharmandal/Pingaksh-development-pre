import React, { useState } from "react";
import { View, Text, Pressable, FlatList, ActivityIndicator } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useEarnings, usePayoutHistory } from "@/hooks/useEarnings";
import { EarningsCard } from "@/components/EarningsCard";
import { earningsService } from "@/api/services/earnings";
import { Payout } from "@/types";

export default function EarningsScreen() {
  const { summary, isLoading } = useEarnings();
  const { data: payouts } = usePayoutHistory();
  const [requesting, setRequesting] = useState(false);

  const handleRequestPayout = async () => {
    if (!summary || summary.total <= 0) return;
    setRequesting(true);
    try {
      await earningsService.requestPayout(summary.total);
    } catch {}
    setRequesting(false);
  };

  const renderPayout = ({ item }: { item: Payout }) => (
    <View className="bg-surface rounded-xl p-4 flex-row justify-between items-center">
      <View>
        <Text className="text-white font-semibold">₹{item.amount}</Text>
        <Text className="text-white/40 text-xs">{new Date(item.requestedAt).toLocaleDateString()}</Text>
      </View>
      <View className={`px-3 py-1 rounded-full ${
        item.status === "completed" ? "bg-accent/20" : "bg-warning/20"
      }`}>
        <Text className={`text-xs font-semibold ${
          item.status === "completed" ? "text-accent" : "text-warning"
        }`}>
          {item.status}
        </Text>
      </View>
    </View>
  );

  if (isLoading) {
    return (
      <SafeAreaView className="flex-1 bg-secondary items-center justify-center">
        <ActivityIndicator color="#6C63FF" size="large" />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView className="flex-1 bg-secondary">
      <View className="flex-1 px-6 pt-4">
        <Text className="text-white text-2xl font-bold mb-6">Earnings</Text>

        {/* Summary Cards */}
        <View className="flex-row gap-3 mb-4">
          <EarningsCard title="Today" amount={summary?.today || 0} />
          <EarningsCard title="This Week" amount={summary?.thisWeek || 0} />
        </View>
        <View className="flex-row gap-3 mb-6">
          <EarningsCard title="This Month" amount={summary?.thisMonth || 0} color="#6C63FF" />
          <EarningsCard title="Total" amount={summary?.total || 0} color="#00D4AA" />
        </View>

        {/* Stats Row */}
        <View className="bg-surface rounded-2xl p-4 flex-row justify-around mb-6">
          <View className="items-center">
            <Text className="text-white text-lg font-bold">{summary?.completedThisWeek || 0}</Text>
            <Text className="text-white/40 text-xs">Bookings</Text>
          </View>
          <View className="items-center">
            <Text className="text-white text-lg font-bold">{summary?.hoursWorkedToday || 0}h</Text>
            <Text className="text-white/40 text-xs">Hours</Text>
          </View>
          <View className="items-center">
            <Text className="text-white text-lg font-bold">{summary?.averageRating?.toFixed(1) || "—"}</Text>
            <Text className="text-white/40 text-xs">Rating</Text>
          </View>
        </View>

        {/* Payout Button */}
        <Pressable
          onPress={handleRequestPayout}
          disabled={requesting}
          className="bg-earn rounded-2xl py-3 items-center mb-6 active:opacity-80"
        >
          <Text className="text-secondary font-bold text-base">
            {requesting ? "Requesting..." : "Request Payout"}
          </Text>
        </Pressable>

        {/* Payout History */}
        <Text className="text-white font-semibold mb-3">Payout History</Text>
        <FlatList
          data={payouts?.results || []}
          keyExtractor={(item) => item.id}
          renderItem={renderPayout}
          ItemSeparatorComponent={() => <View className="h-2" />}
          ListEmptyComponent={
            <Text className="text-white/30 text-center py-8">No payouts yet</Text>
          }
        />
      </View>
    </SafeAreaView>
  );
}
