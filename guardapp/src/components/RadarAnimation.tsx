import React, { useEffect } from "react";
import { View } from "react-native";
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withRepeat,
  withTiming,
  withDelay,
  Easing,
} from "react-native-reanimated";

export function RadarAnimation() {
  const ring1 = useSharedValue(0);
  const ring2 = useSharedValue(0);
  const ring3 = useSharedValue(0);

  useEffect(() => {
    ring1.value = withRepeat(withTiming(1, { duration: 2000, easing: Easing.out(Easing.ease) }), -1);
    ring2.value = withRepeat(withDelay(600, withTiming(1, { duration: 2000, easing: Easing.out(Easing.ease) })), -1);
    ring3.value = withRepeat(withDelay(1200, withTiming(1, { duration: 2000, easing: Easing.out(Easing.ease) })), -1);
  }, []);

  const makeRingStyle = (value: Animated.SharedValue<number>) =>
    useAnimatedStyle(() => ({
      opacity: 1 - value.value,
      transform: [{ scale: 1 + value.value * 2 }],
    }));

  const style1 = makeRingStyle(ring1);
  const style2 = makeRingStyle(ring2);
  const style3 = makeRingStyle(ring3);

  return (
    <View className="items-center justify-center w-48 h-48">
      {[style1, style2, style3].map((style, i) => (
        <Animated.View
          key={i}
          style={style}
          className="absolute w-24 h-24 rounded-full border-2 border-accent"
        />
      ))}
      <View className="w-6 h-6 rounded-full bg-accent" />
    </View>
  );
}
