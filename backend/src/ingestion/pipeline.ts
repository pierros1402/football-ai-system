// src/ingestion/pipeline.ts
import { getProvider } from "./providers/registry.ts";
import {
  normalizeCompetition,
  normalizeSeason,
  normalizeTeam,
  normalizePlayer,
  normalizeMatch,
  normalizeEvent,
  normalizeStats,
} from "./normalizer.ts";
import { getOrCreateMapping } from "./mappingEngine.ts";
import {
  writeCompetition,
  writeSeason,
  writeTeam,
  writePlayer,
  writeMatch,
  writeEvents,
  writeStats,
  writeLineups,
} from "./writer.ts";

export interface IngestionTask {
  provider: string;
  entityType: string;
  entityId: string;
}

export async function runIngestionTask(task: IngestionTask) {
  const provider = getProvider(task.provider);
  if (!provider) throw new Error(`Provider not registered: ${task.provider}`);

  const fetchMethod = getFetchMethod(provider, task.entityType);
  if (!fetchMethod) {
    throw new Error(`Provider does not support entity type: ${task.entityType}`);
  }

  const raw = await fetchMethod(task.entityId);
  const normalized = normalizeEntity(task.entityType, raw);

  const internalId = await getOrCreateMapping(
    task.provider,
    task.entityType,
    task.entityId,
    normalized
  );

  await writeEntity(task.entityType, internalId, normalized);

  return internalId;
}

function getFetchMethod(provider: any, entityType: string): ((id: string) => Promise<any>) | null {
  switch (entityType) {
    case "competition": return provider.fetchCompetition;
    case "season": return provider.fetchSeason;
    case "team": return provider.fetchTeam;
    case "player": return provider.fetchPlayer;
    case "match": return provider.fetchMatch;
    case "events": return provider.fetchEvents;
    case "stats": return provider.fetchStats;
    default: return null;
  }
}

function normalizeEntity(entityType: string, raw: any) {
  switch (entityType) {
    case "competition": return normalizeCompetition(raw);
    case "season": return normalizeSeason(raw);
    case "team": return normalizeTeam(raw);
    case "player": return normalizePlayer(raw);
    case "match": return normalizeMatch(raw);
    case "events": return raw.map((e: any) => normalizeEvent(e));
    case "stats": return normalizeStats(raw);
    default:
      throw new Error(`Unknown entity type: ${entityType}`);
  }
}

async function writeEntity(entityType: string, id: number, data: any) {
  switch (entityType) {
    case "competition": return writeCompetition(id, data);
    case "season": return writeSeason(id, data);
    case "team": return writeTeam(id, data);
    case "player": return writePlayer(id, data);
    case "match": return writeMatch(id, data);
    case "events": return writeEvents(id, data);
    case "stats":
      // stats χρειάζονται context (match/team/player) – αυτό θα το ορίσουμε per‑provider
      return;
    default:
      throw new Error(`Unknown entity type: ${entityType}`);
  }
}
