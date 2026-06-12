import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { type ColumnDef } from "@tanstack/react-table";
import { DataTable } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { DateRangePicker } from "@/components/DateRangePicker";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { useBookings } from "@/hooks/useQueries";
import type { Booking } from "@/types";
import { format } from "date-fns";

const columns: ColumnDef<Booking, unknown>[] = [
  { accessorKey: "id", header: "ID", cell: ({ row }) => <span className="font-mono text-xs">{row.original.id.slice(0, 8)}</span> },
  { accessorKey: "user.name", header: "User", cell: ({ row }) => row.original.user.name },
  { accessorKey: "guard.name", header: "Guard", cell: ({ row }) => row.original.guard.name },
  { accessorKey: "status", header: "Status", cell: ({ row }) => <StatusBadge status={row.original.status} /> },
  { accessorKey: "amount", header: "Amount", cell: ({ row }) => `$${row.original.amount}` },
  { accessorKey: "start_time", header: "Date", cell: ({ row }) => format(new Date(row.original.start_time), "MMM d, HH:mm") },
];

export default function BookingsList() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const { data, isLoading } = useBookings({ page, status: status || undefined, date_from: dateFrom || undefined, date_to: dateTo || undefined });

  return (
    <div className="space-y-6">
      <PageHeader title="Bookings" description="View and manage all bookings" />
      <div className="flex flex-wrap items-center gap-3">
        <Select value={status} onValueChange={(v) => { setStatus(v); setPage(1); }}>
          <SelectTrigger className="w-40"><SelectValue placeholder="All Status" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Status</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="in_progress">In Progress</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="cancelled">Cancelled</SelectItem>
          </SelectContent>
        </Select>
        <DateRangePicker from={dateFrom} to={dateTo} onChange={(f, t) => { setDateFrom(f); setDateTo(t); setPage(1); }} />
      </div>
      <div onClick={(e) => {
        const row = (e.target as HTMLElement).closest("tr");
        if (row) {
          const idx = row.rowIndex - 1;
          if (data?.results[idx]) navigate(`/bookings/${data.results[idx].id}`);
        }
      }} className="cursor-pointer">
        <DataTable columns={columns} data={data?.results || []} totalCount={data?.count || 0} page={page} onPageChange={setPage} isLoading={isLoading} />
      </div>
    </div>
  );
}
