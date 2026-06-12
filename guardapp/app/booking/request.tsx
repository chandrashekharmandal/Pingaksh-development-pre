import React, { useState, useEffect } from "react";
import { View, Text, Pressable } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import * as Haptics from "expo-haptics";
import { useActiveBookingStore } from "@/stores/activeBooking";
import { bookingsService } from "@/api/services/bookings";
import { wsService } from "@/services/websocket";

export default function BookingRequestScreen() {
  const { incomingRequest, setIncomingRequest, setActiveBooking } = useActiveBookingStore();
  const [countdown, setCountdown] = useState(30);
  const [isAccepting, setIsAccepting] = useState(false);

  useEffect(() => {
    if (!incomingRequest) {
      router.back();
      return;
    }

    const interval = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          handleDecline();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);

    return () => clearInterval(interval);
  }, []);

  const handleAccept = async () => {
    if (!incomingRequest) return;
    setIsAccepting(true);
    try {
      const booking = await bookingsService.acceptBooking(incomingRequest.id);
      setActiveBooking(booking);
      setIncomingRequest(null);
      wsService.sendBookingAccepted(incomingRequest.id);
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      router.replace("/booking/active");
    } catch {
      setIsAccepting(false);
    }
  };

  const handleDecline = async () => {
    if (!incomingRequest) return;
    try {
      await bookingsService.declineBooking(incomingRequest.id);
      wsService.sendBookingDeclined(incomingRequest.id);
    } catch {}
    setIncomingRequest(null);
    router.back();
  };

  if (!incomingRequest) return null;

  return (
    <SafeAreaView className="flex-1 bg-secondary justify-center px-6">
      {/* Countdown */}
      <View className="items-center mb-8">
        <View className="w-20 h-20 rounded-full bg-primary/20 items-center justify-center">
          <Text className="text-3xl font-bold text-primary">{countdown}</Text>
        </View>
        <Text className="text-white/40 text-sm mt-2">seconds remaining</Text>
      </View>

      {/* Request Details */}
      <View className="bg-surface rounded-3xl p-6 mb-8">
        <Text className="text-white text-xl font-bold text-center mb-4">
          New Booking Request
        </Text>

        <View className="gap-3">
          <View className="flex-row justify-between">
            <Text className="text-white/50">Client</Text>
            <Text className="text-white font-semibold">{incomingRequest.client.name}</Text>
          </View>
          <View className="flex-row justify-between">
            <Text className="text-white/50">Rating</Text>
            <Text className="text-warning">★ {incomingRequest.client.rating?.toFixed(1)}</Text>
          </View>
          <View className="flex-row justify-between">
            <Text className="text-white/50">Distance</Text>
            <Text className="text-white font-semibold">{incomingRequest.location.distance} km</Text>
          </View>
          <View className="flex-row justify-between">
            <Text className="text-white/50">Duration</Text>
            <Text className="text-white font-semibold">{incomingRequest.duration} hrs</Text>
          </View>
          <View className="h-px bg-white/10 my-1" />
          <View className="flex-row justify-between items-center">
            <Text className="text-white/50">Earnings</Text>
            <Text className="text-earn text-2xl font-bold">₹{incomingRequest.estimatedEarnings}</Text>
          </View>
        </View>

        <Text className="text-white/30 text-xs text-center mt-4" numberOfLines={2}>
          {incomingRequest.location.address}
        </Text>
      </View>

      {/* Actions */}
      <View className="flex-row gap-4">
        <Pressable
          onPress={handleDecline}
          className="flex-1 bg-danger/20 rounded-2xl py-4 items-center active:opacity-80"
        >
          <Text className="text-danger font-bold text-lg">Decline</Text>
        </Pressable>
        <Pressable
          onPress={handleAccept}
          disabled={isAccepting}
          className="flex-1 bg-accent rounded-2xl py-4 items-center active:opacity-80"
        >
          <Text className="text-secondary font-bold text-lg">
            {isAccepting ? "..." : "Accept"}
          </Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}
