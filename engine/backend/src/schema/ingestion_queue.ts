// src/schema/ingestion_queue.ts
import { pgTable, serial, text, integer, timestamp, index } from "drizzle-orm/pg-core";

export const ingestionQueue = pgTable(
  "ingestion_queue",
  {
    id: serial("id").primaryKey(),

    provider: text("provider").notNull(),
    // e.g. "sofascore", "opta", "statsbomb"

    entityType: text("entity_type").notNull(),
    // competition, season, team, player, match, events, stats

    entityId: text("entity_id"),
    // provider-specific ID (string because some providers use UUIDs)

    priority: integer("priority").notNull().default(1),
    // 1 = normal, 5 = urgent

    status: text("status").notNull().default("pending"),
    // pending, running, done, failed

    attempts: integer("attempts").notNull().default(0),
    // number of retries

    createdAt: timestamp("created_at").defaultNow().notNull(),
    updatedAt: timestamp("updated_at").defaultNow().notNull(),
  },
  (table) => ({
    // 🔥 Critical index for workers to fetch tasks fast
    statusPriorityIdx: index("queue_status_priority_idx").on(
      table.status,
      table.priority
    ),

    // 🔥 Useful for debugging and reprocessing
    providerLookupIdx: index("queue_provider_lookup_idx").on(
      table.provider,
      table.entityType,
      table.entityId
    ),
  })
);
