// src/ingestion/mappingEngine.ts
import { db } from "../db.ts";
import * as schema from "../schema/index.ts";
import { and, eq } from "drizzle-orm";

const {
  providerMappings,
  competitions,
  seasons,
  teams,
  players,
  matches,
} = schema;

export async function getOrCreateMapping(
  provider: string,
  entityType: string,
  providerEntityId: string,
  normalized: any
): Promise<number> {
  const [existing] = await db
    .select()
    .from(providerMappings)
    .where(
      and(
        eq(providerMappings.provider, provider),
        eq(providerMappings.entityType, entityType),
        eq(providerMappings.providerEntityId, providerEntityId)
      )
    );

  if (existing) return existing.entityId;

  const entityId = await createInternalEntity(entityType, normalized);

  await db.insert(providerMappings).values({
    provider,
    entityType,
    entityId,
    providerEntityId,
  });

  return entityId;
}

async function createInternalEntity(
  entityType: string,
  data: any
): Promise<number> {
  switch (entityType) {
    case "competition": {
      const [row] = await db
        .insert(competitions)
        .values({
          name: data.name,
          country: data.country,
        })
        .returning({ id: competitions.id });
      return row.id;
    }

    case "season": {
      const [row] = await db
        .insert(seasons)
        .values({
          name: data.name,
          // TODO: εδώ ιδανικά πρέπει να περάσει πραγματικό competitionId
          competitionId: data.competitionId ?? 0,
          yearStart: data.yearStart,
          yearEnd: data.yearEnd,
        })
        .returning({ id: seasons.id });
      return row.id;
    }

    case "team": {
      const [row] = await db
        .insert(teams)
        .values({
          name: data.name,
          shortName: data.shortName,
          country: data.country,
        })
        .returning({ id: teams.id });
      return row.id;
    }

    case "player": {
      const [row] = await db
        .insert(players)
        .values({
          name: data.name,
          position: data.position,
          nationality: data.nationality,
        })
        .returning({ id: players.id });
      return row.id;
    }

    case "match": {
      const [row] = await db
        .insert(matches)
        .values({
          date: data.date,
          // TODO: εδώ ιδανικά πρέπει να περάσει πραγματικό seasonId
          seasonId: Number(data.seasonId),
          homeTeamId: data.homeTeamId,
          awayTeamId: data.awayTeamId,
          status: data.status,
          venue: data.venue,
        })
        .returning({ id: matches.id });
      return row.id;
    }

    default:
      throw new Error(`Unknown entity type: ${entityType}`);
  }
}
