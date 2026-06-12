import React from "react";
import { View, Text } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { OnlineToggle } from "@/components/OnlineToggle";
import { RadarAnimation } from "@/components/RadarAnimation";
import { EarningsCard } from "@/components/EarningsCard";
import { useGuardStore } from "@/stores/guard";
import { useEarnings } from "@/hooks/useEarnings";
import { useActiveBooking } from "@/hooks/useActiveBooking";
import { useIncomingRequest } from "@/hooks/useIncomingRequest";

export default function DashboardScreen() {
  const { isOnline, guard } = useGuardStore();
  const { summary } = useEarnings();
  const { activeBooking } = useActiveBooking();

  // Setup incoming request listener
  useIncomingRequest();

  // Redirect to active booking if exists
  React.useEffect(() => {
    if (activeBooking) {
      router.push("/booking/active");
    }
  }, [activeBooking]);

  return (
    <SafeAreaView className="flex-1 bg-secondary">
      <View className="flex-1 px-6 pt-4">
        {/* Header */}
        <View className="flex-row justify-between items-center mb-8">
          <View>
            <Text className="text-white/50 text-sm">Welcome back</Text>
            <Text className="text-white text-xl font-bold">
              {guard?.firstName || "Guard"}
            </Text>
          </View>
          <View className={`w-3 h-3 rounded-full ${isOnline ? "bg-accent" : "bg-white/20"}`} />
        </View>

        {/* Online Toggle - Central focus */}
        <View className="items-center justify-center flex-1">
          {isOnline && <RadarAnimation />}
          <View className="mt-6">
            <OnlineToggle />
          </View>
          {isOnline && (
            <Text className="text-white/40 text-sm mt-4">
              Waiting for booking requests...
            </Text>
          )}
          {!isOnline && (
            <Text className="text-white/30 text-sm mt-4">
              Go online to start receiving requests
            </Text>
          )}
        </View>

        {/* Quick Stats */}
        <View className="flex-row gap-3 mb-6">
          <EarningsCard
            title="Today"
            amount={summary?.today || 0}
            subtitle={`${summary?.completedToday || 0} bookings`}
          />
          <EarningsCard
            title="This Week"
            amount={summary?.thisWeek || 0}
            subtitle={`${summary?.hoursWorkedToday || 0}h worked`}
          />
        </View>
      </View>
    </SafeAreaView>
  );
}
