import * as SecureStore from "expo-secure-store";
import { getBaseUrl } from "../client";

export const locationService = {
  sendLocationUpdate: async (
    bookingId: string,
    latitude: number,
    longitude: number,
    heading: number,
    speed: number
  ): Promise<void> => {
    const token = await SecureStore.getItemAsync("access_token");
    const baseUrl = getBaseUrl();

    await fetch(`${baseUrl}/api/bookings/${bookingId}/location/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        latitude,
        longitude,
        heading,
        speed,
        timestamp: Date.now(),
      }),
    });
  },
};
