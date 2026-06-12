import { useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/StatusBadge";
import { BookingTimeline } from "@/components/BookingTimeline";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { Skeleton } from "@/components/ui/skeleton";
import { useBookingDetail, useForceCancelBooking, useRefundBooking } from "@/hooks/useQueries";
import { format } from "date-fns";

export default function BookingDetail() {
  const { id } = useParams<{ id: string }>();
  const { data: booking, isLoading } = useBookingDetail(id!);
  const cancelMutation = useForceCancelBooking();
  const refundMutation = useRefundBooking();

  if (isLoading) return <div className="space-y-4">{Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-32" />)}</div>;
  if (!booking) return <p className="text-muted-foreground">Booking not found</p>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Booking #{booking.id.slice(0, 8)}</h1>
          <p className="text-sm text-muted-foreground">{format(new Date(booking.start_time), "MMM d, yyyy HH:mm")}</p>
        </div>
        <div className="flex items-center gap-2">
          <StatusBadge status={booking.status} />
          {booking.status === "in_progress" && (
            <ConfirmDialog trigger={<Button size="sm" variant="destructive">Force Cancel</Button>} title="Force Cancel" description="This will immediately cancel the booking." confirmLabel="Cancel Booking" variant="destructive" onConfirm={() => cancelMutation.mutate(id!)} />
          )}
          {booking.payment_status === "paid" && booking.status !== "refunded" && (
            <ConfirmDialog trigger={<Button size="sm" variant="outline">Refund</Button>} title="Issue Refund" description="This will refund the full amount to the user." confirmLabel="Refund" onConfirm={() => refundMutation.mutate(id!)} />
          )}
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card>
          <CardHeader><CardTitle className="text-base">User</CardTitle></CardHeader>
          <CardContent>
            <p className="font-medium">{booking.user.name}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-base">Guard</CardTitle></CardHeader>
          <CardContent>
            <p className="font-medium">{booking.guard.name}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-base">Location</CardTitle></CardHeader>
          <CardContent>
            <p className="text-sm">{booking.location.address}</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle className="text-base">Amount Breakdown</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between"><span className="text-muted-foreground">Total</span><span className="font-medium">${booking.amount}</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">Platform Fee</span><span>${booking.platform_fee}</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">Guard Payout</span><span>${booking.guard_payout}</span></div>
            <div className="flex justify-between border-t pt-2"><span className="text-muted-foreground">Payment Status</span><StatusBadge status={booking.payment_status} /></div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-base">Timeline</CardTitle></CardHeader>
          <CardContent>
            <BookingTimeline events={booking.timeline} />
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle className="text-base">Tracking Map</CardTitle></CardHeader>
        <CardContent>
          <div className="flex h-48 items-center justify-center rounded-lg border border-dashed border-border">
            <p className="text-muted-foreground">Map tracking placeholder</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
