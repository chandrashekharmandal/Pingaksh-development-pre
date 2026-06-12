import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { useAuthStore } from "@/stores/auth";
import Login from "@/pages/Login";
import Dashboard from "@/pages/Dashboard";
import GuardsList from "@/pages/guards/GuardsList";
import GuardDetail from "@/pages/guards/GuardDetail";
import UsersList from "@/pages/users/UsersList";
import UserDetail from "@/pages/users/UserDetail";
import BookingsList from "@/pages/bookings/BookingsList";
import BookingDetail from "@/pages/bookings/BookingDetail";
import Payments from "@/pages/Payments";
import SOS from "@/pages/SOS";
import Analytics from "@/pages/Analytics";
import Verifications from "@/pages/Verifications";
import Settings from "@/pages/Settings";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } },
});

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.token);
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="guards" element={<GuardsList />} />
            <Route path="guards/:id" element={<GuardDetail />} />
            <Route path="users" element={<UsersList />} />
            <Route path="users/:id" element={<UserDetail />} />
            <Route path="bookings" element={<BookingsList />} />
            <Route path="bookings/:id" element={<BookingDetail />} />
            <Route path="payments" element={<Payments />} />
            <Route path="sos" element={<SOS />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="verifications" element={<Verifications />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
