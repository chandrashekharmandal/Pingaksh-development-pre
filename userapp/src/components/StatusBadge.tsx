import React from "react";
import { View, Text } from "react-native";
import { BookingStatus } from "@/types";

interface StatusBadgeProps {
  status: BookingStatus;
}

const statusConfig: Record<BookingStatus, { bg: string; text: string; label: string }> = {
  [BookingStatus.PENDING]: { bg: "bg-yellow-500/20", text: "text-yellow-400", label: "Pending" },
  [BookingStatus.CONFIRMED]: { bg: "bg-primary/20", text: "text-primary", label: "Confirmed" },
  [BookingStatus.ACTIVE]: { bg: "bg-accent/20", text: "text-accent", label: "Active" },
  [BookingStatus.COMPLETED]: { bg: "bg-gray-500/20", text: "text-gray-400", label: "Completed" },
  [BookingStatus.CANCELLED]: { bg: "bg-danger/20", text: "text-danger", label: "Cancelled" },
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const config = statusConfig[status];

  return (
    <View className={`px-3 py-1 rounded-full ${config.bg}`}>
      <Text className={`text-xs font-medium ${config.text}`}>
        {config.label}
      </Text>
    </View>
  );
};
