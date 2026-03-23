// src/schema/teams.ts
import { pgTable, serial, text, integer, timestamp } from "drizzle-orm/pg-core";
import { competitions } from "./competitions.ts";

export const teams = pgTable("teams", {
  id: serial("id").primaryKey(),

  name: text("name").notNull(),
  // e.g. "Manchester City"

  shortName: text("short_name"),
  // e.g. "MCI"

  country: text("country"),
  // e.g. "England"

  competitionId: integer("competition_id")
    .references(() => competitions.id),
  // nullable because:
  // - some providers don't give competition per team
  // - teams may appear in multiple competitions (CL, EL, domestic league)

  createdAt: timestamp("created_at").defaultNow().notNull(),
});
