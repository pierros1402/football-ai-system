// src/ingestion/writer.ts
import { db } from "../db.ts";
import * as schema from "../schema/index.ts";
import { NormalizedStat } from "./normalizer.ts";
import { eq } from "drizzle-orm";

const {
  competitions,
  seasons,
  teams,
  players,
  matches,
  events,
  stats,
  lineups,
} = schema;

export async function writeCompetition(id: number, data: any) {
  await db
    .update(competitions)
    .set({
      name: data.name,
      country: data.country,
    })
    .where(eq(competitions.id, id));
}

export async function writeSeason(id: number, data: any) {
  await db
    .update(seasons)
    .set({
      name: data.name,
      yearStart: data.yearStart,
      yearEnd: data.yearEnd,
    })
    .where(eq(seasons.id, id));
}

export async function writeTeam(id: number, data: any) {
  await db
    .update(teams)
    .set({
      name: data.name,
      shortName: data.shortName,
      country: data.country,
    })
    .where(eq(teams.id, id));
}

export async function writePlayer(id: number, data: any) {
  await db
    .update(players)
    .set({
      name: data.name,
      position: data.position,
      nationality: data.nationality,
    })
    .where(eq(players.id, id));
}

export async function writeMatch(id: number, data: any) {
  await db
    .update(matches)
    .set({
      date: data.date,
      homeTeamId: data.homeTeamId,
      awayTeamId: data.awayTeamId,
      status: data.status,
      venue: data.venue,
    })
    .where(eq(matches.id, id));
}

export async function writeEvents(matchId: number, eventList: any[]) {
  for (const ev of eventList) {
    await db.insert(events).values({
      matchId,
      teamId: ev.teamId ? Number(ev.teamId) : null,
      playerId: ev.playerId ? Number(ev.playerId) : null,
      minute: ev.minute,
      second: ev.second,
      type: ev.type,
      outcome: ev.outcome,
      x: ev.x,
      y: ev.y,
    });
  }
}

export async function writeStats(
  matchId: number,
  teamId: number,
  playerId: number | null,
  statsList: NormalizedStat[]
) {
  for (const st of statsList) {
    await db.insert(stats).values({
      matchId,
      teamId,
      playerId,
      key: st.key,
      valueInt: st.valueInt ?? null,
      valueFloat: st.valueFloat ?? null,
      valueText: st.valueText ?? null,
    });
  }
}

export async function writeLineups(
  matchId: number,
  teamId: number,
  lineupList: any[]
) {
  for (const p of lineupList) {
    await db.insert(lineups).values({
      matchId,
      teamId,
      playerId: Number(p.playerId),
      isStarter: p.isStarter,
      position: p.position,
      shirtNumber: p.shirtNumber,
    });
  }
}
