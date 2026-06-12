import React from "react";
import { View, Text, Image, Pressable } from "react-native";
import { Guard, GuardTier } from "@/types";
import { RatingStars } from "./RatingStars";
import { StatusBadge } from "./StatusBadge";

interface GuardCardProps {
  guard: Guard;
  onPress: () => void;
}

const tierColors: Record<GuardTier, string> = {
  [GuardTier.STANDARD]: "bg-surface",
  [GuardTier.PREMIUM]: "bg-primary/20",
  [GuardTier.ELITE]: "bg-accent/20",
};

export const GuardCard: React.FC<GuardCardProps> = ({ guard, onPress }) => {
  return (
    <Pressable
      onPress={onPress}
      className="bg-surface rounded-2xl p-4 mb-3 active:opacity-80"
    >
      <View className="flex-row items-center">
        <View className="relative">
          {guard.avatar ? (
            <Image
              source={{ uri: guard.avatar }}
              className="w-14 h-14 rounded-full"
            />
          ) : (
            <View className="w-14 h-14 rounded-full bg-primary/30 items-center justify-center">
              <Text className="text-primary text-lg font-bold">
                {guard.name.charAt(0)}
              </Text>
            </View>
          )}
          {guard.is_available && (
            <View className="absolute bottom-0 right-0 w-4 h-4 rounded-full bg-accent border-2 border-surface" />
          )}
        </View>

        <View className="flex-1 ml-3">
          <View className="flex-row items-center justify-between">
            <Text className="text-white font-semibold text-base">
              {guard.name}
            </Text>
            <View className={`px-2 py-0.5 rounded-full ${tierColors[guard.tier]}`}>
              <Text className="text-white text-xs capitalize">{guard.tier}</Text>
            </View>
          </View>

          <View className="flex-row items-center mt-1">
            <RatingStars rating={guard.rating} size={12} />
            <Text className="text-gray-400 text-xs ml-1">
              ({guard.total_reviews})
            </Text>
          </View>

          <View className="flex-row items-center justify-between mt-2">
            <Text className="text-gray-400 text-xs">
              {guard.distance_km.toFixed(1)} km away
            </Text>
            <Text className="text-accent font-bold text-sm">
              ₹{guard.hourly_rate}/hr
            </Text>
          </View>
        </View>
      </View>
    </Pressable>
  );
};
