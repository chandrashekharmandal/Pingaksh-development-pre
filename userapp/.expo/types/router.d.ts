/* eslint-disable */
import * as Router from 'expo-router';

export * from 'expo-router';

declare module 'expo-router' {
  export namespace ExpoRouter {
    export interface __routes<T extends string = string> extends Record<string, unknown> {
      StaticRoutes: `/` | `/(auth)` | `/(auth)/login` | `/(auth)/otp-verify` | `/(tabs)` | `/(tabs)/bookings` | `/(tabs)/home` | `/(tabs)/profile` | `/(tabs)/wallet` | `/_sitemap` | `/booking/create` | `/booking/tracking` | `/bookings` | `/home` | `/login` | `/otp-verify` | `/profile` | `/sos` | `/wallet`;
      DynamicRoutes: `/booking/${Router.SingleRoutePart<T>}` | `/guards/${Router.SingleRoutePart<T>}`;
      DynamicRouteTemplate: `/booking/[id]` | `/guards/[id]`;
    }
  }
}
