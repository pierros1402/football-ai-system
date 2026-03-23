// src/ingestion/providers/types.ts

export interface ProviderFetchOptions {
  id: string;
}

export interface NormalizedCompetition {
  name: string;
  country: string | null;
}

export interface NormalizedSeason {
  name: string;
  yearStart: number;
  yearEnd: number;
  competitionId: number | null;
}

export interface NormalizedTeam {
  name: string;
  shortName: string | null;
  country: string | null;
}

export interface NormalizedPlayer {
  name: string;
  position: string | null;
  nationality: string | null;
}

export interface NormalizedMatch {
  date: Date;
  seasonId: number | null;
  homeTeamId: number | null;
  awayTeamId: number | null;
  status: string | null;
  venue: string | null;
}

export interface NormalizedEvent {
  teamId: number | null;
  playerId: number | null;
  minute: number | null;
  second: number | null;
  type: string | null;
  outcome: string | null;
  x: number | null;
  y: number | null;
}

export interface NormalizedStat {
  key: string;
  valueInt: number | null;
  valueFloat: number | null;
  valueText: string | null;
}
