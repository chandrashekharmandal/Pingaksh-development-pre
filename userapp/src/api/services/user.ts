import client from "../client";
import { User } from "@/types";

interface UpdateProfileData {
  name?: string;
  email?: string;
  avatar?: string;
}

export const getProfile = async (): Promise<User> => {
  const { data } = await client.get("/api/users/me/");
  return data;
};

export const updateProfile = async (
  profileData: UpdateProfileData
): Promise<User> => {
  const { data } = await client.patch("/api/users/me/", profileData);
  return data;
};

export const registerPushToken = async (
  token: string
): Promise<{ message: string }> => {
  const { data } = await client.post("/api/notifications/push-token/", {
    token,
    platform: "expo",
  });
  return data;
};
