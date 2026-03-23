import { db } from "./src/db.ts";
import * as schema from "./src/schema/index.ts";

const { ingestionQueue } = schema;

await db.insert(ingestionQueue).values([
  {
    provider: "sofascore",
    entityType: "competition",
    entityId: "17",
    status: "pending"
  }
]);

console.log("Task inserted.");
