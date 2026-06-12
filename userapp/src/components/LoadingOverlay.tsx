import React from "react";
import { View, Text, ActivityIndicator } from "react-native";

interface LoadingOverlayProps {
  message?: string;
  visible: boolean;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  message = "Loading...",
  visible,
}) => {
  if (!visible) return null;

  return (
    <View className="absolute inset-0 bg-secondary/80 items-center justify-center z-50">
      <View className="bg-surface rounded-2xl p-6 items-center">
        <ActivityIndicator size="large" color="#6C63FF" />
        <Text className="text-white mt-3 text-sm">{message}</Text>
      </View>
    </View>
  );
};
