import React from "react";
import { Stack } from "expo-router";

export default function BookingLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: "#1E1E2E" },
        animation: "slide_from_bottom",
      }}
    />
  );
}
