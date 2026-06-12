import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const statusConfig: Record<string, { label: string; className: string }> = {
  active: { label: "Active", className: "bg-accent/20 text-accent border-accent/30" },
  online: { label: "Online", className: "bg-accent/20 text-accent border-accent/30" },
  completed: { label: "Completed", className: "bg-accent/20 text-accent border-accent/30" },
  approved: { label: "Approved", className: "bg-accent/20 text-accent border-accent/30" },
  pending: { label: "Pending", className: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30" },
  processing: { label: "Processing", className: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30" },
  in_progress: { label: "In Progress", className: "bg-primary/20 text-primary border-primary/30" },
  accepted: { label: "Accepted", className: "bg-primary/20 text-primary border-primary/30" },
  suspended: { label: "Suspended", className: "bg-destructive/20 text-destructive border-destructive/30" },
  cancelled: { label: "Cancelled", className: "bg-destructive/20 text-destructive border-destructive/30" },
  failed: { label: "Failed", className: "bg-destructive/20 text-destructive border-destructive/30" },
  rejected: { label: "Rejected", className: "bg-destructive/20 text-destructive border-destructive/30" },
  disputed: { label: "Disputed", className: "bg-orange-500/20 text-orange-400 border-orange-500/30" },
  offline: { label: "Offline", className: "bg-muted text-muted-foreground border-border" },
  resolved: { label: "Resolved", className: "bg-accent/20 text-accent border-accent/30" },
  false_alarm: { label: "False Alarm", className: "bg-muted text-muted-foreground border-border" },
};

export function StatusBadge({ status }: { status: string }) {
  const config = statusConfig[status] || { label: status, className: "" };
  return <Badge variant="outline" className={cn("font-medium", config.className)}>{config.label}</Badge>;
}
