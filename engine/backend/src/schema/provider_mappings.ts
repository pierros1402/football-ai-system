// src/schema/provider_mappings.ts
import { pgTable, serial, text, integer, timestamp, index } from "drizzle-orm/pg-core";

export const providerMappings = pgTable(
  "provider_mappings",
  {
    id: serial("id").primaryKey(),

    provider: text("provider").notNull(),
    // e.g. "sofascore", "opta", "statsbomb", "wyscout"

    entityType: text("entity_type").notNull(),
    // competition, season, team, player, match, event, stat

    entityId: integer("entity_id").notNull(),
    // internal unified ID (e.g. teams.id)

    providerEntityId: text("provider_entity_id").notNull(),
    // provider-specific ID (string because some providers use UUIDs)

    createdAt: timestamp("created_at").defaultNow().notNull(),
  },
  (table) => ({
    // 🔥 Critical index for fast lookups
    providerLookup: index("provider_lookup_idx").on(
      table.provider,
      table.entityType,
      table.providerEntityId
    ),

    // 🔥 Useful for reverse lookups (internal → provider)
    entityLookup: index("entity_lookup_idx").on(
      table.entityType,
      table.entityId
    ),
  })
);
