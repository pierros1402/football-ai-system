"use client";

import { useState } from "react";
import axios from "@/lib/axios";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  async function handleLogin(e: any) {
    e.preventDefault();

    try {
      const res = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`,
        {
          username,
          password,
        }
      );

      localStorage.setItem("access_token", res.data.access_token);

      router.push("/admin/users");
    } catch (err: any) {
      alert("Invalid credentials");
    }
  }

  return (
    <div className="flex items-center justify-center h-screen bg-gray-100">
      <form
        onSubmit={handleLogin}
        className="bg-white p-6 rounded shadow w-80 border"
      >
        <h1 className="text-xl font-bold mb-4 text-black">Admin Login</h1>

        <input
          className="border p-2 w-full mb-3 rounded text-black bg-white"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <input
          className="border p-2 w-full mb-3 rounded text-black bg-white"
          placeholder="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button className="bg-blue-600 text-white w-full py-2 rounded hover:bg-blue-700">
          Login
        </button>
      </form>
    </div>
  );
}
