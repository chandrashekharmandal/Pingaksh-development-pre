import React from "react";
import { View, Text, Pressable, ScrollView, ActivityIndicator } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getBooking, cancelBooking, endBooking } from "@/api/services/bookings";
import { StatusBadge } from "@/components/StatusBadge";
import { BookingStatus } from "@/types";
import * as Haptics from "expo-haptics";

export default function BookingDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: booking, isLoading } = useQuery({
    queryKey: ["booking", id],
    queryFn: () => getBooking(id),
    enabled: !!id,
  });

  const cancelMutation = useMutation({
    mutationFn: () => cancelBooking(id),
    onSuccess: () => {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      queryClient.invalidateQueries({ queryKey: ["booking", id] });
      queryClient.invalidateQueries({ queryKey: ["bookings"] });
    },
  });

  const endMutation = useMutation({
    mutationFn: () => endBooking(id),
    onSuccess: () => {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      queryClient.invalidateQueries({ queryKey: ["booking", id] });
      queryClient.invalidateQueries({ queryKey: ["bookings"] });
    },
  });

  if (isLoading) {
    return (
      <SafeAreaView className="flex-1 bg-secondary items-center justify-center">
        <ActivityIndicator size="large" color="#6C63FF" />
      </SafeAreaView>
    );
  }

  if (!booking) {
    return (
      <SafeAreaView className="flex-1 bg-secondary items-center justify-center">
        <Text className="text-gray-400">Booking not found</Text>
      </SafeAreaView>
    );
  }

  const isActive =
    booking.status === BookingStatus.ACTIVE ||
    booking.status === BookingStatus.CONFIRMED ||
    booking.status === BookingStatus.PENDING;

  return (
    <SafeAreaView className="flex-1 bg-secondary">
      <View className="px-4 pt-4 flex-row items-center justify-between">
        <Pressable onPress={() => router.back()}>
          <Text className="text-primary text-base">← Back</Text>
        </Pressable>
        <StatusBadge status={booking.status} />
      </View>

      <ScrollView className="flex-1 px-4 mt-4" showsVerticalScrollIndicator={false}>
        <View className="bg-surface rounded-2xl p-5 mb-4">
          <Text className="text-white font-bold text-xl mb-1">
            {booking.guard.name}
          </Text>
          <Text className="text-gray-400 text-sm capitalize">
            {booking.guard.tier} Guard
          </Text>
        </View>

        <View className="bg-surface rounded-2xl p-5 mb-4">
          <DetailRow label="Location" value={booking.location_address} />
          <DetailRow
            label="Start Time"
            value={new Date(booking.start_time).toLocaleString("en-IN")}
          />
          <DetailRow label="Duration" value={`${booking.duration_hours} hours`} />
          <DetailRow label="Total" value={`₹${booking.total_amount}`} accent />
          {booking.notes && <DetailRow label="Notes" value={booking.notes} />}
        </View>

        {isActive && (
          <View className="flex-row gap-3 mb-8">
            {booking.status === BookingStatus.ACTIVE && (
              <Pressable
                onPress={() => endMutation.mutate()}
                disabled={endMutation.isPending}
                className="flex-1 bg-accent rounded-full py-4 items-center"
              >
                <Text className="text-white font-semibold">End Booking</Text>
              </Pressable>
            )}
            {booking.status !== BookingStatus.ACTIVE && (
              <Pressable
                onPress={() => cancelMutation.mutate()}
                disabled={cancelMutation.isPending}
                className="flex-1 bg-danger/20 rounded-full py-4 items-center"
              >
                <Text className="text-danger font-semibold">Cancel</Text>
              </Pressable>
            )}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

function DetailRow({
  label,
  value,
  accent,
}: {
  label: string;
  value: string;
  accent?: boolean;
}) {
  return (
    <View className="flex-row justify-between items-start py-2 border-b border-gray-700/20">
      <Text className="text-gray-400 text-sm">{label}</Text>
      <Text
        className={`text-sm font-medium max-w-[60%] text-right ${
          accent ? "text-accent" : "text-white"
        }`}
      >
        {value}
      </Text>
    </View>
  );
}
