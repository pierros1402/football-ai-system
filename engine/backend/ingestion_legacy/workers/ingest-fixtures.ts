// backend/ingestion/workers/ingest-fixtures.ts

import { SOURCES } from "../config";
import { getInternalFixtures } from "../sources/internal_fixtures";
import { mapFixtures } from "../mappers/mapFixtures";
import { validateFixtures } from "../validators/validateFixtures";   // <-- ΕΔΩ
import { saveFixtures } from "../savers/saveFixtures";

export async function ingestFixtures() {
  console.log("Starting fixtures ingestion...");

  for (const source of SOURCES) {
    if (!source.enabled) continue;

    console.log(`Fetching from source: ${source.name}`);

    const raw = await fetchFromSource(source.name);
    const normalized = normalizeFixtures(raw);

    const mapped = await mapFixtures(normalized);

    const valid = validateFixtures(mapped);   // <-- ΕΔΩ

    await saveFixtures(valid);
  }

  console.log("Fixtures ingestion completed.");
}

// --------------------------------------------------
// FETCH FROM SOURCE
// --------------------------------------------------
async function fetchFromSource(sourceName: string) {
  if (sourceName === "internal") {
    return await getInternalFixtures();
  }

  // Μελλοντικές πηγές
  return [];
}

// --------------------------------------------------
// NORMALIZATION (worker-level)
// --------------------------------------------------
function normalizeFixtures(raw: any[]) {
  // Το internal source ήδη επιστρέφει normalized data
  return raw;
}

// --------------------------------------------------
// VALIDATION
// --------------------------------------------------
function validateFixtures(fixtures: any[]) {
  return fixtures.filter(f => {
    if (!f.home_team_id) return false;
    if (!f.away_team_id) return false;
    if (!f.league_id) return false;
    if (!f.season_id) return false;
    if (!f.date) return false;
    return true;
  });
}

// --------------------------------------------------
// SAVE TO DB
// --------------------------------------------------
async function saveFixtures(fixtures: any[]) {
  // TODO: insert into PostgreSQL
  console.log(`Saving ${fixtures.length} fixtures to DB...`);
}
