// src/schema/matches.ts
import { pgTable, serial, integer, text, timestamp } from "drizzle-orm/pg-core";
import { seasons } from "./seasons.ts";
import { teams } from "./teams.ts";

export const matches = pgTable("matches", {
  id: serial("id").primaryKey(),

  seasonId: integer("season_id")
    .notNull()
    .references(() => seasons.id),

  homeTeamId: integer("home_team_id")
    .notNull()
    .references(() => teams.id),

  awayTeamId: integer("away_team_id")
    .notNull()
    .references(() => teams.id),

  date: timestamp("date", { mode: "string" }).notNull(),
  // kickoff time (ISO string)

  status: text("status").notNull().default("scheduled"),

  venue: text("venue"),

  createdAt: timestamp("created_at", { mode: "string" }).defaultNow().notNull(),
});
