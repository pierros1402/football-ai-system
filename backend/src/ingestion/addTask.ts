// src/ingestion/addTask.ts
import { db } from "../db.ts";
import * as schema from "../schema/index.ts";

const { ingestionQueue } = schema;

async function addTask(provider: string, entityType: string, entityId: string) {
  await db.insert(ingestionQueue).values({
    provider,
    entityType,
    entityId,
    status: "pending",
    priority: 1,
    attempts: 0,
  });

  console.log("Task added:", { provider, entityType, entityId });
}

const [,, provider, entityType, entityId] = process.argv;

if (!provider || !entityType || !entityId) {
  console.log("Usage: tsx src/ingestion/addTask.ts <provider> <entityType> <entityId>");
  process.exit(1);
}

addTask(provider, entityType, entityId);
