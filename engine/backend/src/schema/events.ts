// src/schema/events.ts
import { pgTable, serial, integer, text, timestamp } from "drizzle-orm/pg-core";
import { matches } from "./matches.ts";
import { teams } from "./teams.ts";
import { players } from "./players.ts";

export const events = pgTable("events", {
  id: serial("id").primaryKey(),

  matchId: integer("match_id")
    .notNull()
    .references(() => matches.id),

  teamId: integer("team_id")
    .references(() => teams.id),

  playerId: integer("player_id")
    .references(() => players.id),

  minute: integer("minute").notNull(),
  second: integer("second"),

  type: text("type").notNull(),
  // goal, shot, pass, foul, card, offside, save, clearance, substitution, etc.

  outcome: text("outcome"),
  // success, fail, blocked, saved, yellow, red, etc.

  x: integer("x"),
  y: integer("y"),
  // pitch coordinates 0–100 (integer for consistency across providers)

  createdAt: timestamp("created_at").defaultNow().notNull(),
});
