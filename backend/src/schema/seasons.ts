// src/schema/seasons.ts
import { pgTable, serial, integer, text, timestamp } from "drizzle-orm/pg-core";
import { competitions } from "./competitions.ts";

export const seasons = pgTable("seasons", {
  id: serial("id").primaryKey(),

  competitionId: integer("competition_id")
    .notNull()
    .references(() => competitions.id),

  // Unified season label (e.g. "2023/24")
  name: text("name").notNull(),

  // Numeric boundaries for filtering, sorting, analytics
  yearStart: integer("year_start").notNull(),
  yearEnd: integer("year_end").notNull(),

  createdAt: timestamp("created_at").defaultNow().notNull(),
});
