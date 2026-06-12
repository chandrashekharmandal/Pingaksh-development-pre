import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { type ColumnDef } from "@tanstack/react-table";
import { DataTable } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { Input } from "@/components/ui/input";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { ExportButton } from "@/components/ExportButton";
import { useGuards } from "@/hooks/useQueries";
import type { Guard } from "@/types";

const columns: ColumnDef<Guard, unknown>[] = [
  { accessorKey: "name", header: "Name", cell: ({ row }) => <span className="font-medium">{row.original.name}</span> },
  { accessorKey: "tier", header: "Tier", cell: ({ row }) => <span className="capitalize text-primary">{row.original.tier}</span> },
  { accessorKey: "status", header: "Status", cell: ({ row }) => <StatusBadge status={row.original.status} /> },
  { accessorKey: "rating", header: "Rating", cell: ({ row }) => <span>{row.original.rating.toFixed(1)}</span> },
  { accessorKey: "total_bookings", header: "Bookings" },
  { accessorKey: "earnings", header: "Earnings", cell: ({ row }) => <span>${row.original.earnings.toLocaleString()}</span> },
];

export default function GuardsList() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [tier, setTier] = useState("");
  const [status, setStatus] = useState("");

  const { data, isLoading } = useGuards({ page, search: search || undefined, tier: tier || undefined, status: status || undefined });

  return (
    <div className="space-y-6">
      <PageHeader title="Guards" description="Manage security guards" action={<ExportButton data={(data?.results || []) as unknown as Record<string, unknown>[]} filename="guards" />} />
      <div className="flex flex-wrap items-center gap-3">
        <Input placeholder="Search guards..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} className="w-64" />
        <Select value={tier} onValueChange={(v) => { setTier(v); setPage(1); }}>
          <SelectTrigger className="w-36"><SelectValue placeholder="All Tiers" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Tiers</SelectItem>
            <SelectItem value="bronze">Bronze</SelectItem>
            <SelectItem value="silver">Silver</SelectItem>
            <SelectItem value="gold">Gold</SelectItem>
            <SelectItem value="platinum">Platinum</SelectItem>
          </SelectContent>
        </Select>
        <Select value={status} onValueChange={(v) => { setStatus(v); setPage(1); }}>
          <SelectTrigger className="w-36"><SelectValue placeholder="All Status" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Status</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="suspended">Suspended</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div onClick={(e) => {
        const row = (e.target as HTMLElement).closest("tr");
        if (row) {
          const idx = row.rowIndex - 1;
          if (data?.results[idx]) navigate(`/guards/${data.results[idx].id}`);
        }
      }} className="cursor-pointer">
        <DataTable columns={columns} data={data?.results || []} totalCount={data?.count || 0} page={page} onPageChange={setPage} isLoading={isLoading} />
      </div>
    </div>
  );
}
