import React from "react";
import { View, Text, TextInput, Pressable, ScrollView } from "react-native";
import { router } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { onboardingService } from "@/api/services/onboarding";

const schema = z.object({
  firstName: z.string().min(2, "First name required"),
  lastName: z.string().min(2, "Last name required"),
  dateOfBirth: z.string().min(8, "Date of birth required"),
  address: z.string().min(5, "Address required"),
  experience: z.string().min(1, "Experience required"),
  skills: z.string().min(2, "At least one skill required"),
});

type FormData = z.infer<typeof schema>;

export default function PersonalInfoScreen() {
  const { control, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    try {
      await onboardingService.submitPersonalInfo({
        firstName: data.firstName,
        lastName: data.lastName,
        dateOfBirth: data.dateOfBirth,
        address: data.address,
        experience: parseInt(data.experience),
        skills: data.skills.split(",").map((s) => s.trim()),
      });
      router.push("/onboarding/documents");
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-secondary">
      <ScrollView className="flex-1 px-6 pt-8" keyboardShouldPersistTaps="handled">
        <Text className="text-white text-2xl font-bold mb-2">Personal Info</Text>
        <Text className="text-white/50 mb-8">Tell us about yourself</Text>

        {([
          { name: "firstName", label: "First Name", placeholder: "John" },
          { name: "lastName", label: "Last Name", placeholder: "Doe" },
          { name: "dateOfBirth", label: "Date of Birth", placeholder: "DD/MM/YYYY" },
          { name: "address", label: "Address", placeholder: "Your current address" },
          { name: "experience", label: "Experience (years)", placeholder: "2", keyboard: "numeric" },
          { name: "skills", label: "Skills (comma separated)", placeholder: "Security, First Aid, CCTV" },
        ] as const).map((field) => (
          <View key={field.name} className="mb-4">
            <Text className="text-white/60 text-sm mb-2">{field.label}</Text>
            <Controller
              control={control}
              name={field.name}
              render={({ field: { onChange, value } }) => (
                <TextInput
                  value={value}
                  onChangeText={onChange}
                  placeholder={field.placeholder}
                  placeholderTextColor="#ffffff30"
                  keyboardType={(field as any).keyboard || "default"}
                  className="bg-surface rounded-xl px-4 py-3 text-white text-base"
                />
              )}
            />
            {errors[field.name] && (
              <Text className="text-danger text-xs mt-1">{errors[field.name]?.message}</Text>
            )}
          </View>
        ))}

        <Pressable
          onPress={handleSubmit(onSubmit)}
          disabled={isSubmitting}
          className="bg-primary rounded-2xl py-4 items-center mt-4 mb-8 active:opacity-80"
        >
          <Text className="text-white font-bold text-base">
            {isSubmitting ? "Saving..." : "Continue"}
          </Text>
        </Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}
