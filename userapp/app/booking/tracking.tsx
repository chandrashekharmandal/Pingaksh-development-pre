import React, { useEffect } from "react";
import { View, Text, Pressable } from "react-native";
import { useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import MapView, { Marker, PROVIDER_GOOGLE } from "react-native-maps";
import { useBookingStore } from "@/stores/booking";
import { useBookingWebSocket } from "@/hooks/useBookingWebSocket";
import { useLocation } from "@/hooks/useLocation";
import { StatusBadge } from "@/components/StatusBadge";
import { SOSButton } from "@/components/SOSButton";
import { BookingStatus } from "@/types";

export default function TrackingScreen() {
  const router = useRouter();
  const { activeBooking } = useBookingStore();
  const { latitude, longitude } = useLocation();
  useBookingWebSocket(activeBooking?.id || null);

  useEffect(() => {
    if (
      activeBooking?.status === BookingStatus.COMPLETED ||
      activeBooking?.status === BookingStatus.CANCELLED
    ) {
      router.replace(`/booking/${activeBooking.id}`);
    }
  }, [activeBooking?.status]);

  if (!activeBooking) {
    return (
      <SafeAreaView className="flex-1 bg-secondary items-center justify-center">
        <Text className="text-gray-400">No active booking</Text>
        <Pressable onPress={() => router.back()} className="mt-4">
          <Text className="text-primary">Go Back</Text>
        </Pressable>
      </SafeAreaView>
    );
  }

  return (
    <View className="flex-1 bg-secondary">
      <MapView
        provider={PROVIDER_GOOGLE}
        style={{ flex: 1 }}
        initialRegion={{
          latitude: activeBooking.location_lat,
          longitude: activeBooking.location_lng,
          latitudeDelta: 0.01,
          longitudeDelta: 0.01,
        }}
      >
        {latitude && longitude && (
          <Marker
            coordinate={{ latitude, longitude }}
            title="You"
            pinColor="#6C63FF"
          />
        )}
        {activeBooking.guard_lat && activeBooking.guard_lng && (
          <Marker
            coordinate={{
              latitude: activeBooking.guard_lat,
              longitude: activeBooking.guard_lng,
            }}
            title={activeBooking.guard.name}
            pinColor="#00D4AA"
          />
        )}
      </MapView>

      <SafeAreaView className="absolute top-0 left-0 right-0">
        <View className="mx-4 mt-2 flex-row items-center justify-between">
          <Pressable
            onPress={() => router.back()}
            className="bg-surface/90 rounded-full px-4 py-2"
          >
            <Text className="text-white">← Back</Text>
          </Pressable>
          <StatusBadge status={activeBooking.status} />
        </View>
      </SafeAreaView>

      <View className="absolute bottom-0 left-0 right-0 bg-secondary rounded-t-3xl p-6">
        <View className="flex-row items-center justify-between mb-4">
          <View>
            <Text className="text-white font-bold text-lg">
              {activeBooking.guard.name}
            </Text>
            <Text className="text-gray-400 text-sm">
              {activeBooking.guard.tier} Guard
            </Text>
          </View>
          <View className="items-end">
            <Text className="text-accent font-bold">
              ₹{activeBooking.total_amount}
            </Text>
            <Text className="text-gray-400 text-xs">
              {activeBooking.duration_hours}h
            </Text>
          </View>
        </View>

        <View className="flex-row gap-3">
          <Pressable
            onPress={() => router.push("/sos")}
            className="flex-1 bg-danger/20 rounded-full py-3 items-center"
          >
            <Text className="text-danger font-semibold">SOS</Text>
          </Pressable>
          <Pressable
            onPress={() => router.push(`/booking/${activeBooking.id}`)}
            className="flex-1 bg-surface rounded-full py-3 items-center"
          >
            <Text className="text-white font-semibold">Details</Text>
          </Pressable>
        </View>
      </View>
    </View>
  );
}
