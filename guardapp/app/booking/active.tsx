import React, { useEffect, useState } from "react";
import { View, Text, Pressable, Alert, Linking } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import MapView, { Marker } from "react-native-maps";
import * as Haptics from "expo-haptics";
import { useActiveBookingStore } from "@/stores/activeBooking";
import { bookingsService } from "@/api/services/bookings";
import { BookingStepBar } from "@/components/BookingStepBar";
import { useBookingTimer } from "@/hooks/useBookingTimer";
import { startBackgroundLocationTracking, stopBackgroundLocationTracking } from "@/lib/backgroundLocation";

export default function ActiveBookingScreen() {
  const { activeBooking, setActiveBooking, updateStatus, clear } = useActiveBookingStore();
  const elapsed = useBookingTimer(activeBooking?.startedAt || null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (activeBooking) {
      startBackgroundLocationTracking(activeBooking.id).catch(console.error);
    }
    return () => {
      stopBackgroundLocationTracking().catch(console.error);
    };
  }, [activeBooking?.id]);

  if (!activeBooking) {
    router.back();
    return null;
  }

  const handleNextStep = async () => {
    setIsLoading(true);
    try {
      let updated;
      switch (activeBooking.status) {
        case "accepted":
        case "en_route":
          updated = await bookingsService.markArrived(activeBooking.id);
          break;
        case "arrived":
          updated = await bookingsService.startBooking(activeBooking.id);
          break;
        case "started":
          updated = await bookingsService.completeBooking(activeBooking.id);
          await stopBackgroundLocationTracking();
          break;
      }
      if (updated) setActiveBooking(updated);
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);

      if (updated?.status === "completed") {
        clear();
        router.replace(`/booking/${activeBooking.id}`);
      }
    } catch (err) {
      Alert.alert("Error", "Failed to update status");
    }
    setIsLoading(false);
  };

  const getButtonLabel = () => {
    switch (activeBooking.status) {
      case "accepted":
      case "en_route": return "Mark Arrived";
      case "arrived": return "Start Booking";
      case "started": return "Complete";
      default: return "Next";
    }
  };

  const handleSOS = () => {
    Alert.alert("SOS", "Contact emergency services?", [
      { text: "Cancel", style: "cancel" },
      { text: "Call 112", onPress: () => Linking.openURL("tel:112") },
    ]);
  };

  return (
    <SafeAreaView className="flex-1 bg-secondary">
      {/* Map */}
      <View className="h-[40%]">
        <MapView
          style={{ flex: 1 }}
          initialRegion={{
            latitude: activeBooking.location.latitude,
            longitude: activeBooking.location.longitude,
            latitudeDelta: 0.01,
            longitudeDelta: 0.01,
          }}
          userInterfaceStyle="dark"
        >
          <Marker
            coordinate={{
              latitude: activeBooking.location.latitude,
              longitude: activeBooking.location.longitude,
            }}
            title={activeBooking.client.name}
          />
        </MapView>
      </View>

      {/* Bottom Panel */}
      <View className="flex-1 px-6 pt-4">
        <BookingStepBar currentStep={activeBooking.status} />

        {/* Client Info */}
        <View className="bg-surface rounded-2xl p-4 mt-4 flex-row items-center justify-between">
          <View>
            <Text className="text-white font-bold text-base">{activeBooking.client.name}</Text>
            <Text className="text-white/40 text-xs" numberOfLines={1}>
              {activeBooking.location.address}
            </Text>
          </View>
          <Pressable
            onPress={() => Linking.openURL(`tel:${activeBooking.client.phone}`)}
            className="w-10 h-10 rounded-full bg-primary/20 items-center justify-center"
          >
            <Text className="text-primary">📞</Text>
          </Pressable>
        </View>

        {/* Timer & Earnings */}
        {activeBooking.status === "started" && (
          <View className="flex-row justify-between mt-4">
            <View className="bg-surface rounded-xl p-3 flex-1 mr-2 items-center">
              <Text className="text-white/40 text-xs">Duration</Text>
              <Text className="text-white text-xl font-bold">{elapsed}</Text>
            </View>
            <View className="bg-surface rounded-xl p-3 flex-1 ml-2 items-center">
              <Text className="text-white/40 text-xs">Earning</Text>
              <Text className="text-earn text-xl font-bold">₹{activeBooking.estimatedEarnings}</Text>
            </View>
          </View>
        )}

        {/* Actions */}
        <View className="mt-auto mb-6 gap-3">
          <Pressable
            onPress={handleNextStep}
            disabled={isLoading}
            className={`rounded-2xl py-4 items-center active:opacity-80 ${
              activeBooking.status === "started" ? "bg-earn" : "bg-primary"
            }`}
          >
            <Text className="text-white font-bold text-base">
              {isLoading ? "Updating..." : getButtonLabel()}
            </Text>
          </Pressable>

          <Pressable
            onPress={handleSOS}
            className="bg-danger/10 rounded-2xl py-3 items-center"
          >
            <Text className="text-danger font-bold">SOS Emergency</Text>
          </Pressable>
        </View>
      </View>
    </SafeAreaView>
  );
}
