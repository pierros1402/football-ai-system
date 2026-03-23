// src/ingestion/providers/health.ts
import { getProvider } from "./registry.ts";
import type { BaseProvider } from "./baseProvider.ts";

export function checkProvider(name: string) {
  const p = getProvider(name) as BaseProvider | undefined;
  if (!p) throw new Error(`Provider not registered: ${name}`);

  const requiredMethods = [
    "fetchCompetition",
    "fetchSeason",
    "fetchTeam",
    "fetchPlayer",
    "fetchMatch",
    "fetchEvents",
    "fetchStats",
  ];

  for (const m of requiredMethods) {
    const value = (p as any)[m];

    if (value && typeof value !== "function") {
      throw new Error(`Provider ${name} has invalid method: ${m}`);
    }
  }

  return true;
}
