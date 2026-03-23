// src/dbInspect.ts
import { db } from "./db.ts";
import * as schema from "./schema/index.ts";

const { ingestionQueue } = schema;

async function main() {
  const rows = await db.select().from(ingestionQueue);
  console.log(rows);
}

main();
