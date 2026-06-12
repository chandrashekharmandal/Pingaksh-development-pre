import React from "react";
import { View, Text, Pressable } from "react-native";
import { Booking, BookingStatus } from "@/types";
import { StatusBadge } from "./StatusBadge";

interface BookingCardProps {
  booking: Booking;
  onPress: () => void;
}

export const BookingCard: React.FC<BookingCardProps> = ({ booking, onPress }) => {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-IN", {
      day: "numeric",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <Pressable
      onPress={onPress}
      className="bg-surface rounded-2xl p-4 mb-3 active:opacity-80"
    >
      <View className="flex-row items-center justify-between mb-2">
        <Text className="text-white font-semibold text-base">
          {booking.guard.name}
        </Text>
        <StatusBadge status={booking.status} />
      </View>

      <View className="flex-row items-center mb-2">
        <View className="w-2 h-2 rounded-full bg-primary mr-2" />
        <Text className="text-gray-400 text-sm flex-1" numberOfLines={1}>
          {booking.location_address}
        </Text>
      </View>

      <View className="flex-row items-center justify-between mt-2 pt-2 border-t border-gray-700/30">
        <Text className="text-gray-400 text-xs">
          {formatDate(booking.start_time)}
        </Text>
        <Text className="text-gray-400 text-xs">
          {booking.duration_hours}h
        </Text>
        <Text className="text-accent font-bold text-sm">
          ₹{booking.total_amount}
        </Text>
      </View>
    </Pressable>
  );
};
