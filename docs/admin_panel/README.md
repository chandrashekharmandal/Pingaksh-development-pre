# b-secure Admin Panel

## Purpose

The b-secure Admin Panel is an **internal operations dashboard** used exclusively by platform administrators. It provides full visibility and control over the platform's core entities — guards, users, bookings, payments, SOS events, and analytics — through a unified, real-time web interface.

This is not a customer-facing product. Access is restricted via next-auth credentials-based authentication backed by the Django admin login API. All routes under `/(dashboard)/*` are protected by middleware.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Next.js 14 (App Router) |
| Language | TypeScript |
| Styling | Tailwind CSS + shadcn/ui |
| Server State | TanStack Query v5 (React Query) |
| Client State | Zustand |
| Tables | TanStack Table v8 |
| Charts | Recharts |
| Forms | React Hook Form + Zod |
| HTTP Client | Axios |
| Authentication | next-auth (JWT strategy, Credentials Provider) |
| Real-time | WebSocket (native browser API) |
| Icons | lucide-react |

---

## Folder Structure

```
admin-panel/
├── app/
│   ├── (auth)/
│   │   └── login/
│   │       └── page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx                        # Sidebar + Topbar shell
│   │   ├── page.tsx                          # Overview / home dashboard
│   │   ├── guards/
│   │   │   ├── page.tsx                      # Guards list
│   │   │   └── [id]/
│   │   │       └── page.tsx                  # Guard detail + verification
│   │   ├── users/
│   │   │   ├── page.tsx                      # Users list
│   │   │   └── [id]/
│   │   │       └── page.tsx                  # User detail
│   │   ├── bookings/
│   │   │   ├── page.tsx                      # Bookings list
│   │   │   └── [id]/
│   │   │       └── page.tsx                  # Booking detail + actions
│   │   ├── payments/
│   │   │   ├── page.tsx                      # Transactions + payouts tabs
│   │   │   └── payouts/
│   │   │       └── page.tsx                  # Payouts management
│   │   ├── sos/
│   │   │   └── page.tsx                      # Live SOS dashboard
│   │   ├── analytics/
│   │   │   └── page.tsx                      # Charts + metrics
│   │   ├── verifications/
│   │   │   └── page.tsx                      # Verification queue
│   │   └── settings/
│   │       └── page.tsx                      # Platform settings
│   ├── api/
│   │   └── auth/
│   │       └── [...nextauth]/
│   │           └── route.ts                  # NextAuth route handler
│   ├── layout.tsx                            # Root layout (providers)
│   └── globals.css
├── components/
│   ├── ui/                                   # shadcn/ui primitives
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── input.tsx
│   │   ├── select.tsx
│   │   ├── badge.tsx
│   │   ├── tabs.tsx
│   │   ├── table.tsx
│   │   ├── dropdown-menu.tsx
│   │   ├── avatar.tsx
│   │   ├── skeleton.tsx
│   │   ├── alert-dialog.tsx
│   │   ├── popover.tsx
│   │   └── calendar.tsx
│   ├── layout/
│   │   ├── Sidebar.tsx                       # Nav sidebar
│   │   └── Topbar.tsx                        # Breadcrumb + avatar dropdown
│   ├── tables/
│   │   └── DataTable.tsx                     # TanStack Table generic wrapper
│   ├── charts/
│   │   ├── BookingsLineChart.tsx
│   │   ├── RevenueBarChart.tsx
│   │   ├── TierPieChart.tsx
│   │   └── PeakHoursHeatmap.tsx
│   └── shared/
│       ├── KPICard.tsx
│       ├── StatusBadge.tsx
│       ├── GuardVerificationCard.tsx
│       ├── SOSEventCard.tsx
│       ├── BookingTimeline.tsx
│       ├── PageHeader.tsx
│       ├── DateRangePicker.tsx
│       ├── ConfirmDialog.tsx
│       └── ExportButton.tsx
├── hooks/
│   ├── useAdminWebSocket.ts
│   ├── useDashboardMetrics.ts
│   ├── useGuards.ts
│   ├── useUsers.ts
│   ├── useBookings.ts
│   ├── usePayments.ts
│   ├── useSOS.ts
│   └── useAnalytics.ts
├── services/
│   ├── axios.ts                              # Axios instance + interceptors
│   ├── dashboardService.ts
│   ├── guardService.ts
│   ├── userService.ts
│   ├── bookingService.ts
│   ├── paymentService.ts
│   ├── sosService.ts
│   ├── analyticsService.ts
│   └── settingsService.ts
├── stores/
│   ├── sosStore.ts                           # Live SOS events (Zustand)
│   ├── wsStore.ts                            # WebSocket connection state
│   └── dashboardStore.ts                     # Live KPI counters
├── lib/
│   ├── auth.ts                               # NextAuth config
│   ├── queryClient.ts                        # TanStack Query client
│   ├── utils.ts                              # cn(), formatters
│   └── validators/
│       └── settingsSchema.ts
├── types/
│   └── admin.ts                              # All TypeScript interfaces
├── middleware.ts                             # Route protection
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
└── .env.local
```

---

## Documentation Index

| File | Description |
|---|---|
| [overview.md](./overview.md) | Setup, environment variables, NextAuth, middleware, layout, Axios, React Query |
| [pages.md](./pages.md) | Full TSX code for every page component |
| [components.md](./components.md) | Reusable component implementations |
| [realtime.md](./realtime.md) | WebSocket hook, SOS alarms, browser notifications |
| [api_integration.md](./api_integration.md) | Axios instance, all service functions, TypeScript types |

---

## Quick Start

```bash
cd admin-panel
npm install
cp .env.example .env.local   # fill in values
npm run dev                  # http://localhost:3000
```

Login with admin credentials. All dashboard routes auto-redirect to `/login` if unauthenticated.
