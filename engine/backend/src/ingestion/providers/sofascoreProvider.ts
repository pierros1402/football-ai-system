// src/ingestion/providers/sofascoreProvider.ts
import { BaseProvider } from "./baseProvider.ts";
import { sofascoreApi } from "./sofascore.ts";

export const sofascoreProvider: BaseProvider = {
  // --- COMPETITION ---
  async fetchCompetition(id: string) {
    const raw = await sofascoreApi.getCompetition(id);

    return {
      id: String(raw.id),
      name: raw.name,
      country: raw.country?.name ?? undefined,
    };
  },

  // --- SEASON ---
  async fetchSeason(id: string) {
    const raw = await sofascoreApi.getSeason(id);

    return {
      id: String(raw.id),
      name: raw.name ?? `${raw.year}/${String(raw.year + 1).slice(-2)}`,
      yearStart: raw.year,
      yearEnd: raw.year + 1,
    };
  },

  // --- TEAM ---
  async fetchTeam(id: string) {
    const raw = await sofascoreApi.getTeam(id);

    return {
      id: String(raw.id),
      name: raw.name,
      shortName: raw.shortName ?? undefined,
      country: raw.country?.name ?? undefined,
    };
  },

  // --- PLAYER ---
  async fetchPlayer(id: string) {
    const raw = await sofascoreApi.getPlayer(id);

    return {
      id: String(raw.id),
      name: raw.name,
      position: raw.position ?? undefined,
      nationality: raw.country?.name ?? undefined,
    };
  },

  // --- MATCH ---
  async fetchMatch(id: string) {
    const raw = await sofascoreApi.getMatch(id);

    return {
      id: String(raw.id),
      date: new Date(raw.startTimestamp * 1000).toISOString(),
      homeTeamId: String(raw.homeTeam?.id),
      awayTeamId: String(raw.awayTeam?.id),
      status: raw.status?.type ?? "unknown",
      venue: raw.venue?.stadium?.name ?? undefined,
    };
  },

  // --- EVENTS ---
  async fetchEvents(id: string) {
    const raw = await sofascoreApi.getEvents(id);

    return raw.map((ev: any) => ({
      teamId: ev.team?.id ? String(ev.team.id) : undefined,
      playerId: ev.player?.id ? String(ev.player.id) : undefined,
      minute: ev.time ?? 0,
      second: ev.timeSeconds ?? undefined,
      type: ev.incidentType ?? "unknown",
      outcome: ev.outcome ?? undefined,
      x: ev.x ?? undefined,
      y: ev.y ?? undefined,
    }));
  },

  // --- STATS ---
  async fetchStats(id: string) {
    const raw = await sofascoreApi.getStats(id);

    const list: any[] = [];

    for (const group of raw.groups ?? []) {
      for (const item of group.statisticsItems ?? []) {
        list.push({
          key: item.name,
          valueInt: typeof item.value === "number" && Number.isInteger(item.value)
            ? item.value
            : undefined,
          valueFloat: typeof item.value === "number" && !Number.isInteger(item.value)
            ? item.value
            : undefined,
          valueText: typeof item.displayValue === "string"
            ? item.displayValue
            : undefined,
        });
      }
    }

    return list;
  },
};
