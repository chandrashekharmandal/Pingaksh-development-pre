import * as TaskManager from "expo-task-manager";
import * as Location from "expo-location";
import * as SecureStore from "expo-secure-store";

const BACKGROUND_LOCATION_TASK = "BACKGROUND_LOCATION_TASK";
const BASE_URL = "https://api.bsecure.app";

TaskManager.defineTask(BACKGROUND_LOCATION_TASK, async ({ data, error }) => {
  if (error) {
    console.error("[BackgroundLocation] Error:", error.message);
    return;
  }

  if (data) {
    const { locations } = data as { locations: Location.LocationObject[] };
    const location = locations[0];

    if (!location) return;

    try {
      const token = await SecureStore.getItemAsync("access_token");
      const bookingId = await SecureStore.getItemAsync("active_booking_id");

      if (!token || !bookingId) return;

      await fetch(`${BASE_URL}/api/bookings/${bookingId}/location/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          latitude: location.coords.latitude,
          longitude: location.coords.longitude,
          heading: location.coords.heading ?? 0,
          speed: location.coords.speed ?? 0,
          timestamp: location.timestamp,
        }),
      });
    } catch (err) {
      console.error("[BackgroundLocation] Send failed:", err);
    }
  }
});

export const startBackgroundLocationTracking = async (bookingId: string): Promise<void> => {
  await SecureStore.setItemAsync("active_booking_id", bookingId);

  const { status: foreground } = await Location.requestForegroundPermissionsAsync();
  if (foreground !== "granted") throw new Error("Foreground location permission denied");

  const { status: background } = await Location.requestBackgroundPermissionsAsync();
  if (background !== "granted") throw new Error("Background location permission denied");

  const isStarted = await Location.hasStartedLocationUpdatesAsync(BACKGROUND_LOCATION_TASK);
  if (isStarted) return;

  await Location.startLocationUpdatesAsync(BACKGROUND_LOCATION_TASK, {
    accuracy: Location.Accuracy.High,
    distanceInterval: 10,
    timeInterval: 5000,
    deferredUpdatesInterval: 5000,
    showsBackgroundLocationIndicator: true,
    foregroundService: {
      notificationTitle: "bSecure Guard Active",
      notificationBody: "Tracking your location for active booking",
      notificationColor: "#6C63FF",
    },
  });
};

export const stopBackgroundLocationTracking = async (): Promise<void> => {
  await SecureStore.deleteItemAsync("active_booking_id");

  const isStarted = await Location.hasStartedLocationUpdatesAsync(BACKGROUND_LOCATION_TASK);
  if (isStarted) {
    await Location.stopLocationUpdatesAsync(BACKGROUND_LOCATION_TASK);
  }
};
