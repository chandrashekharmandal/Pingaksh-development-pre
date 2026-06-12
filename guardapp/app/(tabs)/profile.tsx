import React from "react";
import { View, Text, Pressable, ScrollView, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import * as SecureStore from "expo-secure-store";
import { useGuardStore } from "@/stores/guard";
import { StatusBadge } from "@/components/StatusBadge";

export default function ProfileScreen() {
  const { guard, reset } = useGuardStore();

  const handleLogout = () => {
    Alert.alert("Logout", "Are you sure you want to logout?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Logout",
        style: "destructive",
        onPress: async () => {
          await SecureStore.deleteItemAsync("access_token");
          await SecureStore.deleteItemAsync("refresh_token");
          reset();
          router.replace("/(auth)/welcome");
        },
      },
    ]);
  };

  return (
    <SafeAreaView className="flex-1 bg-secondary">
      <ScrollView className="flex-1 px-6 pt-4">
        <Text className="text-white text-2xl font-bold mb-6">Profile</Text>

        {/* Avatar & Name */}
        <View className="items-center mb-8">
          <View className="w-20 h-20 rounded-full bg-primary/20 items-center justify-center mb-3">
            <Text className="text-3xl">👤</Text>
          </View>
          <Text className="text-white text-xl font-bold">
            {guard?.firstName} {guard?.lastName}
          </Text>
          <Text className="text-white/40 text-sm">{guard?.phone}</Text>
          <View className="mt-2">
            <StatusBadge status={guard?.verificationStatus || "pending"} />
          </View>
        </View>

        {/* Stats */}
        <View className="bg-surface rounded-2xl p-4 flex-row justify-around mb-6">
          <View className="items-center">
            <Text className="text-white text-lg font-bold">{guard?.totalBookings || 0}</Text>
            <Text className="text-white/40 text-xs">Bookings</Text>
          </View>
          <View className="items-center">
            <Text className="text-warning text-lg font-bold">{guard?.rating?.toFixed(1) || "—"}</Text>
            <Text className="text-white/40 text-xs">Rating</Text>
          </View>
          <View className="items-center">
            <Text className="text-white text-lg font-bold">{guard?.experience || 0}y</Text>
            <Text className="text-white/40 text-xs">Experience</Text>
          </View>
        </View>

        {/* Skills */}
        {guard?.skills && guard.skills.length > 0 && (
          <View className="mb-6">
            <Text className="text-white font-semibold mb-3">Skills</Text>
            <View className="flex-row flex-wrap gap-2">
              {guard.skills.map((skill) => (
                <View key={skill} className="bg-primary/20 px-3 py-1.5 rounded-full">
                  <Text className="text-primary text-xs font-semibold">{skill}</Text>
                </View>
              ))}
            </View>
          </View>
        )}

        {/* Settings */}
        <View className="gap-2 mb-8">
          {[
            { label: "Edit Profile", action: () => {} },
            { label: "Documents", action: () => {} },
            { label: "Availability", action: () => {} },
            { label: "Notifications", action: () => {} },
            { label: "Help & Support", action: () => {} },
          ].map((item) => (
            <Pressable
              key={item.label}
              onPress={item.action}
              className="bg-surface rounded-xl p-4 flex-row justify-between items-center active:opacity-80"
            >
              <Text className="text-white">{item.label}</Text>
              <Text className="text-white/30">›</Text>
            </Pressable>
          ))}
        </View>

        {/* Logout */}
        <Pressable
          onPress={handleLogout}
          className="bg-danger/10 rounded-xl p-4 items-center mb-8 active:opacity-80"
        >
          <Text className="text-danger font-semibold">Logout</Text>
        </Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}
