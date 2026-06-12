import React, { useState } from "react";
import {
  View,
  Text,
  Pressable,
  FlatList,
  TextInput,
  ActivityIndicator,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useWallet, useTransactions } from "@/hooks/useWallet";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { initiateTopUp } from "@/api/services/wallet";
import * as Haptics from "expo-haptics";

export default function WalletScreen() {
  const { data: wallet, isLoading: walletLoading } = useWallet();
  const { data: transactions, isLoading: txLoading } = useTransactions();
  const [topUpAmount, setTopUpAmount] = useState("");
  const [showTopUp, setShowTopUp] = useState(false);
  const queryClient = useQueryClient();

  const topUpMutation = useMutation({
    mutationFn: (amount: number) => initiateTopUp(amount),
    onSuccess: () => {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      queryClient.invalidateQueries({ queryKey: ["wallet"] });
      setShowTopUp(false);
      setTopUpAmount("");
    },
  });

  const quickAmounts = [500, 1000, 2000, 5000];

  return (
    <SafeAreaView className="flex-1 bg-secondary">
      <View className="px-4 pt-4">
        <Text className="text-white text-2xl font-bold mb-6">Wallet</Text>

        <View className="bg-surface rounded-2xl p-6 mb-6">
          <Text className="text-gray-400 text-sm">Available Balance</Text>
          {walletLoading ? (
            <ActivityIndicator color="#6C63FF" className="mt-2" />
          ) : (
            <Text className="text-white text-4xl font-bold mt-1">
              ₹{wallet?.balance.toLocaleString() || "0"}
            </Text>
          )}
          <Pressable
            onPress={() => setShowTopUp(!showTopUp)}
            className="bg-primary rounded-full py-3 mt-4 items-center"
          >
            <Text className="text-white font-semibold">
              {showTopUp ? "Cancel" : "Add Money"}
            </Text>
          </Pressable>
        </View>

        {showTopUp && (
          <View className="bg-surface rounded-2xl p-4 mb-6">
            <Text className="text-white font-medium mb-3">Top Up Amount</Text>
            <View className="flex-row flex-wrap gap-2 mb-4">
              {quickAmounts.map((amount) => (
                <Pressable
                  key={amount}
                  onPress={() => setTopUpAmount(String(amount))}
                  className={`px-4 py-2 rounded-full ${
                    topUpAmount === String(amount)
                      ? "bg-primary"
                      : "bg-secondary"
                  }`}
                >
                  <Text className="text-white text-sm">₹{amount}</Text>
                </Pressable>
              ))}
            </View>
            <TextInput
              className="bg-secondary rounded-xl px-4 py-3 text-white text-lg mb-4"
              placeholder="Enter amount"
              placeholderTextColor="#6B7280"
              keyboardType="number-pad"
              value={topUpAmount}
              onChangeText={setTopUpAmount}
            />
            <Pressable
              onPress={() => topUpMutation.mutate(Number(topUpAmount))}
              disabled={!topUpAmount || topUpMutation.isPending}
              className={`rounded-full py-3 items-center ${
                topUpAmount ? "bg-accent" : "bg-accent/40"
              }`}
            >
              <Text className="text-white font-semibold">
                {topUpMutation.isPending ? "Processing..." : "Proceed to Pay"}
              </Text>
            </Pressable>
          </View>
        )}

        <Text className="text-white font-bold text-lg mb-3">Transactions</Text>
      </View>

      {txLoading ? (
        <ActivityIndicator color="#6C63FF" className="mt-4" />
      ) : (
        <FlatList
          data={transactions?.results || []}
          keyExtractor={(item) => item.id}
          contentContainerStyle={{ paddingHorizontal: 16 }}
          renderItem={({ item }) => (
            <View className="flex-row items-center justify-between py-3 border-b border-gray-700/30">
              <View className="flex-1">
                <Text className="text-white text-sm">{item.description}</Text>
                <Text className="text-gray-500 text-xs mt-1">
                  {new Date(item.created_at).toLocaleDateString("en-IN", {
                    day: "numeric",
                    month: "short",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </Text>
              </View>
              <Text
                className={`font-bold ${
                  item.type === "credit" ? "text-accent" : "text-danger"
                }`}
              >
                {item.type === "credit" ? "+" : "-"}₹{item.amount}
              </Text>
            </View>
          )}
          ListEmptyComponent={
            <View className="items-center py-8">
              <Text className="text-gray-400">No transactions yet</Text>
            </View>
          }
          showsVerticalScrollIndicator={false}
        />
      )}
    </SafeAreaView>
  );
}
