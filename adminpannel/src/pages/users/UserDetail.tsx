import { useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/StatusBadge";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { Skeleton } from "@/components/ui/skeleton";
import { useUserDetail, useSuspendUser } from "@/hooks/useQueries";
import { format } from "date-fns";

export default function UserDetail() {
  const { id } = useParams<{ id: string }>();
  const { data: user, isLoading } = useUserDetail(id!);
  const suspendMutation = useSuspendUser();

  if (isLoading) return <div className="space-y-4">{Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-32" />)}</div>;
  if (!user) return <p className="text-muted-foreground">User not found</p>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{user.name}</h1>
          <p className="text-sm text-muted-foreground">{user.email} | {user.phone}</p>
          <p className="text-xs text-muted-foreground">Joined {format(new Date(user.created_at), "MMM d, yyyy")}</p>
        </div>
        <div className="flex items-center gap-2">
          <StatusBadge status={user.status} />
          {user.status === "active" && (
            <ConfirmDialog
              trigger={<Button size="sm" variant="destructive">Suspend</Button>}
              title="Suspend User"
              description="This user will be unable to create new bookings."
              confirmLabel="Suspend"
              variant="destructive"
              onConfirm={() => suspendMutation.mutate(id!)}
            />
          )}
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card><CardContent className="pt-6"><p className="text-2xl font-bold">{user.total_bookings}</p><p className="text-xs text-muted-foreground">Total Bookings</p></CardContent></Card>
        <Card><CardContent className="pt-6"><p className="text-2xl font-bold">${user.total_spent.toLocaleString()}</p><p className="text-xs text-muted-foreground">Total Spent</p></CardContent></Card>
        <Card><CardContent className="pt-6"><p className="text-2xl font-bold">{user.payment_methods}</p><p className="text-xs text-muted-foreground">Payment Methods</p></CardContent></Card>
      </div>

      <Card>
        <CardHeader><CardTitle className="text-base">Recent Bookings</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-2">
            {user.recent_bookings.map((b) => (
              <div key={b.id} className="flex items-center justify-between rounded-md border p-3">
                <div>
                  <p className="text-sm font-medium">Guard: {b.guard.name}</p>
                  <p className="text-xs text-muted-foreground">{format(new Date(b.start_time), "MMM d, yyyy HH:mm")}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium">${b.amount}</p>
                  <StatusBadge status={b.status} />
                </div>
              </div>
            ))}
            {user.recent_bookings.length === 0 && <p className="text-sm text-muted-foreground">No bookings yet</p>}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
