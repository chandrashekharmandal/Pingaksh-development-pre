import React, { useState, useRef } from "react";
import { View, Text, TextInput, Pressable, KeyboardAvoidingView, Platform } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import * as SecureStore from "expo-secure-store";
import { authService } from "@/api/services/auth";
import { useGuardStore } from "@/stores/guard";
import { profileService } from "@/api/services/profile";

export default function OTPVerifyScreen() {
  const { phone } = useLocalSearchParams<{ phone: string }>();
  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const inputs = useRef<(TextInput | null)[]>([]);
  const { setAuthenticated, setGuard, setOnboardingComplete } = useGuardStore();

  const handleChange = (text: string, index: number) => {
    const newOtp = [...otp];
    newOtp[index] = text;
    setOtp(newOtp);
    setError("");

    if (text && index < 5) {
      inputs.current[index + 1]?.focus();
    }

    if (newOtp.every((d) => d !== "")) {
      verifyOTP(newOtp.join(""));
    }
  };

  const handleKeyPress = (key: string, index: number) => {
    if (key === "Backspace" && !otp[index] && index > 0) {
      inputs.current[index - 1]?.focus();
    }
  };

  const verifyOTP = async (code: string) => {
    setIsLoading(true);
    try {
      const { access, refresh, onboardingComplete } = await authService.verifyOTP(phone!, code);
      await SecureStore.setItemAsync("access_token", access);
      await SecureStore.setItemAsync("refresh_token", refresh);

      const profile = await profileService.getMyProfile();
      setGuard(profile);
      setAuthenticated(true);
      setOnboardingComplete(onboardingComplete);

      if (onboardingComplete) {
        router.replace("/(tabs)/dashboard");
      } else {
        router.replace("/onboarding/personal-info");
      }
    } catch (err: any) {
      setError(err?.response?.data?.message || "Invalid OTP");
      setOtp(["", "", "", "", "", ""]);
      inputs.current[0]?.focus();
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-secondary">
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        className="flex-1 justify-center px-8"
      >
        <Text className="text-white text-2xl font-bold mb-2">Verify OTP</Text>
        <Text className="text-white/50 mb-8">Code sent to {phone}</Text>

        <View className="flex-row gap-3 justify-center mb-6">
          {otp.map((digit, index) => (
            <TextInput
              key={index}
              ref={(ref) => { inputs.current[index] = ref; }}
              value={digit}
              onChangeText={(t) => handleChange(t, index)}
              onKeyPress={({ nativeEvent }) => handleKeyPress(nativeEvent.key, index)}
              keyboardType="number-pad"
              maxLength={1}
              className="w-12 h-14 bg-surface rounded-xl text-white text-center text-xl font-bold border border-white/10"
              selectTextOnFocus
            />
          ))}
        </View>

        {error ? <Text className="text-danger text-sm text-center mb-4">{error}</Text> : null}
        {isLoading && <Text className="text-primary text-center">Verifying...</Text>}

        <Pressable onPress={() => authService.requestOTP(phone!)} className="mt-6">
          <Text className="text-primary text-center">Resend Code</Text>
        </Pressable>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
