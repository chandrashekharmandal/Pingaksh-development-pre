import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { type ColumnDef } from "@tanstack/react-table";
import { DataTable } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { Input } from "@/components/ui/input";
import { useUsers } from "@/hooks/useQueries";
import type { User } from "@/types";
import { format } from "date-fns";

const columns: ColumnDef<User, unknown>[] = [
  { accessorKey: "name", header: "Name", cell: ({ row }) => <span className="font-medium">{row.original.name}</span> },
  { accessorKey: "email", header: "Email" },
  { accessorKey: "status", header: "Status", cell: ({ row }) => <StatusBadge status={row.original.status} /> },
  { accessorKey: "total_bookings", header: "Bookings" },
  { accessorKey: "total_spent", header: "Spent", cell: ({ row }) => <span>${row.original.total_spent.toLocaleString()}</span> },
  { accessorKey: "created_at", header: "Joined", cell: ({ row }) => format(new Date(row.original.created_at), "MMM d, yyyy") },
];

export default function UsersList() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const { data, isLoading } = useUsers({ page, search: search || undefined });

  return (
    <div className="space-y-6">
      <PageHeader title="Users" description="Manage platform users" />
      <Input placeholder="Search users..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} className="w-64" />
      <div onClick={(e) => {
        const row = (e.target as HTMLElement).closest("tr");
        if (row) {
          const idx = row.rowIndex - 1;
          if (data?.results[idx]) navigate(`/users/${data.results[idx].id}`);
        }
      }} className="cursor-pointer">
        <DataTable columns={columns} data={data?.results || []} totalCount={data?.count || 0} page={page} onPageChange={setPage} isLoading={isLoading} />
      </div>
    </div>
  );
}
