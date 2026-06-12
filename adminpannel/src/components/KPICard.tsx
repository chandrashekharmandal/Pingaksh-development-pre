import { LucideIcon, TrendingUp, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface KPICardProps {
  icon: LucideIcon;
  value: string | number;
  label: string;
  trend?: number;
  className?: string;
}

export function KPICard({ icon: Icon, value, label, trend, className }: KPICardProps) {
  return (
    <div className={cn("relative overflow-hidden rounded-lg border bg-card p-6 transition-all hover:border-primary/50", className)}>
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent" />
      <div className="relative flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">{label}</p>
          <p className="mt-1 text-3xl font-bold tracking-tight">{value}</p>
          {trend !== undefined && (
            <div className={cn("mt-2 flex items-center gap-1 text-xs", trend >= 0 ? "text-accent" : "text-destructive")}>
              {trend >= 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
              <span>{Math.abs(trend)}% from last week</span>
            </div>
          )}
        </div>
        <div className="rounded-lg bg-primary/10 p-3">
          <Icon className="h-6 w-6 text-primary" />
        </div>
      </div>
    </div>
  );
}
