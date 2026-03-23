// backend/ingestion/mappers/mapFixtures.ts

import { mapTeamName } from "./team_mapper";
import { mapLeagueName } from "./league_mapper";
import { mapSeasonName } from "./season_mapper";

/**
 * Mapping engine για fixtures.
 * Μετατρέπει raw names σε unified IDs.
 */
export async function mapFixtures(fixtures: any[]) {
  const mapped: any[] = [];

  for (const f of fixtures) {
    const homeTeamId = await mapTeamName(f.home_team);
    const awayTeamId = await mapTeamName(f.away_team);

    const leagueId = await mapLeagueName(f.league ?? "Unknown League");
    const seasonId = await mapSeasonName(f.season ?? "Unknown Season");

    mapped.push({
      ...f,
      home_team_id: homeTeamId,
      away_team_id: awayTeamId,
      league_id: leagueId,
      season_id: seasonId
    });
  }

  return mapped;
}
