import { runNextIngestionTask } from "./src/ingestion/runner.ts";

async function main() {
  await runNextIngestionTask();
}

main();
