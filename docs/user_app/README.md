# b-secure User Mobile App

The b-secure User App allows customers to book licensed security guards on-demand or on a scheduled basis. Users can track guards in real-time on a map, make payments via Razorpay, manage a wallet, and trigger an SOS alert during active bookings.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | React Native via **Expo SDK 51** |
| Language | **TypeScript** (strict mode) |
| Navigation | **Expo Router** v3 (file-based routing) |
| Server State | **TanStack Query v5** (React Query) |
| Client State | **Zustand** |
| Maps | **React Native Maps** + Google Maps SDK |
| Real-time | **WebSocket** (native browser API) |
| Payments | **Razorpay React Native SDK** |
| Push Notifications | **Expo Notifications** |
| Device Location | **Expo Location** |
| Styling | **NativeWind** v4 (Tailwind CSS for RN) |
| Storage | **Expo SecureStore** (JWT) + AsyncStorage |
| Error Tracking | **Sentry** (`@sentry/react-native`) |
| HTTP Client | **Axios** |
| Forms | **React Hook Form** + **Zod** |

---

## Folder Structure

```
bsecure-user-app/
├── app/                          # Expo Router — all screens live here
│   ├── _layout.tsx               # Root layout: auth gate, providers
│   ├── (auth)/
│   │   ├── _layout.tsx           # Auth stack layout
│   │   ├── login.tsx             # Phone number entry
│   │   └── otp-verify.tsx        # OTP verification
│   ├── (tabs)/
│   │   ├── _layout.tsx           # Bottom tab navigator
│   │   ├── home.tsx              # Map + nearby guards + booking entry
│   │   ├── bookings.tsx          # Active & history bookings
│   │   ├── wallet.tsx            # Wallet balance & top-up
│   │   └── profile.tsx           # User profile & settings
│   ├── guards/
│   │   └── [id].tsx              # Guard detail / profile
│   ├── booking/
│   │   ├── create.tsx            # Multi-step booking creation
│   │   ├── tracking.tsx          # Live tracking during booking
│   │   └── [id].tsx              # Booking detail / receipt
│   └── sos.tsx                   # SOS hold-to-trigger screen
│
├── src/
│   ├── api/                      # Axios instance + all service modules
│   │   ├── axios.ts
│   │   ├── authService.ts
│   │   ├── guardService.ts
│   │   ├── bookingService.ts
│   │   ├── walletService.ts
│   │   ├── reviewService.ts
│   │   ├── userService.ts
│   │   ├── sosService.ts
│   │   └── notificationService.ts
│   │
│   ├── components/               # Reusable UI components
│   │   ├── GuardCard.tsx
│   │   ├── BookingCard.tsx
│   │   ├── MapGuardMarker.tsx
│   │   ├── OTPInput.tsx
│   │   ├── RatingStars.tsx
│   │   ├── StatusBadge.tsx
│   │   ├── SOSButton.tsx
│   │   └── LoadingOverlay.tsx
│   │
│   ├── hooks/                    # Custom React hooks
│   │   ├── useNearbyGuards.ts
│   │   ├── useCreateBooking.ts
│   │   ├── useBookingWebSocket.ts
│   │   ├── useWallet.ts
│   │   ├── useRazorpay.ts
│   │   ├── useLocation.ts
│   │   ├── useOTP.ts
│   │   ├── usePushNotifications.ts
│   │   └── useSOSTrigger.ts
│   │
│   ├── store/                    # Zustand global state
│   │   ├── useAuthStore.ts
│   │   ├── useBookingStore.ts
│   │   └── useLocationStore.ts
│   │
│   ├── types/                    # TypeScript interfaces & enums
│   │   └── index.ts
│   │
│   ├── lib/
│   │   ├── queryClient.ts        # TanStack Query configuration
│   │   └── constants.ts          # App-wide constants
│   │
│   └── utils/
│       ├── format.ts             # Date, currency formatters
│       └── validators.ts         # Zod schemas
│
├── assets/
│   ├── images/
│   └── fonts/
│
├── app.json                      # Expo config
├── babel.config.js
├── metro.config.js
├── tailwind.config.js
├── tsconfig.json
└── package.json
```

---

## Documentation

| File | Description |
|---|---|
| [overview.md](./overview.md) | Setup, environment variables, global state, Axios, React Query, TypeScript types |
| [screens.md](./screens.md) | Every screen with full TSX component code |
| [components.md](./components.md) | Reusable UI components with typed props |
| [hooks.md](./hooks.md) | All custom hooks with full implementations |
| [api_integration.md](./api_integration.md) | API service layer, interceptors, error handling |

---

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/bsecure/user-app.git
cd user-app
npm install

# 2. Set up environment (see overview.md)
cp .env.example .env
# fill in API_BASE_URL, WS_BASE_URL, GOOGLE_MAPS_API_KEY, RAZORPAY_KEY_ID, SENTRY_DSN

# 3. Start development server
npx expo start

# 4. Run on device/simulator
npx expo run:ios
npx expo run:android
```

---

## Related Repositories

- `bsecure-backend` — Django REST Framework + Django Channels API
- `bsecure-guard-app` — Guard-side React Native app
- `bsecure-admin` — Web dashboard (Next.js)
