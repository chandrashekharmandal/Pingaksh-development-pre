import React, { useEffect, useState } from "react";
import { View, Text, Pressable } from "react-native";
import { router } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { onboardingService } from "@/api/services/onboarding";
import { useGuardStore } from "@/stores/guard";

const STEPS = [
  { key: "submitted", label: "Application Submitted", icon: "📋" },
  { key: "in_review", label: "Under Review", icon: "🔍" },
  { key: "approved", label: "Approved", icon: "✅" },
];

export default function OnboardingCompleteScreen() {
  const [status, setStatus] = useState<string>("submitted");
  const { setOnboardingComplete } = useGuardStore();

  useEffect(() => {
    const submitAndPoll = async () => {
      try {
        await onboardingService.submitForReview();
      } catch {}

      const interval = setInterval(async () => {
        try {
          const { status: s } = await onboardingService.getVerificationStatus();
          setStatus(s);
          if (s === "approved") {
            clearInterval(interval);
            setOnboardingComplete(true);
          }
        } catch {}
      }, 5000);

      return () => clearInterval(interval);
    };

    submitAndPoll();
  }, []);

  const currentIndex = STEPS.findIndex((s) => s.key === status);

  return (
    <SafeAreaView className="flex-1 bg-secondary justify-center px-8">
      <Text className="text-white text-2xl font-bold text-center mb-2">Almost There!</Text>
      <Text className="text-white/50 text-center mb-10">
        We're reviewing your application
      </Text>

      <View className="gap-6 mb-10">
        {STEPS.map((step, index) => {
          const isActive = index <= currentIndex;
          const isCurrent = index === currentIndex;

          return (
            <View key={step.key} className="flex-row items-center gap-4">
              <View className={`w-12 h-12 rounded-full items-center justify-center ${
                isActive ? "bg-accent/20" : "bg-surface"
              }`}>
                <Text className="text-xl">{step.icon}</Text>
              </View>
              <View className="flex-1">
                <Text className={`font-semibold ${isActive ? "text-white" : "text-white/40"}`}>
                  {step.label}
                </Text>
                {isCurrent && (
                  <Text className="text-accent text-xs mt-0.5">In progress...</Text>
                )}
              </View>
              {isActive && <Text className="text-accent">✓</Text>}
            </View>
          );
        })}
      </View>

      {status === "approved" && (
        <Pressable
          onPress={() => router.replace("/(tabs)/dashboard")}
          className="bg-primary rounded-2xl py-4 items-center active:opacity-80"
        >
          <Text className="text-white font-bold text-base">Start Earning</Text>
        </Pressable>
      )}

      {status === "rejected" && (
        <View className="bg-danger/10 rounded-2xl p-4">
          <Text className="text-danger font-semibold text-center">
            Application needs revision. Please update your documents.
          </Text>
        </View>
      )}
    </SafeAreaView>
  );
}
