import client from "../client";

interface SOSResponse {
  id: string;
  status: string;
  message: string;
}

export const triggerSOS = async (
  bookingId: string,
  lat: number,
  lng: number
): Promise<SOSResponse> => {
  const { data } = await client.post("/api/sos/trigger/", {
    booking_id: bookingId,
    latitude: lat,
    longitude: lng,
  });
  return data;
};
