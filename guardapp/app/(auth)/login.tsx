import React, { useState } from "react";
import { View, Text, TextInput, Pressable, KeyboardAvoidingView, Platform } from "react-native";
import { router } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { authService } from "@/api/services/auth";

export default function LoginScreen() {
  const [phone, setPhone] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSendOTP = async () => {
    if (phone.length < 10) {
      setError("Enter a valid phone number");
      return;
    }

    setIsLoading(true);
    setError("");
    try {
      await authService.requestOTP(`+91${phone}`);
      router.push({ pathname: "/(auth)/otp-verify", params: { phone: `+91${phone}` } });
    } catch (err: any) {
      setError(err?.response?.data?.message || "Failed to send OTP");
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
        <Text className="text-white text-2xl font-bold mb-2">Enter your number</Text>
        <Text className="text-white/50 mb-8">We'll send you a verification code</Text>

        <View className="flex-row bg-surface rounded-2xl overflow-hidden mb-4">
          <View className="bg-surface px-4 justify-center border-r border-white/10">
            <Text className="text-white/60 text-base">+91</Text>
          </View>
          <TextInput
            value={phone}
            onChangeText={(t) => { setPhone(t.replace(/[^0-9]/g, "")); setError(""); }}
            placeholder="Phone number"
            placeholderTextColor="#ffffff40"
            keyboardType="phone-pad"
            maxLength={10}
            className="flex-1 text-white text-lg py-4 px-4"
          />
        </View>

        {error ? <Text className="text-danger text-sm mb-4">{error}</Text> : null}

        <Pressable
          onPress={handleSendOTP}
          disabled={isLoading || phone.length < 10}
          className={`rounded-2xl py-4 items-center ${
            phone.length >= 10 ? "bg-primary" : "bg-primary/30"
          } active:opacity-80`}
        >
          <Text className="text-white font-bold text-base">
            {isLoading ? "Sending..." : "Continue"}
          </Text>
        </Pressable>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
