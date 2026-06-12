import { useLocation, useNavigate } from "react-router-dom";
import { Bell, LogOut, User } from "lucide-react";
import { ConnectionStatus } from "@/components/ConnectionStatus";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuthStore } from "@/stores/auth";

interface TopbarProps {
  isConnected: boolean;
}

export function Topbar({ isConnected }: TopbarProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const breadcrumb = location.pathname === "/" ? "Dashboard" : location.pathname.slice(1).split("/").map((s) => s.charAt(0).toUpperCase() + s.slice(1)).join(" / ");

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <header className="flex h-14 items-center justify-between border-b bg-card px-6">
      <div className="flex items-center gap-4">
        <h2 className="text-sm font-medium text-muted-foreground">{breadcrumb}</h2>
      </div>
      <div className="flex items-center gap-4">
        <ConnectionStatus isConnected={isConnected} />
        <button className="relative rounded-md p-2 hover:bg-secondary">
          <Bell className="h-4 w-4 text-muted-foreground" />
        </button>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="flex items-center gap-2 rounded-md p-1 hover:bg-secondary">
              <Avatar className="h-8 w-8">
                <AvatarFallback className="text-xs">{user?.name?.charAt(0) || "A"}</AvatarFallback>
              </Avatar>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuLabel>{user?.name || "Admin"}</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <User className="mr-2 h-4 w-4" /> Profile
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleLogout} className="text-destructive">
              <LogOut className="mr-2 h-4 w-4" /> Logout
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
