import React from "react";
import { View, Text, Pressable } from "react-native";
import BottomSheet, { BottomSheetView } from "@gorhom/bottom-sheet";
import { IncomingRequest } from "@/types";

interface Props {
  request: IncomingRequest;
  countdown: number;
  onAccept: () => void;
  onDecline: () => void;
}

export function IncomingRequestSheet({ request, countdown, onAccept, onDecline }: Props) {
  const bottomSheetRef = React.useRef<BottomSheet>(null);

  return (
    <BottomSheet
      ref={bottomSheetRef}
      snapPoints={["55%"]}
      backgroundStyle={{ backgroundColor: "#2A2A3E" }}
      handleIndicatorStyle={{ backgroundColor: "#6C63FF" }}
    >
      <BottomSheetView className="flex-1 px-6 py-4">
        <View className="items-center mb-4">
          <View className="w-16 h-16 rounded-full bg-primary/20 items-center justify-center mb-2">
            <Text className="text-2xl font-bold text-primary">{countdown}</Text>
          </View>
          <Text className="text-white/60 text-sm">seconds to respond</Text>
        </View>

        <Text className="text-white text-xl font-bold text-center mb-2">
          New Booking Request
        </Text>

        <View className="bg-secondary rounded-2xl p-4 mb-4 gap-2">
          <View className="flex-row justify-between">
            <Text className="text-white/60">Client</Text>
            <Text className="text-white font-semibold">{request.client.name}</Text>
          </View>
          <View className="flex-row justify-between">
            <Text className="text-white/60">Distance</Text>
            <Text className="text-white font-semibold">{request.location.distance} km</Text>
          </View>
          <View className="flex-row justify-between">
            <Text className="text-white/60">Duration</Text>
            <Text className="text-white font-semibold">{request.duration} hrs</Text>
          </View>
          <View className="flex-row justify-between">
            <Text className="text-white/60">Earnings</Text>
            <Text className="text-earn font-bold text-lg">₹{request.estimatedEarnings}</Text>
          </View>
        </View>

        <Text className="text-white/50 text-xs text-center mb-4" numberOfLines={2}>
          {request.location.address}
        </Text>

        <View className="flex-row gap-3">
          <Pressable
            onPress={onDecline}
            className="flex-1 bg-danger/20 rounded-2xl py-4 items-center"
          >
            <Text className="text-danger font-bold text-base">Decline</Text>
          </Pressable>
          <Pressable
            onPress={onAccept}
            className="flex-1 bg-accent rounded-2xl py-4 items-center"
          >
            <Text className="text-secondary font-bold text-base">Accept</Text>
          </Pressable>
        </View>
      </BottomSheetView>
    </BottomSheet>
  );
}
