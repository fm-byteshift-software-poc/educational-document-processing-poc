import { Outlet } from "react-router";
import Navbar from "@/components/Navbar";

export default function MainLayout() {
  return (
    <div className="min-h-screen bg-base-100">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}
