import { Users, Shield, CalendarCheck, DollarSign } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { KPICard } from "@/components/KPICard";
import { StatusBadge } from "@/components/StatusBadge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { useMetrics, useHourlyBookings, useRecentSOS } from "@/hooks/useQueries";
import { Skeleton } from "@/components/ui/skeleton";
import { format } from "date-fns";

export default function Dashboard() {
  const { data: metrics, isLoading: metricsLoading } = useMetrics();
  const { data: hourly } = useHourlyBookings();
  const { data: recentSOS } = useRecentSOS();

  if (metricsLoading) {
    return (
      <div className="space-y-6">
        <div className="grid gap-4 md:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-32" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <KPICard icon={Users} value={metrics?.total_users?.toLocaleString() || "0"} label="Total Users" trend={metrics?.users_trend} />
        <KPICard icon={Shield} value={metrics?.total_guards?.toLocaleString() || "0"} label="Total Guards" trend={metrics?.guards_trend} />
        <KPICard icon={CalendarCheck} value={metrics?.active_bookings?.toLocaleString() || "0"} label="Active Bookings" trend={metrics?.bookings_trend} />
        <KPICard icon={DollarSign} value={`$${metrics?.revenue_today?.toLocaleString() || "0"}`} label="Revenue Today" trend={metrics?.revenue_trend} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Hourly Bookings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={hourly || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(217.2 32.6% 17.5%)" />
                  <XAxis dataKey="hour" stroke="hsl(215 20.2% 65.1%)" fontSize={12} />
                  <YAxis stroke="hsl(215 20.2% 65.1%)" fontSize={12} />
                  <Tooltip contentStyle={{ backgroundColor: "hsl(222.2 84% 6.9%)", border: "1px solid hsl(217.2 32.6% 17.5%)", borderRadius: "8px" }} />
                  <Line type="monotone" dataKey="bookings" stroke="hsl(263 70% 50%)" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recent SOS Alerts</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>User</TableHead>
                  <TableHead>Time</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recentSOS?.slice(0, 5).map((sos) => (
                  <TableRow key={sos.id}>
                    <TableCell className="font-medium">{sos.user.name}</TableCell>
                    <TableCell className="text-muted-foreground">{format(new Date(sos.triggered_at), "HH:mm")}</TableCell>
                    <TableCell><StatusBadge status={sos.status} /></TableCell>
                  </TableRow>
                )) || (
                  <TableRow>
                    <TableCell colSpan={3} className="text-center text-muted-foreground">No recent alerts</TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Live Map</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex h-64 items-center justify-center rounded-lg border border-dashed border-border">
            <p className="text-muted-foreground">Map integration placeholder — connect Google Maps or Mapbox</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
