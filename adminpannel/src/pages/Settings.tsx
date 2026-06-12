import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { PageHeader } from "@/components/PageHeader";
import { Skeleton } from "@/components/ui/skeleton";
import { useSettings, useUpdateSettings } from "@/hooks/useQueries";
import type { PlatformSettings } from "@/types";

const schema = z.object({
  platform_fee_percent: z.coerce.number().min(0).max(100),
  bronze_rate: z.coerce.number().min(0),
  silver_rate: z.coerce.number().min(0),
  gold_rate: z.coerce.number().min(0),
  platinum_rate: z.coerce.number().min(0),
  payout_threshold: z.coerce.number().min(0),
  payout_frequency: z.enum(["daily", "weekly", "biweekly"]),
  sos_auto_notify_police: z.boolean(),
  max_booking_hours: z.coerce.number().min(1).max(24),
});

export default function Settings() {
  const { data: settings, isLoading } = useSettings();
  const updateMutation = useUpdateSettings();

  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm<PlatformSettings>({
    resolver: zodResolver(schema),
    values: settings,
  });

  const onSubmit = (data: PlatformSettings) => {
    updateMutation.mutate(data);
  };

  if (isLoading) return <div className="space-y-4">{Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-32" />)}</div>;

  return (
    <div className="space-y-6">
      <PageHeader title="Settings" description="Platform configuration" />
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <Card>
          <CardHeader><CardTitle className="text-base">Fee & Rates</CardTitle></CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm text-muted-foreground">Platform Fee (%)</label>
              <Input type="number" step="0.1" {...register("platform_fee_percent")} />
              {errors.platform_fee_percent && <p className="text-xs text-destructive">{errors.platform_fee_percent.message}</p>}
            </div>
            <div className="space-y-2">
              <label className="text-sm text-muted-foreground">Bronze Rate ($/hr)</label>
              <Input type="number" step="0.5" {...register("bronze_rate")} />
            </div>
            <div className="space-y-2">
              <label className="text-sm text-muted-foreground">Silver Rate ($/hr)</label>
              <Input type="number" step="0.5" {...register("silver_rate")} />
            </div>
            <div className="space-y-2">
              <label className="text-sm text-muted-foreground">Gold Rate ($/hr)</label>
              <Input type="number" step="0.5" {...register("gold_rate")} />
            </div>
            <div className="space-y-2">
              <label className="text-sm text-muted-foreground">Platinum Rate ($/hr)</label>
              <Input type="number" step="0.5" {...register("platinum_rate")} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-base">Payout Configuration</CardTitle></CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm text-muted-foreground">Payout Threshold ($)</label>
              <Input type="number" {...register("payout_threshold")} />
            </div>
            <div className="space-y-2">
              <label className="text-sm text-muted-foreground">Payout Frequency</label>
              <Select value={watch("payout_frequency")} onValueChange={(v) => setValue("payout_frequency", v as "daily" | "weekly" | "biweekly")}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="daily">Daily</SelectItem>
                  <SelectItem value="weekly">Weekly</SelectItem>
                  <SelectItem value="biweekly">Biweekly</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-base">General</CardTitle></CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm text-muted-foreground">Max Booking Hours</label>
              <Input type="number" {...register("max_booking_hours")} />
            </div>
            <div className="flex items-center gap-3 pt-6">
              <input type="checkbox" id="sos_police" {...register("sos_auto_notify_police")} className="h-4 w-4 rounded border-input" />
              <label htmlFor="sos_police" className="text-sm">Auto-notify police on SOS</label>
            </div>
          </CardContent>
        </Card>

        <Button type="submit" disabled={updateMutation.isPending}>
          {updateMutation.isPending ? "Saving..." : "Save Settings"}
        </Button>
      </form>
    </div>
  );
}
