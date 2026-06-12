import { apiClient } from "../client";

export const onboardingService = {
  submitPersonalInfo: async (data: {
    firstName: string;
    lastName: string;
    skills: string[];
    experience: number;
    dateOfBirth: string;
    address: string;
  }) => {
    const { data: response } = await apiClient.post("/api/guards/onboarding/personal/", data);
    return response;
  },

  submitForReview: async () => {
    const { data } = await apiClient.post("/api/guards/onboarding/submit/");
    return data;
  },

  getVerificationStatus: async (): Promise<{
    status: "pending" | "in_review" | "approved" | "rejected";
    message: string | null;
  }> => {
    const { data } = await apiClient.get("/api/guards/me/verification-status/");
    return data;
  },
};
