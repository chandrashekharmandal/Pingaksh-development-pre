import { useState } from "react";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { PageHeader } from "@/components/PageHeader";
import { useBookingAnalytics, useRevenueAnalytics, useGuardAnalytics, usePeakHours } from "@/hooks/useQueries";
import { cn } from "@/lib/utils";

const COLORS = ["hsl(263 70% 50%)", "hsl(160 100% 42%)", "hsl(0 84.2% 60.2%)", "#f59e0b"];

export default function Analytics() {
  const [period, setPeriod] = useState("30d");
  const { data: bookingData } = useBookingAnalytics(period);
  const { data: revenueData } = useRevenueAnalytics(period);
  const { data: guardData } = useGuardAnalytics();
  const { data: peakHours } = usePeakHours();

  const chartData = bookingData?.labels.map((label, i) => ({
    name: label,
    bookings: bookingData.datasets[0]?.data[i] || 0,
  })) || [];

  const revenueChartData = revenueData?.labels.map((label, i) => ({
    name: label,
    revenue: revenueData.datasets[0]?.data[i] || 0,
  })) || [];

  const guardPieData = guardData?.labels.map((label, i) => ({
    name: label,
    value: guardData.datasets[0]?.data[i] || 0,
  })) || [];

  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const hours = Array.from({ length: 24 }, (_, i) => i);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Analytics"
        description="Platform performance insights"
        action={
          <Select value={period} onValueChange={setPeriod}>
            <SelectTrigger className="w-28"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">7 days</SelectItem>
              <SelectItem value="30d">30 days</SelectItem>
              <SelectItem value="90d">90 days</SelectItem>
            </SelectContent>
          </Select>
        }
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle className="text-base">Bookings Over Time</CardTitle></CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(217.2 32.6% 17.5%)" />
                  <XAxis dataKey="name" stroke="hsl(215 20.2% 65.1%)" fontSize={12} />
                  <YAxis stroke="hsl(215 20.2% 65.1%)" fontSize={12} />
                  <Tooltip contentStyle={{ backgroundColor: "hsl(222.2 84% 6.9%)", border: "1px solid hsl(217.2 32.6% 17.5%)", borderRadius: "8px" }} />
                  <Line type="monotone" dataKey="bookings" stroke="hsl(263 70% 50%)" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-base">Revenue</CardTitle></CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={revenueChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(217.2 32.6% 17.5%)" />
                  <XAxis dataKey="name" stroke="hsl(215 20.2% 65.1%)" fontSize={12} />
                  <YAxis stroke="hsl(215 20.2% 65.1%)" fontSize={12} />
                  <Tooltip contentStyle={{ backgroundColor: "hsl(222.2 84% 6.9%)", border: "1px solid hsl(217.2 32.6% 17.5%)", borderRadius: "8px" }} />
                  <Bar dataKey="revenue" fill="hsl(160 100% 42%)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-base">Guards by Tier</CardTitle></CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={guardPieData} cx="50%" cy="50%" outerRadius={80} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                    {guardPieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: "hsl(222.2 84% 6.9%)", border: "1px solid hsl(217.2 32.6% 17.5%)", borderRadius: "8px" }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-base">Peak Hours Heatmap</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-1">
              <div className="flex gap-1 pl-10">
                {hours.filter((h) => h % 3 === 0).map((h) => (
                  <span key={h} className="w-6 text-center text-[10px] text-muted-foreground">{h}</span>
                ))}
              </div>
              {days.map((day, dayIdx) => (
                <div key={day} className="flex items-center gap-1">
                  <span className="w-8 text-xs text-muted-foreground">{day}</span>
                  {hours.map((hour) => {
                    const peak = peakHours?.find((p) => p.day === dayIdx && p.hour === hour);
                    const intensity = peak ? Math.min(peak.value / 100, 1) : 0;
                    return (
                      <div
                        key={hour}
                        className={cn("h-4 w-4 rounded-sm", intensity === 0 ? "bg-muted" : "")}
                        style={intensity > 0 ? { backgroundColor: `hsla(263, 70%, 50%, ${intensity})` } : undefined}
                        title={`${day} ${hour}:00 - ${peak?.value || 0} bookings`}
                      />
                    );
                  })}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
