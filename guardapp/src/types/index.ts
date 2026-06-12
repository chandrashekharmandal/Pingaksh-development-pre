export interface Guard {
  id: string;
  phone: string;
  firstName: string;
  lastName: string;
  avatar: string | null;
  isOnline: boolean;
  isVerified: boolean;
  verificationStatus: "pending" | "in_review" | "approved" | "rejected";
  rating: number;
  totalBookings: number;
  skills: string[];
  experience: number;
  createdAt: string;
}

export interface ActiveBooking {
  id: string;
  status: "accepted" | "en_route" | "arrived" | "started" | "completed";
  client: {
    id: string;
    name: string;
    phone: string;
    avatar: string | null;
  };
  location: {
    latitude: number;
    longitude: number;
    address: string;
  };
  scheduledAt: string;
  startedAt: string | null;
  completedAt: string | null;
  duration: number | null;
  rate: number;
  estimatedEarnings: number;
  notes: string | null;
}

export interface IncomingRequest {
  id: string;
  client: {
    name: string;
    avatar: string | null;
    rating: number;
  };
  location: {
    latitude: number;
    longitude: number;
    address: string;
    distance: number;
  };
  duration: number;
  rate: number;
  estimatedEarnings: number;
  expiresAt: string;
}

export interface EarningsSummary {
  today: number;
  thisWeek: number;
  thisMonth: number;
  total: number;
  completedToday: number;
  completedThisWeek: number;
  hoursWorkedToday: number;
  averageRating: number;
}

export interface Payout {
  id: string;
  amount: number;
  status: "pending" | "processing" | "completed" | "failed";
  requestedAt: string;
  completedAt: string | null;
  method: string;
}

export interface GuardDocument {
  id: string;
  type: "id_proof" | "police_verification" | "photo" | "address_proof";
  status: "pending" | "uploaded" | "verified" | "rejected";
  url: string | null;
  rejectionReason: string | null;
}

export interface BookingHistoryItem {
  id: string;
  clientName: string;
  clientAvatar: string | null;
  address: string;
  date: string;
  duration: number;
  earnings: number;
  rating: number | null;
  status: "completed" | "cancelled";
}

export interface LocationUpdate {
  bookingId: string;
  latitude: number;
  longitude: number;
  heading: number;
  speed: number;
  timestamp: number;
}

export interface WSMessage {
  type: string;
  payload: Record<string, unknown>;
}
