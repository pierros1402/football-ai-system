// src/schema/stats.ts
import { pgTable, serial, integer, text, doublePrecision, timestamp } from "drizzle-orm/pg-core";
import { matches } from "./matches.ts";
import { teams } from "./teams.ts";
import { players } from "./players.ts";

export const stats = pgTable("stats", {
  id: serial("id").primaryKey(),

  matchId: integer("match_id")
    .notNull()
    .references(() => matches.id),

  teamId: integer("team_id")
    .notNull()
    .references(() => teams.id),

  playerId: integer("player_id")
    .references(() => players.id),
  // nullable because many stats are team-level

  key: text("key").notNull(),
  // e.g. "shots", "passes", "xg", "xa", "touches", "possession"

  valueInt: integer("value_int"),
  // for integer stats (shots, passes, tackles)

  valueFloat: doublePrecision("value_float"),
  // for float stats (xG, xA, possession)

  valueText: text("value_text"),
  // for string stats (left foot, counter attack)

  createdAt: timestamp("created_at").defaultNow().notNull(),
});
