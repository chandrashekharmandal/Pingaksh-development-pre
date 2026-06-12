import { useState } from "react";
import { type ColumnDef } from "@tanstack/react-table";
import { DollarSign, TrendingUp, Wallet, Clock } from "lucide-react";
import { KPICard } from "@/components/KPICard";
import { DataTable } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { useTransactions, useRevenueSummary, usePayouts, useApprovePayout, useBulkApprovePayouts } from "@/hooks/useQueries";
import type { Transaction, Payout } from "@/types";
import { format } from "date-fns";

const txColumns: ColumnDef<Transaction, unknown>[] = [
  { accessorKey: "id", header: "ID", cell: ({ row }) => <span className="font-mono text-xs">{row.original.id.slice(0, 8)}</span> },
  { accessorKey: "type", header: "Type", cell: ({ row }) => <span className="capitalize">{row.original.type}</span> },
  { accessorKey: "amount", header: "Amount", cell: ({ row }) => `$${row.original.amount}` },
  { accessorKey: "status", header: "Status", cell: ({ row }) => <StatusBadge status={row.original.status} /> },
  { accessorKey: "method", header: "Method" },
  { accessorKey: "created_at", header: "Date", cell: ({ row }) => format(new Date(row.original.created_at), "MMM d, HH:mm") },
];

const payoutColumns: ColumnDef<Payout, unknown>[] = [
  { accessorKey: "guard.name", header: "Guard", cell: ({ row }) => row.original.guard.name },
  { accessorKey: "amount", header: "Amount", cell: ({ row }) => `$${row.original.amount}` },
  { accessorKey: "status", header: "Status", cell: ({ row }) => <StatusBadge status={row.original.status} /> },
  { accessorKey: "period_end", header: "Period", cell: ({ row }) => format(new Date(row.original.period_end), "MMM d") },
  { id: "actions", header: "", cell: ({ row }) => row.original.status === "pending" ? <ApproveBtn id={row.original.id} /> : null },
];

function ApproveBtn({ id }: { id: string }) {
  const mutation = useApprovePayout();
  return <Button size="sm" variant="outline" onClick={() => mutation.mutate(id)} disabled={mutation.isPending}>Approve</Button>;
}

export default function Payments() {
  const [txPage, setTxPage] = useState(1);
  const [payoutPage, setPayoutPage] = useState(1);
  const { data: revenue } = useRevenueSummary();
  const { data: txData, isLoading: txLoading } = useTransactions({ page: txPage });
  const { data: payoutData, isLoading: payoutLoading } = usePayouts({ page: payoutPage });
  const bulkApprove = useBulkApprovePayouts();

  const pendingPayouts = payoutData?.results.filter((p) => p.status === "pending") || [];

  return (
    <div className="space-y-6">
      <PageHeader title="Payments" description="Revenue and payouts management" />

      <div className="grid gap-4 md:grid-cols-4">
        <KPICard icon={DollarSign} value={`$${revenue?.total_revenue?.toLocaleString() || "0"}`} label="Total Revenue" />
        <KPICard icon={TrendingUp} value={`$${revenue?.platform_fees?.toLocaleString() || "0"}`} label="Platform Fees" />
        <KPICard icon={Wallet} value={`$${revenue?.guard_payouts?.toLocaleString() || "0"}`} label="Guard Payouts" />
        <KPICard icon={Clock} value={`$${revenue?.pending_payouts?.toLocaleString() || "0"}`} label="Pending Payouts" />
      </div>

      <Tabs defaultValue="transactions">
        <TabsList>
          <TabsTrigger value="transactions">Transactions</TabsTrigger>
          <TabsTrigger value="payouts">Payouts</TabsTrigger>
        </TabsList>
        <TabsContent value="transactions">
          <DataTable columns={txColumns} data={txData?.results || []} totalCount={txData?.count || 0} page={txPage} onPageChange={setTxPage} isLoading={txLoading} />
        </TabsContent>
        <TabsContent value="payouts">
          {pendingPayouts.length > 1 && (
            <div className="mb-4">
              <Button size="sm" onClick={() => bulkApprove.mutate(pendingPayouts.map((p) => p.id))} disabled={bulkApprove.isPending}>
                Approve All Pending ({pendingPayouts.length})
              </Button>
            </div>
          )}
          <DataTable columns={payoutColumns} data={payoutData?.results || []} totalCount={payoutData?.count || 0} page={payoutPage} onPageChange={setPayoutPage} isLoading={payoutLoading} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
