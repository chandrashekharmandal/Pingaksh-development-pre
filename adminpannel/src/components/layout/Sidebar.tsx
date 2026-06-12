import { useState } from "react";
import { NavLink } from "react-router-dom";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Shield,
  Users,
  CalendarCheck,
  CreditCard,
  AlertTriangle,
  BarChart3,
  FileCheck,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/guards", icon: Shield, label: "Guards" },
  { to: "/users", icon: Users, label: "Users" },
  { to: "/bookings", icon: CalendarCheck, label: "Bookings" },
  { to: "/payments", icon: CreditCard, label: "Payments" },
  { to: "/sos", icon: AlertTriangle, label: "SOS", badge: true },
  { to: "/analytics", icon: BarChart3, label: "Analytics" },
  { to: "/verifications", icon: FileCheck, label: "Verifications" },
  { to: "/settings", icon: Settings, label: "Settings" },
];

interface SidebarProps {
  sosCount: number;
}

export function Sidebar({ sosCount }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside className={cn("relative flex h-screen flex-col border-r bg-card transition-all duration-300", collapsed ? "w-16" : "w-60")}>
      <div className="flex h-14 items-center justify-between px-4">
        {!collapsed && <span className="text-lg font-bold text-primary">BSecure</span>}
        <button onClick={() => setCollapsed(!collapsed)} className="rounded-md p-1 hover:bg-secondary">
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>
      <nav className="flex-1 space-y-1 px-2 py-4">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
                isActive ? "bg-primary/10 text-primary" : "text-muted-foreground hover:bg-secondary hover:text-foreground",
                collapsed && "justify-center px-2"
              )
            }
          >
            <item.icon className="h-5 w-5 shrink-0" />
            {!collapsed && <span>{item.label}</span>}
            {!collapsed && item.badge && sosCount > 0 && (
              <span className="ml-auto flex h-5 w-5 items-center justify-center rounded-full bg-destructive text-[10px] font-bold text-white">
                {sosCount}
              </span>
            )}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
