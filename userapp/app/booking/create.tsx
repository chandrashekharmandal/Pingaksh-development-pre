import React, { useState } from "react";
import {
  View,
  Text,
  Pressable,
  TextInput,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { useMutation } from "@tanstack/react-query";
import { createBooking } from "@/api/services/bookings";
import { useLocationStore } from "@/stores/location";
import { useBookingStore } from "@/stores/booking";
import { useNearbyGuards } from "@/hooks/useNearbyGuards";
import { GuardCard } from "@/components/GuardCard";
import { Guard } from "@/types";
import * as Haptics from "expo-haptics";

type Step = "guard" | "details" | "confirm";

export default function CreateBookingScreen() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("guard");
  const [selectedGuard, setSelectedGuard] = useState<Guard | null>(null);
  const [duration, setDuration] = useState("2");
  const [address, setAddress] = useState("");
  const [notes, setNotes] = useState("");
  const { latitude, longitude } = useLocationStore();
  const { setActiveBooking } = useBookingStore();
  const { data: guardsData } = useNearbyGuards();

  const bookingMutation = useMutation({
    mutationFn: createBooking,
    onSuccess: (booking) => {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      setActiveBooking(booking);
      router.replace(`/booking/tracking`);
    },
  });

  const handleConfirm = () => {
    if (!selectedGuard || !latitude || !longitude) return;

    bookingMutation.mutate({
      guard_id: selectedGuard.id,
      start_time: new Date().toISOString(),
      duration_hours: Number(duration),
      location_lat: latitude,
      location_lng: longitude,
      location_address: address,
      notes: notes || undefined,
    });
  };

  return (
    <SafeAreaView className="flex-1 bg-secondary">
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        className="flex-1"
      >
        <View className="px-4 pt-4 flex-row items-center justify-between">
          <Pressable onPress={() => router.back()}>
            <Text className="text-primary text-base">← Close</Text>
          </Pressable>
          <Text className="text-white font-bold text-lg">Book a Guard</Text>
          <View className="w-12" />
        </View>

        <View className="flex-row px-4 mt-4 mb-4">
          {(["guard", "details", "confirm"] as Step[]).map((s, i) => (
            <View key={s} className="flex-1 flex-row items-center">
              <View
                className={`w-8 h-8 rounded-full items-center justify-center ${
                  step === s ? "bg-primary" : "bg-surface"
                }`}
              >
                <Text className="text-white text-xs font-bold">{i + 1}</Text>
              </View>
              {i < 2 && <View className="flex-1 h-0.5 bg-surface mx-1" />}
            </View>
          ))}
        </View>

        <ScrollView className="flex-1 px-4" showsVerticalScrollIndicator={false}>
          {step === "guard" && (
            <View>
              <Text className="text-white font-bold text-lg mb-4">
                Select a Guard
              </Text>
              {guardsData?.results
                .filter((g) => g.is_available)
                .map((guard) => (
                  <Pressable
                    key={guard.id}
                    onPress={() => {
                      setSelectedGuard(guard);
                      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                    }}
                  >
                    <View
                      className={`border-2 rounded-2xl ${
                        selectedGuard?.id === guard.id
                          ? "border-primary"
                          : "border-transparent"
                      }`}
                    >
                      <GuardCard guard={guard} onPress={() => setSelectedGuard(guard)} />
                    </View>
                  </Pressable>
                ))}
              <Pressable
                onPress={() => selectedGuard && setStep("details")}
                disabled={!selectedGuard}
                className={`rounded-full py-4 items-center mt-4 ${
                  selectedGuard ? "bg-primary" : "bg-primary/40"
                }`}
              >
                <Text className="text-white font-semibold">Next</Text>
              </Pressable>
            </View>
          )}

          {step === "details" && (
            <View>
              <Text className="text-white font-bold text-lg mb-4">
                Booking Details
              </Text>

              <Text className="text-gray-400 text-sm mb-2">Duration (hours)</Text>
              <View className="flex-row gap-2 mb-4">
                {["1", "2", "4", "6", "8", "12"].map((h) => (
                  <Pressable
                    key={h}
                    onPress={() => setDuration(h)}
                    className={`px-4 py-2 rounded-full ${
                      duration === h ? "bg-primary" : "bg-surface"
                    }`}
                  >
                    <Text className="text-white text-sm">{h}h</Text>
                  </Pressable>
                ))}
              </View>

              <Text className="text-gray-400 text-sm mb-2">Location Address</Text>
              <TextInput
                className="bg-surface rounded-xl px-4 py-3 text-white mb-4"
                placeholder="Enter your address"
                placeholderTextColor="#6B7280"
                value={address}
                onChangeText={setAddress}
              />

              <Text className="text-gray-400 text-sm mb-2">Notes (optional)</Text>
              <TextInput
                className="bg-surface rounded-xl px-4 py-3 text-white mb-4"
                placeholder="Any special instructions"
                placeholderTextColor="#6B7280"
                value={notes}
                onChangeText={setNotes}
                multiline
                numberOfLines={3}
              />

              <View className="flex-row gap-3 mt-4">
                <Pressable
                  onPress={() => setStep("guard")}
                  className="flex-1 rounded-full py-4 items-center bg-surface"
                >
                  <Text className="text-white font-semibold">Back</Text>
                </Pressable>
                <Pressable
                  onPress={() => address && setStep("confirm")}
                  disabled={!address}
                  className={`flex-1 rounded-full py-4 items-center ${
                    address ? "bg-primary" : "bg-primary/40"
                  }`}
                >
                  <Text className="text-white font-semibold">Next</Text>
                </Pressable>
              </View>
            </View>
          )}

          {step === "confirm" && (
            <View>
              <Text className="text-white font-bold text-lg mb-4">
                Confirm Booking
              </Text>

              <View className="bg-surface rounded-2xl p-4 mb-4">
                <Text className="text-gray-400 text-sm">Guard</Text>
                <Text className="text-white font-medium mt-1">
                  {selectedGuard?.name} ({selectedGuard?.tier})
                </Text>

                <Text className="text-gray-400 text-sm mt-3">Duration</Text>
                <Text className="text-white font-medium mt-1">
                  {duration} hours
                </Text>

                <Text className="text-gray-400 text-sm mt-3">Location</Text>
                <Text className="text-white font-medium mt-1">{address}</Text>

                {notes && (
                  <>
                    <Text className="text-gray-400 text-sm mt-3">Notes</Text>
                    <Text className="text-white font-medium mt-1">{notes}</Text>
                  </>
                )}

                <View className="mt-4 pt-4 border-t border-gray-700/30">
                  <View className="flex-row justify-between">
                    <Text className="text-gray-400">Estimated Total</Text>
                    <Text className="text-accent font-bold text-lg">
                      ₹{(selectedGuard?.hourly_rate || 0) * Number(duration)}
                    </Text>
                  </View>
                </View>
              </View>

              <View className="flex-row gap-3">
                <Pressable
                  onPress={() => setStep("details")}
                  className="flex-1 rounded-full py-4 items-center bg-surface"
                >
                  <Text className="text-white font-semibold">Back</Text>
                </Pressable>
                <Pressable
                  onPress={handleConfirm}
                  disabled={bookingMutation.isPending}
                  className="flex-1 rounded-full py-4 items-center bg-accent"
                >
                  <Text className="text-white font-semibold">
                    {bookingMutation.isPending ? "Booking..." : "Confirm"}
                  </Text>
                </Pressable>
              </View>

              {bookingMutation.isError && (
                <Text className="text-danger text-center mt-4">
                  Failed to create booking. Try again.
                </Text>
              )}
            </View>
          )}
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
