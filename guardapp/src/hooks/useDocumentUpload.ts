import { useState, useCallback } from "react";
import * as ImagePicker from "expo-image-picker";
import { documentsService } from "@/api/services/documents";

interface UploadState {
  isUploading: boolean;
  progress: number;
  error: string | null;
}

export function useDocumentUpload() {
  const [state, setState] = useState<UploadState>({
    isUploading: false,
    progress: 0,
    error: null,
  });

  const pickAndUpload = useCallback(async (documentType: string) => {
    setState({ isUploading: true, progress: 0, error: null });

    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        quality: 0.8,
        allowsEditing: true,
      });

      if (result.canceled) {
        setState({ isUploading: false, progress: 0, error: null });
        return null;
      }

      const asset = result.assets[0];
      const filename = `${documentType}_${Date.now()}.jpg`;
      const contentType = "image/jpeg";

      setState((s) => ({ ...s, progress: 0.2 }));

      const { uploadUrl, key, documentId } = await documentsService.getUploadURL(filename, contentType);

      setState((s) => ({ ...s, progress: 0.4 }));

      const fileResponse = await fetch(asset.uri);
      const blob = await fileResponse.blob();

      await fetch(uploadUrl, {
        method: "PUT",
        headers: { "Content-Type": contentType },
        body: blob,
      });

      setState((s) => ({ ...s, progress: 0.8 }));

      const doc = await documentsService.confirmUpload(documentId, key);

      setState({ isUploading: false, progress: 1, error: null });
      return doc;
    } catch (error: any) {
      setState({ isUploading: false, progress: 0, error: error.message || "Upload failed" });
      return null;
    }
  }, []);

  return { ...state, pickAndUpload };
}
