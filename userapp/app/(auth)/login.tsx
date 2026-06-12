import React, { useState } from "react";
import { View, Text, TextInput, Pressable, KeyboardAvoidingView, Platform } from "react-native";
import { useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { requestOTP } from "@/api/services/auth";
import * as Haptics from "expo-haptics";

export default function LoginScreen() {
  const [phone, setPhone] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const handleContinue = async () => {
    if (phone.length < 10) {
      setError("Enter a valid phone number");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await requestOTP(phone);
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      router.push({ pathname: "/(auth)/otp-verify", params: { phone } });
    } catch (err: any) {
      setError(err?.data?.message || "Something went wrong");
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
        <View className="mb-12">
          <Text className="text-white text-4xl font-bold mb-2">bSecure</Text>
          <Text className="text-gray-400 text-lg">
            Your safety, on demand.
          </Text>
        </View>

        <View className="mb-6">
          <Text className="text-gray-400 text-sm mb-2 ml-1">Phone Number</Text>
          <View className="flex-row items-center bg-surface rounded-2xl px-4 py-1">
            <Text className="text-white text-base mr-2">+91</Text>
            <TextInput
              className="flex-1 text-white text-lg py-4"
              placeholder="Enter your number"
              placeholderTextColor="#6B7280"
              keyboardType="phone-pad"
              maxLength={10}
              value={phone}
              onChangeText={(text) => {
                setPhone(text.replace(/[^0-9]/g, ""));
                setError("");
              }}
            />
          </View>
          {error ? (
            <Text className="text-danger text-sm mt-2 ml-1">{error}</Text>
          ) : null}
        </View>

        <Pressable
          onPress={handleContinue}
          disabled={loading || phone.length < 10}
          className={`rounded-full py-4 items-center ${
            phone.length >= 10 ? "bg-primary" : "bg-primary/40"
          }`}
          style={{ opacity: loading ? 0.7 : 1 }}
        >
          <Text className="text-white text-base font-semibold">
            {loading ? "Sending OTP..." : "Continue"}
          </Text>
        </Pressable>

        <Text className="text-gray-500 text-xs text-center mt-6">
          By continuing, you agree to our Terms of Service and Privacy Policy
        </Text>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
