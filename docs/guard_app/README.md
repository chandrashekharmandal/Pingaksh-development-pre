# b-secure Guard Mobile App

The **b-secure Guard App** is the professional-facing mobile application for verified security guard personnel on the b-secure platform. Guards use this app to manage their availability, receive and fulfill booking requests from users, navigate to job sites, track real-time earnings, maintain compliance documents, and respond to SOS emergencies.

---

## Purpose

Security guard professionals use this app to:

- Toggle their **online/offline availability** to receive booking requests
- Receive **real-time push notifications and WebSocket alerts** for incoming requests
- **Accept or decline** bookings within a 30-second window
- **Navigate** to the user's location using native maps integration
- Progress through booking **status steps**: En Route → Arrived → Started → Completed
- Monitor **earnings**, request payouts, and view payout history
- Upload and manage **compliance documents** (Aadhaar, PAN, police verification, etc.)
- Complete an **onboarding flow** that gates entry to the main app until admin-approved
- Trigger and receive **SOS alerts** with full-screen priority notifications

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | React Native via **Expo SDK 51** |
| Language | **TypeScript** (strict mode) |
| Navigation | **Expo Router** v3 (file-based routing) |
| Server State | **TanStack Query v5** (`@tanstack/react-query`) |
| Client State | **Zustand** v4 |
| Maps | **React Native Maps** (`react-native-maps`) |
| Real-time | **WebSocket** (native browser API) |
| Push Notifications | **Expo Notifications** (`expo-notifications`) |
| Background Location | **Expo Location** + **Expo Task Manager** (`expo-task-manager`) |
| Styling | **NativeWind** v4 (Tailwind CSS for RN) |
| Forms | **React Hook Form** + **Zod** |
| HTTP Client | **Axios** |
| Media | **expo-image-picker**, **expo-av** |
| Storage | **expo-secure-store** (tokens), **AsyncStorage** |

---

## Folder Structure

```
guard-app/
├── app/                                # Expo Router file-based routes
│   ├── _layout.tsx                     # Root layout — auth gate, providers
│   ├── index.tsx                       # Redirect: auth check → login or tabs
│   ├── (auth)/
│   │   ├── _layout.tsx
│   │   ├── login.tsx                   # Phone number entry
│   │   └── otp.tsx                     # OTP verification
│   ├── onboarding/
│   │   ├── _layout.tsx
│   │   ├── personal-info.tsx           # Step 1: name, DOB, city, skills
│   │   ├── documents.tsx               # Step 2: document uploads
│   │   └── complete.tsx                # Step 3: under-review screen
│   ├── (tabs)/
│   │   ├── _layout.tsx                 # Bottom tab navigator
│   │   ├── dashboard.tsx               # Online toggle + booking radar
│   │   ├── earnings.tsx                # Earnings summary + payout
│   │   ├── history.tsx                 # Booking history
│   │   └── profile.tsx                 # Profile + documents + schedule
│   ├── booking/
│   │   ├── request.tsx                 # Full-screen incoming request modal
│   │   ├── active.tsx                  # Active booking map + steps
│   │   └── [id].tsx                    # Completed booking detail
│   └── documents/
│       └── upload.tsx                  # Document camera/upload flow
├── src/
│   ├── api/                            # Axios instance + service modules
│   │   ├── client.ts
│   │   ├── guardProfileService.ts
│   │   ├── bookingService.ts
│   │   ├── earningsService.ts
│   │   ├── documentService.ts
│   │   ├── locationService.ts
│   │   └── onboardingService.ts
│   ├── store/                          # Zustand stores
│   │   ├── guardStore.ts
│   │   ├── activeBookingStore.ts
│   │   └── earningsStore.ts
│   ├── hooks/                          # Custom React hooks
│   │   ├── useGuardStatus.ts
│   │   ├── useIncomingRequest.ts
│   │   ├── useAcceptBooking.ts
│   │   ├── useActiveBooking.ts
│   │   ├── useNavigationToUser.ts
│   │   ├── useEarnings.ts
│   │   ├── useDocumentUpload.ts
│   │   └── useBookingTimer.ts
│   ├── services/
│   │   ├── websocketService.ts         # Guard WebSocket client
│   │   └── backgroundLocation.ts      # BG location module
│   ├── types/
│   │   └── guard.ts                    # All TypeScript interfaces
│   ├── constants/
│   │   ├── tasks.ts                    # Task name constants
│   │   └── config.ts                   # API URL, WS URL, thresholds
│   └── components/                     # Shared UI components
│       ├── RadarAnimation.tsx
│       ├── BookingRequestCard.tsx
│       ├── StepProgressBar.tsx
│       ├── EarningsChart.tsx
│       ├── DocumentItem.tsx
│       └── SOSButton.tsx
├── assets/
│   ├── sounds/
│   │   └── incoming_request.mp3
│   └── images/
├── app.json
├── babel.config.js
├── tailwind.config.js
├── tsconfig.json
└── package.json
```

---

## Documentation Index

| File | Description |
|---|---|
| [overview.md](./overview.md) | Setup, env vars, background location config, auth gate, Zustand stores |
| [screens.md](./screens.md) | All screen components with full TSX code |
| [background_location.md](./background_location.md) | Background location tracking deep-dive |
| [hooks.md](./hooks.md) | All custom hooks with TypeScript code |
| [realtime.md](./realtime.md) | WebSocket service, message types, notification handling |
| [api_integration.md](./api_integration.md) | Axios setup, all service modules, TypeScript interfaces |

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/bsecure/guard-app
cd guard-app
npm install

# Copy env
cp .env.example .env.local
# Fill in API_URL, WS_URL, etc.

# Start
npx expo start

# Physical device build (required for background location)
npx expo run:ios --device
npx expo run:android --device
```

> **Important:** Background location tracking requires a physical device. Always test location features using a custom development build, not Expo Go.

---

## Key Differentiators from User App

| Feature | Guard App | User App |
|---|---|---|
| Background Location | Broadcasts every 10s via `expo-task-manager` | Not required |
| Online/Offline Toggle | Explicit availability control | Always discoverable |
| Verification Gate | Onboarding + admin approval required | Instant registration |
| SOS Receiver | Receives SOS from users, full-screen alert | Sends SOS |
| Earnings & Payouts | Full earnings dashboard + payout requests | Not applicable |
