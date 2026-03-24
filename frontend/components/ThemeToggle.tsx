"use client";

import { useTheme } from "../app/providers/ThemeProvider";

export default function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <div className="flex gap-2 items-center">
      <button
        onClick={() => setTheme("light")}
        className={`px-3 py-1 rounded ${theme === "light" ? "bg-accent text-white" : "bg-gray-300"}`}
      >
        Light
      </button>

      <button
        onClick={() => setTheme("dark")}
        className={`px-3 py-1 rounded ${theme === "dark" ? "bg-accent text-white" : "bg-gray-300"}`}
      >
        Dark
      </button>

      <button
        onClick={() => setTheme("system")}
        className={`px-3 py-1 rounded ${theme === "system" ? "bg-accent text-white" : "bg-gray-300"}`}
      >
        Auto
      </button>
    </div>
  );
}
