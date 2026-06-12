import React from "react";
import { View, Text } from "react-native";

interface Props {
  status: string;
}

const STATUS_MAP: Record<string, { bg: string; text: string; label: string }> = {
  online: { bg: "bg-accent/20", text: "text-accent", label: "Online" },
  offline: { bg: "bg-white/10", text: "text-white/60", label: "Offline" },
  verified: { bg: "bg-accent/20", text: "text-accent", label: "Verified" },
  pending: { bg: "bg-warning/20", text: "text-warning", label: "Pending" },
  in_review: { bg: "bg-primary/20", text: "text-primary", label: "In Review" },
  approved: { bg: "bg-accent/20", text: "text-accent", label: "Approved" },
  rejected: { bg: "bg-danger/20", text: "text-danger", label: "Rejected" },
  completed: { bg: "bg-accent/20", text: "text-accent", label: "Completed" },
  active: { bg: "bg-primary/20", text: "text-primary", label: "Active" },
};

export function StatusBadge({ status }: Props) {
  const config = STATUS_MAP[status] || STATUS_MAP.pending;

  return (
    <View className={`px-3 py-1 rounded-full ${config.bg}`}>
      <Text className={`text-xs font-semibold ${config.text}`}>{config.label}</Text>
    </View>
  );
}
