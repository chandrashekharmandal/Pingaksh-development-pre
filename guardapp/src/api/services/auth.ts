import { apiClient } from "../client";

interface OTPRequestResponse {
  message: string;
  sessionId: string;
}

interface OTPVerifyResponse {
  access: string;
  refresh: string;
  isNewUser: boolean;
  onboardingComplete: boolean;
}

export const authService = {
  requestOTP: async (phone: string): Promise<OTPRequestResponse> => {
    const { data } = await apiClient.post("/api/auth/guard/otp/request/", { phone });
    return data;
  },

  verifyOTP: async (phone: string, otp: string): Promise<OTPVerifyResponse> => {
    const { data } = await apiClient.post("/api/auth/guard/otp/verify/", { phone, otp });
    return data;
  },
};
