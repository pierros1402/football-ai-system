// src/ingestion/queueRunner.ts
import { db } from "../db.ts";
import * as schema from "../schema/index.ts";
import { runIngestionTask } from "./pipeline.ts";
import { eq, asc, desc } from "drizzle-orm";

const { ingestionQueue, ingestionJobs } = schema;

export async function runNextIngestionTask() {
  const [task] = await db
    .select()
    .from(ingestionQueue)
    .where(eq(ingestionQueue.status, "pending"))
    .orderBy(desc(ingestionQueue.priority), asc(ingestionQueue.id))
    .limit(1);

  if (!task) {
    console.log("No pending ingestion tasks.");
    return null;
  }

  console.log("Running ingestion task:", task);

  const now = new Date();

  const [job] = await db
    .insert(ingestionJobs)
    .values({
      provider: task.provider,
      entityType: task.entityType,
      entityId: task.entityId as string,
      status: "running",
      message: null,
      createdAt: now,
      updatedAt: now,
    })
    .returning();

  try {
    const internalId = await runIngestionTask({
      provider: task.provider,
      entityType: task.entityType,
      entityId: task.entityId as string,
    });

    await db
      .update(ingestionJobs)
      .set({
        status: "success",
        message: `internalId=${internalId}`,
        updatedAt: new Date(),
      })
      .where(eq(ingestionJobs.id, job.id));

    await db
      .update(ingestionQueue)
      .set({
        status: "done",
        updatedAt: new Date(),
      })
      .where(eq(ingestionQueue.id, task.id));

    console.log("Ingestion completed:", internalId);
    return internalId;
  } catch (err: any) {
    console.error("Ingestion failed:", err);

    await db
      .update(ingestionJobs)
      .set({
        status: "failed",
        message: err.message ?? String(err),
        updatedAt: new Date(),
      })
      .where(eq(ingestionJobs.id, job.id));

    await db
      .update(ingestionQueue)
      .set({
        status: "failed",
        attempts: task.attempts + 1,
        updatedAt: new Date(),
      })
      .where(eq(ingestionQueue.id, task.id));

    throw err;
  }
}

// Run automatically when executed directly
if (import.meta.main) {
  runNextIngestionTask();
}
