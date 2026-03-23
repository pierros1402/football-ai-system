// src/schema/players.ts
import { pgTable, serial, text, integer, timestamp } from "drizzle-orm/pg-core";
import { teams } from "./teams.ts";

export const players = pgTable("players", {
  id: serial("id").primaryKey(),

  name: text("name").notNull(),
  // e.g. "Kevin De Bruyne"

  position: text("position"),
  // e.g. "MF", "FW", "GK"
  // Providers use: role, position, detailedPosition → normalized to this

  nationality: text("nationality"),
  // e.g. "Belgium"

  teamId: integer("team_id")
    .references(() => teams.id),
  // nullable because:
  // - some providers don't attach players to teams
  // - players may be free agents
  // - national team players don't belong to clubs

  createdAt: timestamp("created_at").defaultNow().notNull(),
});
