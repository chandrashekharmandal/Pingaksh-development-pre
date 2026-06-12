import React from "react";
import { Pressable, Text, View } from "react-native";
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
  withTiming,
  interpolateColor,
} from "react-native-reanimated";
import { useGuardStatus } from "@/hooks/useGuardStatus";

export function OnlineToggle() {
  const { isOnline, isToggling, toggle } = useGuardStatus();
  const progress = useSharedValue(isOnline ? 1 : 0);

  React.useEffect(() => {
    progress.value = withSpring(isOnline ? 1 : 0);
  }, [isOnline]);

  const trackStyle = useAnimatedStyle(() => ({
    backgroundColor: interpolateColor(progress.value, [0, 1], ["#3A3A4E", "#00D4AA"]),
  }));

  const thumbStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: withSpring(progress.value * 52) }],
  }));

  return (
    <View className="items-center gap-3">
      <Pressable onPress={toggle} disabled={isToggling}>
        <Animated.View
          style={trackStyle}
          className="w-[100px] h-[48px] rounded-full justify-center px-1"
        >
          <Animated.View
            style={thumbStyle}
            className="w-[42px] h-[42px] rounded-full bg-white shadow-lg"
          />
        </Animated.View>
      </Pressable>
      <Text className="text-white text-lg font-bold">
        {isToggling ? "Switching..." : isOnline ? "ONLINE" : "OFFLINE"}
      </Text>
    </View>
  );
}
