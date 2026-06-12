import { useState, useCallback } from "react";
import * as Location from "expo-location";
import * as Haptics from "expo-haptics";
import { profileService } from "@/api/services/profile";
import { useGuardStore } from "@/stores/guard";
import { wsService } from "@/services/websocket";

export function useGuardStatus() {
  const { isOnline, setOnline, setOffline } = useGuardStore();
  const [isToggling, setIsToggling] = useState(false);

  const goOnline = useCallback(async () => {
    setIsToggling(true);
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== "granted") {
        throw new Error("Location permission required to go online");
      }

      await profileService.setOnlineStatus(true);
      setOnline();
      await wsService.connect();
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch (error) {
      throw error;
    } finally {
      setIsToggling(false);
    }
  }, [setOnline]);

  const goOffline = useCallback(async () => {
    setIsToggling(true);
    try {
      await profileService.setOnlineStatus(false);
      setOffline();
      wsService.disconnect();
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
    } catch (error) {
      throw error;
    } finally {
      setIsToggling(false);
    }
  }, [setOffline]);

  const toggle = useCallback(async () => {
    if (isOnline) {
      await goOffline();
    } else {
      await goOnline();
    }
  }, [isOnline, goOnline, goOffline]);

  return { isOnline, isToggling, toggle, goOnline, goOffline };
}
