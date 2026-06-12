import React from "react";
import { View, Text } from "react-native";

interface RatingStarsProps {
  rating: number;
  size?: number;
  showValue?: boolean;
}

export const RatingStars: React.FC<RatingStarsProps> = ({
  rating,
  size = 14,
  showValue = false,
}) => {
  const fullStars = Math.floor(rating);
  const hasHalf = rating - fullStars >= 0.5;
  const emptyStars = 5 - fullStars - (hasHalf ? 1 : 0);

  return (
    <View className="flex-row items-center">
      {Array.from({ length: fullStars }).map((_, i) => (
        <Text key={`full-${i}`} style={{ fontSize: size, color: "#FFD700" }}>
          ★
        </Text>
      ))}
      {hasHalf && (
        <Text style={{ fontSize: size, color: "#FFD700" }}>★</Text>
      )}
      {Array.from({ length: emptyStars }).map((_, i) => (
        <Text key={`empty-${i}`} style={{ fontSize: size, color: "#4B5563" }}>
          ★
        </Text>
      ))}
      {showValue && (
        <Text className="text-gray-400 text-xs ml-1">
          {rating.toFixed(1)}
        </Text>
      )}
    </View>
  );
};
