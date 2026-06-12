import React, { useState } from "react";
import { View, Text, Pressable, KeyboardAvoidingView, Platform } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { verifyOTP } from "@/api/services/auth";
import { useAuthStore } from "@/stores/auth";
import { OTPInput } from "@/components/OTPInput";
import * as Haptics from "expo-haptics";

export default function OTPVerifyScreen() {
  const { phone } = useLocalSearchParams<{ phone: string }>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();
  const { login } = useAuthStore();

  const handleVerify = async (otp: string) => {
    setLoading(true);
    setError("");

    try {
      const response = await verifyOTP(phone, otp);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      await login(
        { access: response.access, refresh: response.refresh },
        response.user as any
      );
      router.replace("/(tabs)/home");
    } catch (err: any) {
      setError(err?.data?.message || "Invalid OTP");
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-secondary">
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        className="flex-1 justify-center px-6"
      >
        <Pressable onPress={() => router.back()} className="mb-8">
          <Text className="text-primary text-base">← Back</Text>
        </Pressable>

        <View className="mb-8">
          <Text className="text-white text-2xl font-bold mb-2">
            Verify your number
          </Text>
          <Text className="text-gray-400 text-base">
            Enter the 6-digit code sent to +91 {phone}
          </Text>
        </View>

        <View className="mb-8">
          <OTPInput length={6} onComplete={handleVerify} />
          {error ? (
            <Text className="text-danger text-sm text-center mt-4">
              {error}
            </Text>
          ) : null}
        </View>

        {loading && (
          <Text className="text-gray-400 text-center">Verifying...</Text>
        )}

        <Pressable className="mt-6">
          <Text className="text-primary text-center text-sm">
            Didn't receive code? Resend
          </Text>
        </Pressable>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
