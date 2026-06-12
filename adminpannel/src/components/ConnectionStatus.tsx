import { cn } from "@/lib/utils";

export function ConnectionStatus({ isConnected }: { isConnected: boolean }) {
  return (
    <div className="flex items-center gap-2">
      <div className={cn("h-2 w-2 rounded-full", isConnected ? "bg-accent animate-pulse" : "bg-destructive")} />
      <span className="text-xs text-muted-foreground">{isConnected ? "Live" : "Disconnected"}</span>
    </div>
  );
}
