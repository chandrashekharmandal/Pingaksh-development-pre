import React, { useState } from "react";
import { View, Text, Pressable, FlatList, ActivityIndicator } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useQuery } from "@tanstack/react-query";
import { router } from "expo-router";
import { bookingsService } from "@/api/services/bookings";
import { BookingHistoryItem } from "@/types";

const FILTERS = ["today", "week", "month"] as const;

export default function HistoryScreen() {
  const [filter, setFilter] = useState<string>("week");
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ["bookingHistory", filter, page],
    queryFn: () => bookingsService.getHistory(page, filter),
  });

  const renderItem = ({ item }: { item: BookingHistoryItem }) => (
    <Pressable
      onPress={() => router.push(`/booking/${item.id}`)}
      className="bg-surface rounded-2xl p-4 active:opacity-80"
    >
      <View className="flex-row justify-between items-start mb-2">
        <View className="flex-1">
          <Text className="text-white font-semibold">{item.clientName}</Text>
          <Text className="text-white/40 text-xs mt-1" numberOfLines={1}>{item.address}</Text>
        </View>
        <Text className="text-earn font-bold">₹{item.earnings}</Text>
      </View>
      <View className="flex-row justify-between items-center">
        <Text className="text-white/30 text-xs">
          {new Date(item.date).toLocaleDateString()} • {item.duration}h
        </Text>
        {item.rating && (
          <Text className="text-warning text-xs">★ {item.rating.toFixed(1)}</Text>
        )}
      </View>
    </Pressable>
  );

  return (
    <SafeAreaView className="flex-1 bg-secondary">
      <View className="flex-1 px-6 pt-4">
        <Text className="text-white text-2xl font-bold mb-6">History</Text>

        {/* Filter Pills */}
        <View className="flex-row gap-2 mb-6">
          {FILTERS.map((f) => (
            <Pressable
              key={f}
              onPress={() => { setFilter(f); setPage(1); }}
              className={`px-4 py-2 rounded-full ${filter === f ? "bg-primary" : "bg-surface"}`}
            >
              <Text className={`text-sm font-semibold capitalize ${filter === f ? "text-white" : "text-white/50"}`}>
                {f}
              </Text>
            </Pressable>
          ))}
        </View>

        {isLoading ? (
          <ActivityIndicator color="#6C63FF" size="large" className="mt-10" />
        ) : (
          <FlatList
            data={data?.results || []}
            keyExtractor={(item) => item.id}
            renderItem={renderItem}
            ItemSeparatorComponent={() => <View className="h-3" />}
            ListEmptyComponent={
              <Text className="text-white/30 text-center py-12">No completed bookings</Text>
            }
            showsVerticalScrollIndicator={false}
          />
        )}
      </View>
    </SafeAreaView>
  );
}
