import type { TimelineEvent } from "@/types";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

const eventColors: Record<string, string> = {
  created: "bg-muted-foreground",
  accepted: "bg-primary",
  started: "bg-accent",
  completed: "bg-accent",
  cancelled: "bg-destructive",
  refunded: "bg-yellow-400",
};

export function BookingTimeline({ events }: { events: TimelineEvent[] }) {
  return (
    <div className="space-y-0">
      {events.map((event, i) => (
        <div key={event.id} className="flex gap-3">
          <div className="flex flex-col items-center">
            <div className={cn("h-3 w-3 rounded-full", eventColors[event.event] || "bg-muted-foreground")} />
            {i < events.length - 1 && <div className="w-px flex-1 bg-border" />}
          </div>
          <div className="pb-4">
            <p className="text-sm font-medium capitalize">{event.event.replace(/_/g, " ")}</p>
            <p className="text-xs text-muted-foreground">
              {format(new Date(event.timestamp), "MMM d, yyyy HH:mm")}
              {event.actor && ` - ${event.actor}`}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
