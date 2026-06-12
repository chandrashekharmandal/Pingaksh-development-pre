import { useState, useEffect } from "react";
import { AlertTriangle, Phone } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { SOSEvent } from "@/types";
import { formatDistanceToNow } from "date-fns";

interface SOSEventCardProps {
  event: SOSEvent;
  onResolve: (id: string, notes: string) => void;
}

export function SOSEventCard({ event, onResolve }: SOSEventCardProps) {
  const [elapsed, setElapsed] = useState("");
  const [notes, setNotes] = useState("");

  useEffect(() => {
    const update = () => setElapsed(formatDistanceToNow(new Date(event.triggered_at), { addSuffix: false }));
    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, [event.triggered_at]);

  return (
    <div className="relative overflow-hidden rounded-lg border-2 border-destructive/50 bg-destructive/5 p-4">
      <div className="absolute right-0 top-0 h-2 w-full animate-pulse bg-destructive/30" />
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="rounded-full bg-destructive/20 p-2">
            <AlertTriangle className="h-5 w-5 text-destructive" />
          </div>
          <div>
            <p className="font-semibold">{event.user.name}</p>
            <p className="text-sm text-muted-foreground">{event.location.address}</p>
          </div>
        </div>
        <div className="text-right">
          <p className="font-mono text-lg font-bold text-destructive">{elapsed}</p>
          <p className="text-xs text-muted-foreground">elapsed</p>
        </div>
      </div>
      <div className="mt-3 flex items-center gap-2">
        <a href={`tel:${event.user.phone}`} className="inline-flex items-center gap-1 text-sm text-accent hover:underline">
          <Phone className="h-3 w-3" /> {event.user.phone}
        </a>
        {event.guard && (
          <span className="text-sm text-muted-foreground">| Guard: {event.guard.name}</span>
        )}
      </div>
      <div className="mt-3 flex gap-2">
        <input
          className="flex-1 rounded-md border border-input bg-transparent px-3 py-1 text-sm placeholder:text-muted-foreground"
          placeholder="Resolution notes..."
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
        <Button size="sm" variant="destructive" onClick={() => onResolve(event.id, notes)}>
          Resolve
        </Button>
      </div>
    </div>
  );
}
