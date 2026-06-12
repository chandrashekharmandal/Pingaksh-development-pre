import { apiClient } from "../client";
import { GuardDocument } from "@/types";

export const documentsService = {
  getDocuments: async (): Promise<GuardDocument[]> => {
    const { data } = await apiClient.get("/api/guards/me/documents/");
    return data;
  },

  getUploadURL: async (filename: string, contentType: string): Promise<{ uploadUrl: string; key: string; documentId: string }> => {
    const { data } = await apiClient.post("/api/guards/me/documents/upload-url/", { filename, contentType });
    return data;
  },

  confirmUpload: async (documentId: string, s3Key: string): Promise<GuardDocument> => {
    const { data } = await apiClient.post(`/api/guards/me/documents/${documentId}/confirm/`, { s3Key });
    return data;
  },
};
