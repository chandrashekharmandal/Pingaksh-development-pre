import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface DateRangePickerProps {
  from: string;
  to: string;
  onChange: (from: string, to: string) => void;
}

export function DateRangePicker({ from, to, onChange }: DateRangePickerProps) {
  const presets = [
    { label: "Today", days: 0 },
    { label: "7d", days: 7 },
    { label: "30d", days: 30 },
    { label: "90d", days: 90 },
  ];

  const applyPreset = (days: number) => {
    const end = new Date();
    const start = new Date();
    start.setDate(end.getDate() - days);
    onChange(start.toISOString().split("T")[0], end.toISOString().split("T")[0]);
  };

  return (
    <div className="flex items-center gap-2">
      <div className="flex items-center gap-1">
        {presets.map((p) => (
          <Button key={p.label} variant="ghost" size="sm" onClick={() => applyPreset(p.days)}>
            {p.label}
          </Button>
        ))}
      </div>
      <Input type="date" value={from} onChange={(e) => onChange(e.target.value, to)} className="w-36" />
      <span className="text-muted-foreground">to</span>
      <Input type="date" value={to} onChange={(e) => onChange(from, e.target.value)} className="w-36" />
    </div>
  );
}
