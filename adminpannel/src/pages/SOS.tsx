import { useState } from "react";
import { type ColumnDef } from "@tanstack/react-table";
import { PageHeader } from "@/components/PageHeader";
import { SOSEventCard } from "@/components/SOSEventCard";
import { DataTable } from "@/components/DataTable";
import { StatusBadge } from "@/components/StatusBadge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useActiveSOS, useSOSHistory, useResolveSOS } from "@/hooks/useQueries";
import type { SOSEvent } from "@/types";
import { format } from "date-fns";

const columns: ColumnDef<SOSEvent, unknown>[] = [
  { accessorKey: "user.name", header: "User", cell: ({ row }) => row.original.user.name },
  { accessorKey: "location.address", header: "Location", cell: ({ row }) => <span className="max-w-[200px] truncate">{row.original.location.address}</span> },
  { accessorKey: "status", header: "Status", cell: ({ row }) => <StatusBadge status={row.original.status} /> },
  { accessorKey: "triggered_at", header: "Triggered", cell: ({ row }) => format(new Date(row.original.triggered_at), "MMM d, HH:mm") },
  { accessorKey: "resolved_at", header: "Resolved", cell: ({ row }) => row.original.resolved_at ? format(new Date(row.original.resolved_at), "HH:mm") : "-" },
];

export default function SOS() {
  const [page, setPage] = useState(1);
  const { data: active } = useActiveSOS();
  const { data: history, isLoading } = useSOSHistory({ page });
  const resolveMutation = useResolveSOS();

  return (
    <div className="space-y-6">
      <PageHeader title="SOS Alerts" description="Monitor and resolve emergency alerts" />

      {active && active.length > 0 && (
        <Card className="border-destructive/30">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base text-destructive">
              <span className="h-2 w-2 animate-pulse rounded-full bg-destructive" />
              Active Alerts ({active.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {active.map((event) => (
              <SOSEventCard key={event.id} event={event} onResolve={(id, notes) => resolveMutation.mutate({ id, notes })} />
            ))}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader><CardTitle className="text-base">History</CardTitle></CardHeader>
        <CardContent>
          <DataTable columns={columns} data={history?.results || []} totalCount={history?.count || 0} page={page} onPageChange={setPage} isLoading={isLoading} />
        </CardContent>
      </Card>
    </div>
  );
}
