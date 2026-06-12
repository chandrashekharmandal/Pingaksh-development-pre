export interface AdminUser {
  id: string;
  email: string;
  name: string;
  role: "superadmin" | "admin" | "moderator";
  avatar?: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: AdminUser;
}

export interface Guard {
  id: string;
  name: string;
  email: string;
  phone: string;
  avatar?: string;
  tier: "bronze" | "silver" | "gold" | "platinum";
  status: "active" | "suspended" | "pending" | "offline";
  rating: number;
  total_bookings: number;
  earnings: number;
  verified: boolean;
  created_at: string;
  location?: { lat: number; lng: number };
}

export interface GuardDetail extends Guard {
  documents: Document[];
  stats: {
    completed_bookings: number;
    cancelled_bookings: number;
    avg_rating: number;
    total_hours: number;
  };
  recent_bookings: Booking[];
}

export interface Document {
  id: string;
  type: string;
  url: string;
  status: "pending" | "approved" | "rejected";
  uploaded_at: string;
  reviewed_at?: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  phone: string;
  avatar?: string;
  status: "active" | "suspended";
  total_bookings: number;
  total_spent: number;
  created_at: string;
}

export interface UserDetail extends User {
  recent_bookings: Booking[];
  payment_methods: number;
}

export interface Booking {
  id: string;
  user: { id: string; name: string; avatar?: string };
  guard: { id: string; name: string; avatar?: string };
  status: "pending" | "accepted" | "in_progress" | "completed" | "cancelled" | "disputed";
  start_time: string;
  end_time?: string;
  duration_hours: number;
  amount: number;
  platform_fee: number;
  guard_payout: number;
  location: { address: string; lat: number; lng: number };
  created_at: string;
}

export interface BookingDetail extends Booking {
  timeline: TimelineEvent[];
  payment_status: "pending" | "paid" | "refunded";
  notes?: string;
}

export interface TimelineEvent {
  id: string;
  event: string;
  timestamp: string;
  actor?: string;
}

export interface Transaction {
  id: string;
  booking_id: string;
  type: "payment" | "refund" | "payout";
  amount: number;
  status: "pending" | "completed" | "failed";
  method: string;
  created_at: string;
  user?: { id: string; name: string };
  guard?: { id: string; name: string };
}

export interface Payout {
  id: string;
  guard: { id: string; name: string };
  amount: number;
  status: "pending" | "approved" | "processing" | "completed" | "failed";
  period_start: string;
  period_end: string;
  created_at: string;
}

export interface SOSEvent {
  id: string;
  booking_id: string;
  user: { id: string; name: string; phone: string };
  guard?: { id: string; name: string; phone: string };
  status: "active" | "resolved" | "false_alarm";
  location: { address: string; lat: number; lng: number };
  triggered_at: string;
  resolved_at?: string;
  resolution_notes?: string;
}

export interface DashboardMetrics {
  total_users: number;
  total_guards: number;
  active_bookings: number;
  revenue_today: number;
  users_trend: number;
  guards_trend: number;
  bookings_trend: number;
  revenue_trend: number;
}

export interface HourlyBooking {
  hour: string;
  bookings: number;
}

export interface RevenueSummary {
  total_revenue: number;
  platform_fees: number;
  guard_payouts: number;
  pending_payouts: number;
  monthly_growth: number;
}

export interface AnalyticsData {
  labels: string[];
  datasets: { label: string; data: number[] }[];
}

export interface PeakHour {
  day: number;
  hour: number;
  value: number;
}

export interface VerificationItem {
  id: string;
  guard: { id: string; name: string; avatar?: string };
  document_type: string;
  document_url: string;
  submitted_at: string;
  status: "pending" | "approved" | "rejected";
}

export interface VerificationStats {
  pending: number;
  approved_today: number;
  rejected_today: number;
  avg_review_time: number;
}

export interface PlatformSettings {
  platform_fee_percent: number;
  bronze_rate: number;
  silver_rate: number;
  gold_rate: number;
  platinum_rate: number;
  payout_threshold: number;
  payout_frequency: "daily" | "weekly" | "biweekly";
  sos_auto_notify_police: boolean;
  max_booking_hours: number;
}

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next: string | null;
  previous: string | null;
}

export interface WebSocketMessage {
  type: string;
  payload: Record<string, unknown>;
}
