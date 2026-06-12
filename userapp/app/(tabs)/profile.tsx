import React from "react";
import { View, Text, Pressable, Image, ScrollView, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import { useAuthStore } from "@/stores/auth";
import { useQuery } from "@tanstack/react-query";
import { getProfile } from "@/api/services/user";

export default function ProfileScreen() {
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const { data: profile } = useQuery({
    queryKey: ["profile"],
    queryFn: getProfile,
  });

  const currentUser = profile || user;

  const handleLogout = () => {
    Alert.alert("Logout", "Are you sure you want to logout?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Logout",
        style: "destructive",
        onPress: () => logout(),
      },
    ]);
  };

  const menuItems = [
    { label: "Edit Profile", onPress: () => {} },
    { label: "Saved Addresses", onPress: () => {} },
    { label: "Emergency Contacts", onPress: () => {} },
    { label: "Notifications", onPress: () => {} },
    { label: "Help & Support", onPress: () => {} },
    { label: "About", onPress: () => {} },
  ];

  return (
    <SafeAreaView className="flex-1 bg-secondary">
      <ScrollView className="flex-1 px-4 pt-4" showsVerticalScrollIndicator={false}>
        <Text className="text-white text-2xl font-bold mb-6">Profile</Text>

        <View className="bg-surface rounded-2xl p-6 items-center mb-6">
          {currentUser?.avatar ? (
            <Image
              source={{ uri: currentUser.avatar }}
              className="w-20 h-20 rounded-full mb-3"
            />
          ) : (
            <View className="w-20 h-20 rounded-full bg-primary/30 items-center justify-center mb-3">
              <Text className="text-primary text-2xl font-bold">
                {currentUser?.name?.charAt(0) || "U"}
              </Text>
            </View>
          )}
          <Text className="text-white text-xl font-bold">
            {currentUser?.name || "User"}
          </Text>
          <Text className="text-gray-400 text-sm mt-1">
            +91 {currentUser?.phone}
          </Text>
          {currentUser?.email && (
            <Text className="text-gray-400 text-sm mt-1">
              {currentUser.email}
            </Text>
          )}
        </View>

        <View className="bg-surface rounded-2xl overflow-hidden mb-6">
          {menuItems.map((item, index) => (
            <Pressable
              key={item.label}
              onPress={item.onPress}
              className={`px-5 py-4 flex-row items-center justify-between active:bg-white/5 ${
                index < menuItems.length - 1 ? "border-b border-gray-700/30" : ""
              }`}
            >
              <Text className="text-white text-base">{item.label}</Text>
              <Text className="text-gray-500">›</Text>
            </Pressable>
          ))}
        </View>

        <Pressable
          onPress={handleLogout}
          className="bg-danger/10 rounded-2xl py-4 items-center mb-8"
        >
          <Text className="text-danger font-semibold">Logout</Text>
        </Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}
