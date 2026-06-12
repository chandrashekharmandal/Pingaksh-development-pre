import client from "../client";
import { Wallet, Transaction } from "@/types";

interface TransactionsResponse {
  results: Transaction[];
  count: number;
  next: string | null;
}

interface TopUpInitiateResponse {
  order_id: string;
  amount: number;
  currency: string;
  razorpay_key: string;
}

export const getWallet = async (): Promise<Wallet> => {
  const { data } = await client.get("/api/payments/wallet/");
  return data;
};

export const getTransactions = async (
  page: number = 1
): Promise<TransactionsResponse> => {
  const { data } = await client.get("/api/payments/transactions/", {
    params: { page },
  });
  return data;
};

export const initiateTopUp = async (
  amount: number
): Promise<TopUpInitiateResponse> => {
  const { data } = await client.post("/api/payments/topup/initiate/", { amount });
  return data;
};

export const confirmTopUp = async (
  orderId: string,
  paymentId: string,
  signature: string
): Promise<{ message: string; balance: number }> => {
  const { data } = await client.post("/api/payments/topup/confirm/", {
    order_id: orderId,
    payment_id: paymentId,
    signature,
  });
  return data;
};
