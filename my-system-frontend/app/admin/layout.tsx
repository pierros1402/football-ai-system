"use client";

import LogoutButton from "@/components/LogoutButton";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="flex justify-between items-center p-4 bg-white border-b">
        <h1 className="text-xl font-bold">Admin Panel</h1>
        <LogoutButton />
      </header>

      <main className="p-6">
        {children}
      </main>
    </div>
  );
}
