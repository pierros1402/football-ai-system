// src/schema/lineups.ts
import { pgTable, serial, integer, text, boolean, timestamp } from "drizzle-orm/pg-core";
import { matches } from "./matches.ts";
import { teams } from "./teams.ts";
import { players } from "./players.ts";

export const lineups = pgTable("lineups", {
  id: serial("id").primaryKey(),

  matchId: integer("match_id")
    .notNull()
    .references(() => matches.id),

  teamId: integer("team_id")
    .notNull()
    .references(() => teams.id),

  playerId: integer("player_id")
    .notNull()
    .references(() => players.id),

  isStarter: boolean("is_starter").notNull(),
  // true = starting XI, false = substitute

  position: text("position"),
  // e.g. GK, LB, CB, RB, DM, CM, AM, LW, RW, ST
  // Providers use different formats → normalized here

  shirtNumber: integer("shirt_number"),
  // jersey number if available

  createdAt: timestamp("created_at").defaultNow().notNull(),
});
