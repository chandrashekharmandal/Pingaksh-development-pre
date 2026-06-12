import React from "react";
import { Tabs } from "expo-router";
import { View, Text } from "react-native";

function TabIcon({ name, focused }: { name: string; focused: boolean }) {
  const icons: Record<string, string> = {
    Home: "⌂",
    Bookings: "☰",
    Wallet: "◈",
    Profile: "●",
  };

  return (
    <View className="items-center pt-2">
      <Text
        style={{
          fontSize: 20,
          color: focused ? "#6C63FF" : "#6B7280",
        }}
      >
        {icons[name] || "●"}
      </Text>
      <Text
        className={`text-xs mt-1 ${focused ? "text-primary" : "text-gray-500"}`}
      >
        {name}
      </Text>
    </View>
  );
}

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: "#1E1E2E",
          borderTopColor: "#2A2A3E",
          borderTopWidth: 1,
          height: 80,
          paddingBottom: 20,
        },
        tabBarShowLabel: false,
      }}
    >
      <Tabs.Screen
        name="home"
        options={{
          tabBarIcon: ({ focused }) => <TabIcon name="Home" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="bookings"
        options={{
          tabBarIcon: ({ focused }) => <TabIcon name="Bookings" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="wallet"
        options={{
          tabBarIcon: ({ focused }) => <TabIcon name="Wallet" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          tabBarIcon: ({ focused }) => <TabIcon name="Profile" focused={focused} />,
        }}
      />
    </Tabs>
  );
}
