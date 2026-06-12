import React, { useState } from "react";
import { View, Text, Pressable, FlatList, ActivityIndicator } from "react-native";
import { useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { useQuery } from "@tanstack/react-query";
import { getBookingList } from "@/api/services/bookings";
import { BookingCard } from "@/components/BookingCard";
import { BookingStatus } from "@/types";

type Tab = "active" | "history";

export default function BookingsScreen() {
  const [activeTab, setActiveTab] = useState<Tab>("active");
  const router = useRouter();

  const { data, isLoading } = useQuery({
    queryKey: ["bookings", activeTab],
    queryFn: () =>
      getBookingList(
        activeTab === "active" ? BookingStatus.ACTIVE : undefined
      ),
  });

  const filteredBookings =
    activeTab === "active"
      ? data?.results.filter(
          (b) =>
            b.status === BookingStatus.ACTIVE ||
            b.status === BookingStatus.CONFIRMED ||
            b.status === BookingStatus.PENDING
        )
      : data?.results.filter(
          (b) =>
            b.status === BookingStatus.COMPLETED ||
            b.status === BookingStatus.CANCELLED
        );

  return (
    <SafeAreaView className="flex-1 bg-secondary">
      <View className="px-4 pt-4">
        <Text className="text-white text-2xl font-bold mb-6">Bookings</Text>

        <View className="flex-row bg-surface rounded-2xl p-1 mb-6">
          <Pressable
            onPress={() => setActiveTab("active")}
            className={`flex-1 py-3 rounded-xl items-center ${
              activeTab === "active" ? "bg-primary" : ""
            }`}
          >
            <Text
              className={`font-medium ${
                activeTab === "active" ? "text-white" : "text-gray-400"
              }`}
            >
              Active
            </Text>
          </Pressable>
          <Pressable
            onPress={() => setActiveTab("history")}
            className={`flex-1 py-3 rounded-xl items-center ${
              activeTab === "history" ? "bg-primary" : ""
            }`}
          >
            <Text
              className={`font-medium ${
                activeTab === "history" ? "text-white" : "text-gray-400"
              }`}
            >
              History
            </Text>
          </Pressable>
        </View>
      </View>

      {isLoading ? (
        <View className="flex-1 items-center justify-center">
          <ActivityIndicator size="large" color="#6C63FF" />
        </View>
      ) : (
        <FlatList
          data={filteredBookings || []}
          keyExtractor={(item) => item.id}
          contentContainerStyle={{ paddingHorizontal: 16 }}
          renderItem={({ item }) => (
            <BookingCard
              booking={item}
              onPress={() => router.push(`/booking/${item.id}`)}
            />
          )}
          ListEmptyComponent={
            <View className="items-center py-16">
              <Text className="text-gray-400 text-base">
                No {activeTab} bookings
              </Text>
            </View>
          }
          showsVerticalScrollIndicator={false}
        />
      )}
    </SafeAreaView>
  );
}
