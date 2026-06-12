import React, { useCallback, useMemo, useRef } from "react";
import { View, Text, FlatList } from "react-native";
import { useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import MapView, { Marker, PROVIDER_GOOGLE } from "react-native-maps";
import BottomSheet from "@gorhom/bottom-sheet";
import { useLocation } from "@/hooks/useLocation";
import { useNearbyGuards } from "@/hooks/useNearbyGuards";
import { GuardCard } from "@/components/GuardCard";
import { LoadingOverlay } from "@/components/LoadingOverlay";

export default function HomeScreen() {
  const router = useRouter();
  const { latitude, longitude, isLoading: locationLoading } = useLocation();
  const { data: guardsData, isLoading: guardsLoading } = useNearbyGuards();
  const bottomSheetRef = useRef<BottomSheet>(null);
  const snapPoints = useMemo(() => ["30%", "60%", "90%"], []);

  const handleGuardPress = useCallback(
    (guardId: string) => {
      router.push(`/guards/${guardId}`);
    },
    [router]
  );

  if (locationLoading) {
    return (
      <View className="flex-1 bg-secondary items-center justify-center">
        <LoadingOverlay visible message="Getting your location..." />
      </View>
    );
  }

  return (
    <View className="flex-1 bg-secondary">
      <MapView
        provider={PROVIDER_GOOGLE}
        style={{ flex: 1 }}
        initialRegion={{
          latitude: latitude || 28.6139,
          longitude: longitude || 77.209,
          latitudeDelta: 0.03,
          longitudeDelta: 0.03,
        }}
        customMapStyle={darkMapStyle}
      >
        {latitude && longitude && (
          <Marker
            coordinate={{ latitude, longitude }}
            title="You"
            pinColor="#6C63FF"
          />
        )}
        {guardsData?.results.map((guard) => (
          <Marker
            key={guard.id}
            coordinate={{
              latitude: guard.latitude,
              longitude: guard.longitude,
            }}
            title={guard.name}
            pinColor={guard.is_available ? "#00D4AA" : "#6B7280"}
            onPress={() => handleGuardPress(guard.id)}
          />
        ))}
      </MapView>

      <SafeAreaView className="absolute top-0 left-0 right-0">
        <View className="mx-4 mt-2">
          <View className="bg-surface/90 rounded-2xl px-4 py-3">
            <Text className="text-white font-semibold text-lg">bSecure</Text>
            <Text className="text-gray-400 text-xs">
              {guardsData?.count || 0} guards nearby
            </Text>
          </View>
        </View>
      </SafeAreaView>

      <BottomSheet
        ref={bottomSheetRef}
        index={0}
        snapPoints={snapPoints}
        backgroundStyle={{ backgroundColor: "#1E1E2E" }}
        handleIndicatorStyle={{ backgroundColor: "#4B5563" }}
      >
        <View className="px-4 pt-2 pb-4">
          <Text className="text-white font-bold text-lg mb-4">
            Nearby Guards
          </Text>
          {guardsLoading ? (
            <View className="items-center py-8">
              <Text className="text-gray-400">Finding guards...</Text>
            </View>
          ) : (
            <FlatList
              data={guardsData?.results || []}
              keyExtractor={(item) => item.id}
              renderItem={({ item }) => (
                <GuardCard
                  guard={item}
                  onPress={() => handleGuardPress(item.id)}
                />
              )}
              ListEmptyComponent={
                <View className="items-center py-8">
                  <Text className="text-gray-400">No guards available nearby</Text>
                </View>
              }
              showsVerticalScrollIndicator={false}
            />
          )}
        </View>
      </BottomSheet>
    </View>
  );
}

const darkMapStyle = [
  { elementType: "geometry", stylers: [{ color: "#242f3e" }] },
  { elementType: "labels.text.stroke", stylers: [{ color: "#242f3e" }] },
  { elementType: "labels.text.fill", stylers: [{ color: "#746855" }] },
  { featureType: "road", elementType: "geometry", stylers: [{ color: "#38414e" }] },
  { featureType: "road", elementType: "geometry.stroke", stylers: [{ color: "#212a37" }] },
  { featureType: "water", elementType: "geometry", stylers: [{ color: "#17263c" }] },
];
