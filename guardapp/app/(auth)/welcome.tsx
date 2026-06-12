import React from "react";
import { View, Text, Pressable } from "react-native";
import { router } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";

export default function WelcomeScreen() {
  return (
    <SafeAreaView className="flex-1 bg-secondary">
      <View className="flex-1 justify-center items-center px-8">
        <View className="w-24 h-24 rounded-full bg-primary/20 items-center justify-center mb-6">
          <Text className="text-4xl">🛡️</Text>
        </View>

        <Text className="text-white text-3xl font-bold text-center mb-2">
          bSecure Guard
        </Text>
        <Text className="text-white/50 text-center text-base mb-12">
          Earn on your schedule. Protect with purpose.
        </Text>

        <View className="w-full gap-4">
          <View className="flex-row gap-4 mb-6">
            <View className="flex-1 bg-surface rounded-2xl p-4 items-center">
              <Text className="text-earn text-xl font-bold">₹500+</Text>
              <Text className="text-white/50 text-xs mt-1">Avg/day</Text>
            </View>
            <View className="flex-1 bg-surface rounded-2xl p-4 items-center">
              <Text className="text-accent text-xl font-bold">Flex</Text>
              <Text className="text-white/50 text-xs mt-1">Your hours</Text>
            </View>
            <View className="flex-1 bg-surface rounded-2xl p-4 items-center">
              <Text className="text-primary text-xl font-bold">Fast</Text>
              <Text className="text-white/50 text-xs mt-1">Payouts</Text>
            </View>
          </View>

          <Pressable
            onPress={() => router.push("/(auth)/login")}
            className="bg-primary rounded-2xl py-4 items-center active:opacity-80"
          >
            <Text className="text-white font-bold text-lg">Get Started</Text>
          </Pressable>

          <Text className="text-white/30 text-center text-xs mt-4">
            By continuing, you agree to our Terms of Service
          </Text>
        </View>
      </View>
    </SafeAreaView>
  );
}
