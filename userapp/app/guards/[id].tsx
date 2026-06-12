import React from "react";
import {
  View,
  Text,
  Pressable,
  ScrollView,
  Image,
  ActivityIndicator,
  FlatList,
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { useQuery } from "@tanstack/react-query";
import { getGuardProfile, getGuardReviews } from "@/api/services/guards";
import { RatingStars } from "@/components/RatingStars";

export default function GuardProfileScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();

  const { data: guard, isLoading } = useQuery({
    queryKey: ["guard", id],
    queryFn: () => getGuardProfile(id),
    enabled: !!id,
  });

  const { data: reviews } = useQuery({
    queryKey: ["guardReviews", id],
    queryFn: () => getGuardReviews(id),
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <SafeAreaView className="flex-1 bg-secondary items-center justify-center">
        <ActivityIndicator size="large" color="#6C63FF" />
      </SafeAreaView>
    );
  }

  if (!guard) {
    return (
      <SafeAreaView className="flex-1 bg-secondary items-center justify-center">
        <Text className="text-gray-400">Guard not found</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView className="flex-1 bg-secondary">
      <View className="px-4 pt-4 flex-row items-center justify-between">
        <Pressable onPress={() => router.back()}>
          <Text className="text-primary text-base">← Close</Text>
        </Pressable>
        <View />
      </View>

      <ScrollView className="flex-1 px-4 mt-4" showsVerticalScrollIndicator={false}>
        <View className="items-center mb-6">
          {guard.avatar ? (
            <Image
              source={{ uri: guard.avatar }}
              className="w-24 h-24 rounded-full mb-3"
            />
          ) : (
            <View className="w-24 h-24 rounded-full bg-primary/30 items-center justify-center mb-3">
              <Text className="text-primary text-3xl font-bold">
                {guard.name.charAt(0)}
              </Text>
            </View>
          )}
          <Text className="text-white text-2xl font-bold">{guard.name}</Text>
          <Text className="text-gray-400 capitalize mt-1">{guard.tier} Guard</Text>
          <View className="flex-row items-center mt-2">
            <RatingStars rating={guard.rating} size={16} showValue />
            <Text className="text-gray-400 text-sm ml-2">
              ({guard.total_reviews} reviews)
            </Text>
          </View>
        </View>

        <View className="flex-row bg-surface rounded-2xl p-4 mb-4">
          <View className="flex-1 items-center">
            <Text className="text-accent font-bold text-lg">
              ₹{guard.hourly_rate}
            </Text>
            <Text className="text-gray-400 text-xs">per hour</Text>
          </View>
          <View className="w-px bg-gray-700" />
          <View className="flex-1 items-center">
            <Text className="text-white font-bold text-lg">
              {guard.experience_years}
            </Text>
            <Text className="text-gray-400 text-xs">years exp</Text>
          </View>
          <View className="w-px bg-gray-700" />
          <View className="flex-1 items-center">
            <Text className="text-white font-bold text-lg">
              {guard.distance_km.toFixed(1)}
            </Text>
            <Text className="text-gray-400 text-xs">km away</Text>
          </View>
        </View>

        {guard.skills.length > 0 && (
          <View className="mb-4">
            <Text className="text-white font-bold mb-2">Skills</Text>
            <View className="flex-row flex-wrap gap-2">
              {guard.skills.map((skill) => (
                <View key={skill} className="bg-surface px-3 py-1.5 rounded-full">
                  <Text className="text-gray-300 text-sm">{skill}</Text>
                </View>
              ))}
            </View>
          </View>
        )}

        <View className="mb-6">
          <Text className="text-white font-bold mb-3">Reviews</Text>
          {reviews?.results.map((review) => (
            <View key={review.id} className="bg-surface rounded-xl p-4 mb-2">
              <View className="flex-row items-center justify-between mb-1">
                <Text className="text-white font-medium">{review.user_name}</Text>
                <RatingStars rating={review.rating} size={12} />
              </View>
              <Text className="text-gray-400 text-sm">{review.comment}</Text>
              <Text className="text-gray-600 text-xs mt-2">
                {new Date(review.created_at).toLocaleDateString("en-IN")}
              </Text>
            </View>
          ))}
        </View>

        <Pressable
          onPress={() => router.push("/booking/create")}
          className="bg-primary rounded-full py-4 items-center mb-8"
        >
          <Text className="text-white font-semibold text-base">
            Book {guard.name}
          </Text>
        </Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}
