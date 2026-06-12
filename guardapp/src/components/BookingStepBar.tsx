import React from "react";
import { View, Text } from "react-native";

const STEPS = ["en_route", "arrived", "started", "completed"] as const;
const LABELS = ["En Route", "Arrived", "Started", "Completed"];

interface Props {
  currentStep: string;
}

export function BookingStepBar({ currentStep }: Props) {
  const currentIndex = STEPS.indexOf(currentStep as any);

  return (
    <View className="flex-row items-center px-4 py-3">
      {STEPS.map((step, index) => {
        const isActive = index <= currentIndex;
        const isLast = index === STEPS.length - 1;

        return (
          <React.Fragment key={step}>
            <View className="items-center">
              <View
                className={`w-8 h-8 rounded-full items-center justify-center ${
                  isActive ? "bg-accent" : "bg-surface"
                }`}
              >
                <Text className={`text-xs font-bold ${isActive ? "text-secondary" : "text-white/40"}`}>
                  {index + 1}
                </Text>
              </View>
              <Text className={`text-[10px] mt-1 ${isActive ? "text-accent" : "text-white/40"}`}>
                {LABELS[index]}
              </Text>
            </View>
            {!isLast && (
              <View className={`flex-1 h-[2px] mx-1 ${index < currentIndex ? "bg-accent" : "bg-surface"}`} />
            )}
          </React.Fragment>
        );
      })}
    </View>
  );
}
