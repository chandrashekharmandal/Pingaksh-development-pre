import client from "../client";
import { Guard, GuardReview } from "@/types";

interface NearbyGuardsResponse {
  results: Guard[];
  count: number;
}

interface GuardReviewsResponse {
  results: GuardReview[];
  count: number;
  next: string | null;
}

export const getNearbyGuards = async (
  lat: number,
  lng: number,
  radius: number = 5
): Promise<NearbyGuardsResponse> => {
  const { data } = await client.get("/api/guards/nearby/", {
    params: { lat, lng, radius },
  });
  return data;
};

export const getGuardProfile = async (id: string): Promise<Guard> => {
  const { data } = await client.get(`/api/guards/${id}/`);
  return data;
};

export const getGuardReviews = async (
  id: string,
  page: number = 1
): Promise<GuardReviewsResponse> => {
  const { data } = await client.get(`/api/guards/${id}/reviews/`, {
    params: { page },
  });
  return data;
};
