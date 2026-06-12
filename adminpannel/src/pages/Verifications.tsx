import { useState } from "react";
import { type ColumnDef } from "@tanstack/react-table";
import { FileCheck, Clock, CheckCircle, XCircle } from "lucide-react";
import { KPICard } from "@/components/KPICard";
import { DataTable } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { Button } from "@/components/ui/button";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { useVerificationQueue, useVerificationStats, useApproveDocument, useRejectDocument } from "@/hooks/useQueries";
import type { VerificationItem } from "@/types";
import { format } from "date-fns";

function ActionCell({ item }: { item: VerificationItem }) {
  const approveMutation = useApproveDocument();
  const rejectMutation = useRejectDocument();

  if (item.status !== "pending") return null;

  return (
    <div className="flex gap-1">
      <Button size="sm" variant="outline" className="text-accent" onClick={() => approveMutation.mutate(item.id)} disabled={approveMutation.isPending}>
        <CheckCircle className="mr-1 h-3 w-3" /> Approve
      </Button>
      <ConfirmDialog
        trigger={<Button size="sm" variant="ghost" className="text-destructive"><XCircle className="mr-1 h-3 w-3" /> Reject</Button>}
        title="Reject Document"
        description="Are you sure you want to reject this document?"
        confirmLabel="Reject"
        variant="destructive"
        onConfirm={() => rejectMutation.mutate({ id: item.id, reason: "Does not meet requirements" })}
      />
    </div>
  );
}

const columns: ColumnDef<VerificationItem, unknown>[] = [
  { accessorKey: "guard.name", header: "Guard", cell: ({ row }) => <span className="font-medium">{row.original.guard.name}</span> },
  { accessorKey: "document_type", header: "Document", cell: ({ row }) => <span className="capitalize">{row.original.document_type}</span> },
  { accessorKey: "status", header: "Status", cell: ({ row }) => <StatusBadge status={row.original.status} /> },
  { accessorKey: "submitted_at", header: "Submitted", cell: ({ row }) => format(new Date(row.original.submitted_at), "MMM d, HH:mm") },
  { id: "actions", header: "", cell: ({ row }) => <ActionCell item={row.original} /> },
];

export default function Verifications() {
  const [page, setPage] = useState(1);
  const { data: stats } = useVerificationStats();
  const { data, isLoading } = useVerificationQueue({ page });

  return (
    <div className="space-y-6">
      <PageHeader title="Verifications" description="Review guard document submissions" />

      <div className="grid gap-4 md:grid-cols-4">
        <KPICard icon={FileCheck} value={stats?.pending || 0} label="Pending Review" />
        <KPICard icon={CheckCircle} value={stats?.approved_today || 0} label="Approved Today" />
        <KPICard icon={XCircle} value={stats?.rejected_today || 0} label="Rejected Today" />
        <KPICard icon={Clock} value={`${stats?.avg_review_time || 0}m`} label="Avg Review Time" />
      </div>

      <DataTable columns={columns} data={data?.results || []} totalCount={data?.count || 0} page={page} onPageChange={setPage} isLoading={isLoading} />
    </div>
  );
}
