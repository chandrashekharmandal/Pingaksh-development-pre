import React from "react";
import { View, Text, ActivityIndicator } from "react-native";

interface Props {
  message?: string;
}

export function LoadingOverlay({ message = "Loading..." }: Props) {
  return (
    <View className="absolute inset-0 bg-secondary/90 items-center justify-center z-50">
      <ActivityIndicator size="large" color="#6C63FF" />
      <Text className="text-white/60 mt-4 text-sm">{message}</Text>
    </View>
  );
}
