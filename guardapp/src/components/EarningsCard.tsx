import React from "react";
import { View, Text } from "react-native";

interface Props {
  title: string;
  amount: number;
  subtitle?: string;
  color?: string;
}

export function EarningsCard({ title, amount, subtitle, color = "#4CD137" }: Props) {
  return (
    <View className="bg-surface rounded-2xl p-4 flex-1">
      <Text className="text-white/60 text-xs mb-1">{title}</Text>
      <Text style={{ color }} className="text-2xl font-bold">
        ₹{amount.toLocaleString()}
      </Text>
      {subtitle && <Text className="text-white/40 text-xs mt-1">{subtitle}</Text>}
    </View>
  );
}
