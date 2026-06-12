import client from "../client";

interface OTPRequestResponse {
  message: string;
  session_id: string;
}

interface OTPVerifyResponse {
  access: string;
  refresh: string;
  user: {
    id: string;
    phone: string;
    name: string;
    email: string | null;
  };
}

interface TokenRefreshResponse {
  access: string;
  refresh?: string;
}

export const requestOTP = async (phone: string): Promise<OTPRequestResponse> => {
  const { data } = await client.post("/api/auth/otp/request/", { phone });
  return data;
};

export const verifyOTP = async (
  phone: string,
  otp: string
): Promise<OTPVerifyResponse> => {
  const { data } = await client.post("/api/auth/otp/verify/", { phone, otp });
  return data;
};

export const refreshToken = async (
  refresh: string
): Promise<TokenRefreshResponse> => {
  const { data } = await client.post("/api/auth/token/refresh/", { refresh });
  return data;
};
