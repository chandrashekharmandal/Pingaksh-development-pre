import React from "react";
import { View, Text, ActivityIndicator, Pressable } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useLocalSearchParams, router } from "expo-router";
import { useQuery } from "@tanstack/react-query";
import { bookingsService } from "@/api/services/bookings";

export default function BookingDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();

  const { data: booking, isLoading } = useQuery({
    queryKey: ["booking", id],
    queryFn: () => bookingsService.getBookingDetail(id!),
    enabled: !!id,
  });

  if (isLoading || !booking) {
    return (
      <SafeAreaView className="flex-1 bg-secondary items-center justify-center">
        <ActivityIndicator color="#6C63FF" size="large" />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView className="flex-1 bg-secondary">
      <View className="flex-1 px-6 pt-4">
        {/* Header */}
        <Pressable onPress={() => router.back()} className="mb-4">
          <Text className="text-primary">← Back</Text>
        </Pressable>

        <Text className="text-white text-2xl font-bold mb-6">Booking Details</Text>

        {/* Completion Card */}
        {booking.status === "completed" && (
          <View className="bg-earn/10 rounded-3xl p-6 items-center mb-6">
            <Text className="text-earn text-3xl font-bold">₹{booking.estimatedEarnings}</Text>
            <Text className="text-white/50 text-sm mt-1">Total Earned</Text>
          </View>
        )}

        {/* Details */}
        <View className="bg-surface rounded-2xl p-5 gap-4">
          <View className="flex-row justify-between">
            <Text className="text-white/50">Client</Text>
            <Text className="text-white font-semibold">{booking.client.name}</Text>
          </View>
          <View className="flex-row justify-between">
            <Text className="text-white/50">Location</Text>
            <Text className="text-white font-semibold flex-1 text-right ml-4" numberOfLines={2}>
              {booking.location.address}
            </Text>
          </View>
          <View className="flex-row justify-between">
            <Text className="text-white/50">Duration</Text>
            <Text className="text-white font-semibold">{booking.duration || "—"} hrs</Text>
          </View>
          <View className="flex-row justify-between">
            <Text className="text-white/50">Rate</Text>
            <Text className="text-white font-semibold">₹{booking.rate}/hr</Text>
          </View>
          <View className="flex-row justify-between">
            <Text className="text-white/50">Status</Text>
            <View className={`px-3 py-1 rounded-full ${
              booking.status === "completed" ? "bg-accent/20" : "bg-primary/20"
            }`}>
              <Text className={`text-xs font-semibold capitalize ${
                booking.status === "completed" ? "text-accent" : "text-primary"
              }`}>
                {booking.status}
              </Text>
            </View>
          </View>

          {booking.startedAt && (
            <View className="flex-row justify-between">
              <Text className="text-white/50">Started</Text>
              <Text className="text-white/70 text-sm">
                {new Date(booking.startedAt).toLocaleString()}
              </Text>
            </View>
          )}
          {booking.completedAt && (
            <View className="flex-row justify-between">
              <Text className="text-white/50">Completed</Text>
              <Text className="text-white/70 text-sm">
                {new Date(booking.completedAt).toLocaleString()}
              </Text>
            </View>
          )}
        </View>

        {/* Earnings Breakdown */}
        <View className="bg-surface rounded-2xl p-5 mt-4 gap-3">
          <Text className="text-white font-semibold mb-1">Earnings Breakdown</Text>
          <View className="flex-row justify-between">
            <Text className="text-white/50">Base ({booking.duration || 0}h × ₹{booking.rate})</Text>
            <Text className="text-white">₹{(booking.duration || 0) * booking.rate}</Text>
          </View>
          <View className="flex-row justify-between">
            <Text className="text-white/50">Platform fee</Text>
            <Text className="text-danger">-₹{Math.round(booking.estimatedEarnings * 0.1)}</Text>
          </View>
          <View className="h-px bg-white/10" />
          <View className="flex-row justify-between">
            <Text className="text-white font-semibold">Net Earnings</Text>
            <Text className="text-earn font-bold text-lg">₹{booking.estimatedEarnings}</Text>
          </View>
        </View>
      </View>
    </SafeAreaView>
  );
}
