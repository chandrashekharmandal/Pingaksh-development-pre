import { useEffect, useState } from "react";
import * as Location from "expo-location";
import { useLocationStore } from "@/stores/location";

export const useLocation = () => {
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { setLocation, latitude, longitude } = useLocationStore();

  useEffect(() => {
    let subscription: Location.LocationSubscription | null = null;

    const startWatching = async () => {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== "granted") {
        setErrorMsg("Location permission denied");
        setIsLoading(false);
        return;
      }

      const currentLocation = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
      });
      setLocation(
        currentLocation.coords.latitude,
        currentLocation.coords.longitude
      );
      setIsLoading(false);

      subscription = await Location.watchPositionAsync(
        {
          accuracy: Location.Accuracy.Balanced,
          timeInterval: 10000,
          distanceInterval: 50,
        },
        (location) => {
          setLocation(location.coords.latitude, location.coords.longitude);
        }
      );
    };

    startWatching();

    return () => {
      subscription?.remove();
    };
  }, [setLocation]);

  return { latitude, longitude, errorMsg, isLoading };
};
