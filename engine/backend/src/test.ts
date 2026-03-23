import { db } from "./db.js";
import { teams } from "./schema/index.ts";


async function main() {
  await db.insert(teams).values({ name: "Olympiacos" });
  const result = await db.select().from(teams);
  console.log(result);
}

main();
