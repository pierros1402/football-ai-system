// src/schema/ingestion_jobs.ts
import { pgTable, serial, text, timestamp, index } from "drizzle-orm/pg-core";

export const ingestionJobs = pgTable(
  "ingestion_jobs",
  {
    id: serial("id").primaryKey(),

    provider: text("provider").notNull(),
    // e.g. "sofascore", "opta", "statsbomb"

    entityType: text("entity_type").notNull(),
    // competition, season, team, player, match, events, stats

    entityId: text("entity_id"),
    // provider-specific ID (string because some providers use UUIDs)

    status: text("status").notNull(),
    // pending, running, success, failed

    message: text("message"),
    // error message or info

    createdAt: timestamp("created_at").defaultNow().notNull(),
    updatedAt: timestamp("updated_at").defaultNow().notNull(),
  },
  (table) => ({
    // 🔥 Useful for filtering job history
    providerLookupIdx: index("jobs_provider_lookup_idx").on(
      table.provider,
      table.entityType,
      table.entityId
    ),

    // 🔥 Useful for dashboards & monitoring
    statusIdx: index("jobs_status_idx").on(table.status),
  })
);
