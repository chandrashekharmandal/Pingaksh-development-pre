import { useParams } from "react-router-dom";
import { Star, MapPin, Calendar, DollarSign } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/StatusBadge";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { useGuardDetail, useSuspendGuard, useApproveGuard, useChangeGuardTier } from "@/hooks/useQueries";

export default function GuardDetail() {
  const { id } = useParams<{ id: string }>();
  const { data: guard, isLoading } = useGuardDetail(id!);
  const suspendMutation = useSuspendGuard();
  const approveMutation = useApproveGuard();
  const tierMutation = useChangeGuardTier();

  if (isLoading) return <div className="space-y-4">{Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-32" />)}</div>;
  if (!guard) return <p className="text-muted-foreground">Guard not found</p>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{guard.name}</h1>
          <p className="text-sm text-muted-foreground">{guard.email} | {guard.phone}</p>
        </div>
        <div className="flex items-center gap-2">
          <StatusBadge status={guard.status} />
          {guard.status === "pending" && (
            <Button size="sm" onClick={() => approveMutation.mutate(id!)}>Approve</Button>
          )}
          {guard.status === "active" && (
            <ConfirmDialog
              trigger={<Button size="sm" variant="destructive">Suspend</Button>}
              title="Suspend Guard"
              description="This will prevent the guard from receiving new bookings."
              confirmLabel="Suspend"
              variant="destructive"
              onConfirm={() => suspendMutation.mutate(id!)}
            />
          )}
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="flex items-center gap-3 pt-6">
            <Star className="h-5 w-5 text-yellow-400" />
            <div>
              <p className="text-2xl font-bold">{guard.rating.toFixed(1)}</p>
              <p className="text-xs text-muted-foreground">Rating</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-3 pt-6">
            <Calendar className="h-5 w-5 text-primary" />
            <div>
              <p className="text-2xl font-bold">{guard.stats.completed_bookings}</p>
              <p className="text-xs text-muted-foreground">Completed</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-3 pt-6">
            <DollarSign className="h-5 w-5 text-accent" />
            <div>
              <p className="text-2xl font-bold">${guard.earnings.toLocaleString()}</p>
              <p className="text-xs text-muted-foreground">Earnings</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-3 pt-6">
            <MapPin className="h-5 w-5 text-muted-foreground" />
            <div>
              <p className="text-2xl font-bold">{guard.stats.total_hours}h</p>
              <p className="text-xs text-muted-foreground">Total Hours</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle className="text-base">Tier Management</CardTitle></CardHeader>
          <CardContent>
            <Select value={guard.tier} onValueChange={(v) => tierMutation.mutate({ id: id!, tier: v })}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="bronze">Bronze</SelectItem>
                <SelectItem value="silver">Silver</SelectItem>
                <SelectItem value="gold">Gold</SelectItem>
                <SelectItem value="platinum">Platinum</SelectItem>
              </SelectContent>
            </Select>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-base">Documents</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-2">
              {guard.documents.map((doc) => (
                <div key={doc.id} className="flex items-center justify-between rounded-md border p-2">
                  <span className="text-sm capitalize">{doc.type}</span>
                  <StatusBadge status={doc.status} />
                </div>
              ))}
              {guard.documents.length === 0 && <p className="text-sm text-muted-foreground">No documents uploaded</p>}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle className="text-base">Recent Bookings</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-2">
            {guard.recent_bookings.map((b) => (
              <div key={b.id} className="flex items-center justify-between rounded-md border p-3">
                <div>
                  <p className="text-sm font-medium">{b.user.name}</p>
                  <p className="text-xs text-muted-foreground">{b.location.address}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium">${b.amount}</p>
                  <StatusBadge status={b.status} />
                </div>
              </div>
            ))}
            {guard.recent_bookings.length === 0 && <p className="text-sm text-muted-foreground">No bookings yet</p>}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
