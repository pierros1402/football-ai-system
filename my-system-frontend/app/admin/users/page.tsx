"use client";

import { useEffect, useState } from "react";
import axios from "@/lib/axios";
import { useRouter } from "next/navigation";

export default function AdminUsersPage() {
  const router = useRouter();

  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [tokenChecked, setTokenChecked] = useState(false);

  // 1) Check token ONLY on client
  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      router.push("/login");
      return;
    }

    setTokenChecked(true);
  }, []);

  // 2) Fetch users ONLY after token is confirmed
  useEffect(() => {
    if (!tokenChecked) return;

    async function fetchUsers() {
      try {
        const res = await axios.get("/api/users/admin/list");

        setUsers(res.data || res.data.items || []);
      } catch (err) {
        console.error("Fetch error:", err);
        router.push("/login");
      } finally {
        setLoading(false);
      }
    }

    fetchUsers();
  }, [tokenChecked]);

  if (!tokenChecked || loading) {
    return <div className="p-6">Loading...</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Admin Users</h1>

      {users.length === 0 && (
        <div className="text-gray-500">No users found.</div>
      )}

      {users.length > 0 && (
        <table className="w-full border">
          <thead>
            <tr className="bg-gray-100">
              <th className="border p-2">ID</th>
              <th className="border p-2">Username</th>
              <th className="border p-2">Email</th>
              <th className="border p-2">Role</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u: any) => (
              <tr key={u.id}>
                <td className="border p-2">{u.id}</td>
                <td className="border p-2">{u.username}</td>
                <td className="border p-2">{u.email}</td>
                <td className="border p-2">{u.role}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
