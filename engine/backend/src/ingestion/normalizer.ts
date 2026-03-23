// src/ingestion/normalizer.ts

//
// Normalized Interfaces
//

export interface NormalizedCompetition {
  id: string;
  name: string;
  country?: string;
}

export interface NormalizedSeason {
  id: string;
  name: string;      // "2023/24"
  yearStart: number; // 2023
  yearEnd: number;   // 2024
}

export interface NormalizedTeam {
  id: string;
  name: string;
  shortName?: string;
  country?: string;
}

export interface NormalizedPlayer {
  id: string;
  name: string;
  position?: string;
  nationality?: string;
}

export interface NormalizedMatch {
  id: string;
  date: string;
  homeTeamId: string;
  awayTeamId: string;
  status: string;
  venue?: string;
  seasonId: string;   // <-- προσθήκη
}

export interface NormalizedEvent {
  teamId?: string;
  playerId?: string;
  minute: number;
  second?: number;
  type: string;
  outcome?: string;
  x?: number;
  y?: number;
}

export interface NormalizedStat {
  key: string;
  valueInt?: number;
  valueFloat?: number;
  valueText?: string;
}

//
// Utility helpers
//

function pickId(raw: any, ...keys: string[]): string {
  for (const k of keys) {
    if (raw[k] !== undefined && raw[k] !== null) return String(raw[k]);
  }
  throw new Error("Missing ID in raw object");
}

function pick(raw: any, ...keys: string[]): any {
  for (const k of keys) {
    if (raw[k] !== undefined && raw[k] !== null) return raw[k];
  }
  return undefined;
}

//
// Normalizers
//

export function normalizeCompetition(raw: any): NormalizedCompetition {
  return {
    id: pickId(raw, "id", "competitionId", "uid"),
    name: pick(raw, "name", "competitionName"),
    country: pick(raw, "country", "region"),
  };
}

export function normalizeSeason(raw: any): NormalizedSeason {
  const id = pickId(raw, "id", "seasonId", "uid");
  const yearLabel =
    pick(raw, "year", "name", "season") ??
    (raw.startYear && raw.endYear
      ? `${raw.startYear}/${String(raw.endYear).slice(-2)}`
      : "unknown");

  let yearStart: number;
  let yearEnd: number;

  if (yearLabel.includes("/")) {
    const [a, b] = yearLabel.split("/");
    yearStart = Number(a);
    yearEnd = Number(b.length === 2 ? `20${b}` : b);
  } else if (yearLabel.includes("-")) {
    const [a, b] = yearLabel.split("-");
    yearStart = Number(a);
    yearEnd = Number(b);
  } else {
    yearStart = Number(yearLabel) || 0;
    yearEnd = yearStart + 1;
  }

  return {
    id,
    name: yearLabel,
    yearStart,
    yearEnd,
  };
}

export function normalizeTeam(raw: any): NormalizedTeam {
  return {
    id: pickId(raw, "id", "teamId"),
    name: pick(raw, "name", "teamName"),
    shortName: pick(raw, "shortName", "abbreviation"),
    country: pick(raw, "country"),
  };
}

export function normalizePlayer(raw: any): NormalizedPlayer {
  return {
    id: pickId(raw, "id", "playerId"),
    name: pick(raw, "name", "fullName"),
    position: pick(raw, "position", "role"),
    nationality: pick(raw, "nationality"),
  };
}

export function normalizeMatch(raw: any): NormalizedMatch {
  const seasonId =
    raw.tournament?.season?.id ??
    raw.tournament?.uniqueTournament?.season?.id ??
    raw.season?.id;

  return {
    id: pickId(raw, "id", "matchId"),
    date: pick(raw, "date", "kickoffTime"),
    homeTeamId:
      pickId(raw, "homeTeamId") ??
      pickId(raw.home ?? {}, "id", "teamId"),
    awayTeamId:
      pickId(raw, "awayTeamId") ??
      pickId(raw.away ?? {}, "id", "teamId"),
    status: pick(raw, "status"),
    venue: pick(raw, "venue", "stadium"),

    // 🔥 ΠΑΝΤΑ string, ΠΑΝΤΑ υπαρκτό
    seasonId: String(seasonId),
  };
}


export function normalizeEvent(raw: any): NormalizedEvent {
  return {
    teamId: pick(raw, "teamId") ?? raw.team?.id,
    playerId: pick(raw, "playerId") ?? raw.player?.id,
    minute: pick(raw, "minute") ?? 0,
    second: pick(raw, "second"),
    type: pick(raw, "type", "eventType"),
    outcome: pick(raw, "outcome", "result"),
    x: raw.x !== undefined ? Math.round(raw.x * 100) : undefined,
    y: raw.y !== undefined ? Math.round(raw.y * 100) : undefined,
  };
}

export function normalizeStats(raw: any[]): NormalizedStat[] {
  return raw.map((st) => {
    const key = st.key ?? st.name;
    const value = st.value;

    const normalized: NormalizedStat = { key };

    if (typeof value === "number") {
      if (Number.isInteger(value)) normalized.valueInt = value;
      else normalized.valueFloat = value;
    } else if (typeof value === "string") {
      normalized.valueText = value;
    }

    return normalized;
  });
}
