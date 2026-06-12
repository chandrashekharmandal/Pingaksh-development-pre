export enum BookingStatus {
  PENDING = "pending",
  CONFIRMED = "confirmed",
  ACTIVE = "active",
  COMPLETED = "completed",
  CANCELLED = "cancelled",
}

export enum GuardTier {
  STANDARD = "standard",
  PREMIUM = "premium",
  ELITE = "elite",
}

export interface User {
  id: string;
  phone: string;
  name: string;
  email: string | null;
  avatar: string | null;
  is_verified: boolean;
  created_at: string;
}

export interface Guard {
  id: string;
  name: string;
  avatar: string | null;
  phone: string;
  tier: GuardTier;
  rating: number;
  total_reviews: number;
  hourly_rate: number;
  is_available: boolean;
  latitude: number;
  longitude: number;
  distance_km: number;
  experience_years: number;
  verified: boolean;
  skills: string[];
}

export interface GuardReview {
  id: string;
  user_name: string;
  rating: number;
  comment: string;
  created_at: string;
}

export interface Booking {
  id: string;
  guard: Guard;
  user: User;
  status: BookingStatus;
  start_time: string;
  end_time: string | null;
  duration_hours: number;
  location_lat: number;
  location_lng: number;
  location_address: string;
  total_amount: number;
  notes: string | null;
  created_at: string;
  guard_lat: number | null;
  guard_lng: number | null;
}

export interface Wallet {
  id: string;
  balance: number;
  currency: string;
}

export interface Transaction {
  id: string;
  type: "credit" | "debit";
  amount: number;
  description: string;
  created_at: string;
  reference_id: string | null;
}

export interface LocationCoords {
  latitude: number;
  longitude: number;
}

export interface WebSocketMessage {
  type: string;
  data: Record<string, unknown>;
}
