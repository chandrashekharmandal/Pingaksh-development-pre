import React, { useState } from "react";
import { View, Text, Pressable, ScrollView } from "react-native";
import { router } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { useDocumentUpload } from "@/hooks/useDocumentUpload";
import { DocumentUploadCard } from "@/components/DocumentUploadCard";
import { GuardDocument } from "@/types";

const REQUIRED_DOCS = [
  { type: "id_proof", label: "Government ID (Aadhaar/PAN)" },
  { type: "police_verification", label: "Police Verification Certificate" },
  { type: "photo", label: "Professional Photo" },
];

export default function DocumentsScreen() {
  const { isUploading, pickAndUpload } = useDocumentUpload();
  const [uploadedDocs, setUploadedDocs] = useState<Record<string, GuardDocument>>({});
  const [uploadingType, setUploadingType] = useState<string | null>(null);

  const handleUpload = async (type: string) => {
    setUploadingType(type);
    const doc = await pickAndUpload(type);
    if (doc) {
      setUploadedDocs((prev) => ({ ...prev, [type]: doc }));
    }
    setUploadingType(null);
  };

  const allUploaded = REQUIRED_DOCS.every((d) => uploadedDocs[d.type]);

  return (
    <SafeAreaView className="flex-1 bg-secondary">
      <ScrollView className="flex-1 px-6 pt-8">
        <Text className="text-white text-2xl font-bold mb-2">Documents</Text>
        <Text className="text-white/50 mb-8">Upload required documents for verification</Text>

        <View className="gap-4">
          {REQUIRED_DOCS.map((doc) => (
            <DocumentUploadCard
              key={doc.type}
              type={doc.type}
              label={doc.label}
              document={uploadedDocs[doc.type] || null}
              isUploading={uploadingType === doc.type}
              onUpload={() => handleUpload(doc.type)}
            />
          ))}
        </View>

        <Pressable
          onPress={() => router.push("/onboarding/complete")}
          disabled={!allUploaded}
          className={`rounded-2xl py-4 items-center mt-8 mb-8 ${
            allUploaded ? "bg-primary" : "bg-primary/30"
          } active:opacity-80`}
        >
          <Text className="text-white font-bold text-base">Submit for Review</Text>
        </Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}
