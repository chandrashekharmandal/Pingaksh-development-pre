import React from "react";
import { View, Text, Pressable, ActivityIndicator } from "react-native";
import { GuardDocument } from "@/types";

interface Props {
  document: GuardDocument | null;
  type: string;
  label: string;
  isUploading: boolean;
  onUpload: () => void;
}

export function DocumentUploadCard({ document, type, label, isUploading, onUpload }: Props) {
  const getStatusColor = () => {
    if (!document) return "bg-surface";
    switch (document.status) {
      case "verified": return "border-accent";
      case "rejected": return "border-danger";
      case "uploaded": return "border-warning";
      default: return "border-surface";
    }
  };

  const getStatusText = () => {
    if (!document) return "Not uploaded";
    switch (document.status) {
      case "verified": return "Verified ✓";
      case "rejected": return "Rejected";
      case "uploaded": return "Under review";
      default: return "Pending";
    }
  };

  return (
    <Pressable
      onPress={onUpload}
      disabled={isUploading || document?.status === "verified"}
      className={`bg-surface rounded-2xl p-4 border-2 ${getStatusColor()}`}
    >
      <View className="flex-row items-center justify-between">
        <View className="flex-1">
          <Text className="text-white font-semibold text-base">{label}</Text>
          <Text className={`text-sm mt-1 ${
            document?.status === "verified" ? "text-accent" :
            document?.status === "rejected" ? "text-danger" : "text-white/50"
          }`}>
            {getStatusText()}
          </Text>
          {document?.rejectionReason && (
            <Text className="text-danger/80 text-xs mt-1">{document.rejectionReason}</Text>
          )}
        </View>
        {isUploading ? (
          <ActivityIndicator color="#6C63FF" />
        ) : (
          <View className="w-10 h-10 rounded-full bg-primary/20 items-center justify-center">
            <Text className="text-primary text-lg">↑</Text>
          </View>
        )}
      </View>
    </Pressable>
  );
}
