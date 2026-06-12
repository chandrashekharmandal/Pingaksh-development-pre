import React, { useState } from "react";
import { View, Text, Pressable } from "react-native";
import { useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { useBookingStore } from "@/stores/booking";
import { useLocationStore } from "@/stores/location";
import { triggerSOS } from "@/api/services/sos";
import { SOSButton } from "@/components/SOSButton";
import * as Haptics from "expo-haptics";

export default function SOSScreen() {
  const router = useRouter();
  const { activeBooking } = useBookingStore();
  const { latitude, longitude } = useLocationStore();
  const [triggered, setTriggered] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleTrigger = async () => {
    if (!activeBooking || !latitude || !longitude) return;

    setLoading(true);
    setError("");

    try {
      await triggerSOS(activeBooking.id, latitude, longitude);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
      setTriggered(true);
    } catch (err: any) {
      setError("Failed to trigger SOS. Try again.");
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-secondary">
      <View className="px-4 pt-4">
        <Pressable onPress={() => router.back()}>
          <Text className="text-primary text-base">← Back to safety</Text>
        </Pressable>
      </View>

      <View className="flex-1 items-center justify-center px-6">
        {triggered ? (
          <View className="items-center">
            <View className="w-24 h-24 rounded-full bg-danger/20 items-center justify-center mb-6">
              <Text className="text-danger text-4xl">!</Text>
            </View>
            <Text className="text-white text-2xl font-bold mb-2 text-center">
              SOS Triggered
            </Text>
            <Text className="text-gray-400 text-center mb-8">
              Emergency services and your contacts have been notified. Help is on
              the way.
            </Text>
            <Pressable
              onPress={() => router.back()}
              className="bg-surface rounded-full px-8 py-4"
            >
              <Text className="text-white font-semibold">Back to Tracking</Text>
            </Pressable>
          </View>
        ) : (
          <View className="items-center">
            <Text className="text-white text-2xl font-bold mb-2 text-center">
              Emergency SOS
            </Text>
            <Text className="text-gray-400 text-center mb-12">
              Hold the button for 3 seconds to alert emergency services and your
              emergency contacts.
            </Text>
            <SOSButton onTrigger={handleTrigger} disabled={loading} />
            {error && (
              <Text className="text-danger text-center mt-6">{error}</Text>
            )}
          </View>
        )}
      </View>
    </SafeAreaView>
  );
}
