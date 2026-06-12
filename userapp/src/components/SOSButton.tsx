import React, { useRef, useState } from "react";
import { View, Text, Pressable, Animated } from "react-native";
import * as Haptics from "expo-haptics";

interface SOSButtonProps {
  onTrigger: () => void;
  disabled?: boolean;
}

export const SOSButton: React.FC<SOSButtonProps> = ({ onTrigger, disabled }) => {
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const progressAnim = useRef(new Animated.Value(0)).current;
  const [isHolding, setIsHolding] = useState(false);
  const holdTimeout = useRef<ReturnType<typeof setTimeout>>();

  const handlePressIn = () => {
    if (disabled) return;
    setIsHolding(true);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);

    Animated.spring(scaleAnim, {
      toValue: 0.9,
      useNativeDriver: true,
    }).start();

    Animated.timing(progressAnim, {
      toValue: 1,
      duration: 3000,
      useNativeDriver: false,
    }).start();

    holdTimeout.current = setTimeout(() => {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
      onTrigger();
      reset();
    }, 3000);
  };

  const handlePressOut = () => {
    if (holdTimeout.current) {
      clearTimeout(holdTimeout.current);
    }
    reset();
  };

  const reset = () => {
    setIsHolding(false);
    Animated.spring(scaleAnim, {
      toValue: 1,
      useNativeDriver: true,
    }).start();
    progressAnim.setValue(0);
  };

  return (
    <View className="items-center">
      <Animated.View style={{ transform: [{ scale: scaleAnim }] }}>
        <Pressable
          onPressIn={handlePressIn}
          onPressOut={handlePressOut}
          disabled={disabled}
          className="w-32 h-32 rounded-full bg-danger items-center justify-center shadow-lg"
          style={{ opacity: disabled ? 0.5 : 1 }}
        >
          <Text className="text-white text-xl font-bold">SOS</Text>
          <Text className="text-white/70 text-xs mt-1">Hold 3s</Text>
        </Pressable>
      </Animated.View>
      {isHolding && (
        <Text className="text-danger text-sm mt-4 font-medium">
          Keep holding...
        </Text>
      )}
    </View>
  );
};
