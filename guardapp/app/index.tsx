import { Redirect } from "expo-router";
import { useGuardStore } from "@/stores/guard";

export default function Index() {
  const { isAuthenticated, onboardingComplete } = useGuardStore();

  if (!isAuthenticated) {
    return <Redirect href="/(auth)/welcome" />;
  }

  if (!onboardingComplete) {
    return <Redirect href="/onboarding/personal-info" />;
  }

  return <Redirect href="/(tabs)/dashboard" />;
}
