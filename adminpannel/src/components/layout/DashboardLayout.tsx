import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { useAdminWebSocket } from "@/hooks/useAdminWebSocket";

export function DashboardLayout() {
  const { isConnected, sosCount } = useAdminWebSocket();

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar sosCount={sosCount} />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Topbar isConnected={isConnected} />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
