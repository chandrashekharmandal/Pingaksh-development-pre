import React, { useRef, useState } from "react";
import { View, TextInput, Pressable } from "react-native";

interface OTPInputProps {
  length?: number;
  onComplete: (otp: string) => void;
}

export const OTPInput: React.FC<OTPInputProps> = ({
  length = 6,
  onComplete,
}) => {
  const [values, setValues] = useState<string[]>(Array(length).fill(""));
  const inputs = useRef<(TextInput | null)[]>([]);

  const handleChange = (text: string, index: number) => {
    const newValues = [...values];

    if (text.length > 1) {
      const chars = text.split("").slice(0, length);
      chars.forEach((char, i) => {
        if (index + i < length) {
          newValues[index + i] = char;
        }
      });
      setValues(newValues);
      const lastIndex = Math.min(index + chars.length, length) - 1;
      inputs.current[lastIndex]?.focus();
      if (newValues.every((v) => v !== "")) {
        onComplete(newValues.join(""));
      }
      return;
    }

    newValues[index] = text;
    setValues(newValues);

    if (text && index < length - 1) {
      inputs.current[index + 1]?.focus();
    }

    if (newValues.every((v) => v !== "")) {
      onComplete(newValues.join(""));
    }
  };

  const handleKeyPress = (key: string, index: number) => {
    if (key === "Backspace" && !values[index] && index > 0) {
      inputs.current[index - 1]?.focus();
      const newValues = [...values];
      newValues[index - 1] = "";
      setValues(newValues);
    }
  };

  return (
    <View className="flex-row justify-center gap-3">
      {Array.from({ length }).map((_, index) => (
        <TextInput
          key={index}
          ref={(ref) => {
            inputs.current[index] = ref;
          }}
          className="w-12 h-14 bg-surface rounded-xl text-center text-white text-xl font-bold border border-gray-700"
          maxLength={index === 0 ? length : 1}
          keyboardType="number-pad"
          value={values[index]}
          onChangeText={(text) => handleChange(text, index)}
          onKeyPress={({ nativeEvent }) =>
            handleKeyPress(nativeEvent.key, index)
          }
          style={{ borderColor: values[index] ? "#6C63FF" : "#374151" }}
        />
      ))}
    </View>
  );
};
