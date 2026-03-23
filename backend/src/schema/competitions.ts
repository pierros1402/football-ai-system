// src/schema/competitions.ts
import { pgTable, serial, text, timestamp } from "drizzle-orm/pg-core";

export const competitions = pgTable("competitions", {
  id: serial("id").primaryKey(),

  name: text("name").notNull(),
  // e.g. "Premier League", "La Liga"

  country: text("country"),
  // e.g. "England", "Spain"

  type: text("type").default("league"),
  // league, cup, international

  createdAt: timestamp("created_at").defaultNow().notNull(),
});
