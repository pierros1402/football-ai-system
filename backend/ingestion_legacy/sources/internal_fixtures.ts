// backend/ingestion/sources/internal_fixtures.ts

import { fetchHTML } from "./scraper";
import { extractFixturesFromHTML } from "./ai_extractor";

/**
 * Internal autonomous source for fixtures
 * Συνδυάζει scraper + AI extraction + normalization.
 */
export async function getInternalFixtures() {
  // 1. Scrape HTML από την πηγή που θέλουμε
  const html = await scrapeFixturesHTML();

  // 2. AI extraction -> raw structured data
  const extracted = await extractFixturesFromHTML(html);

  // 3. (Optional) Save raw feed locally
  await saveRawFeed("fixtures", extracted);

  // 4. Normalize σε unified format
  const normalized = normalizeInternalFixtures(extracted);

  return normalized;
}

// --------------------------------------------------
// SCRAPER
// --------------------------------------------------
async function scrapeFixturesHTML() {
  const url = "https://example.com/fixtures"; // εδώ θα μπει η πραγματική πηγή
  const html = await fetchHTML(url);
  return html;
}

// --------------------------------------------------
// FEED STORAGE (optional caching)
// --------------------------------------------------
import fs from "fs";
import path from "path";

async function saveRawFeed(name: string, data: any) {
  try {
    const filePath = path.join(__dirname, `../../feeds/${name}.json`);
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
  } catch (err) {
    console.error("Feed save error:", err);
  }
}

// --------------------------------------------------
// NORMALIZATION
// --------------------------------------------------
function normalizeInternalFixtures(raw: any[]) {
  return raw.map(item => ({
    season_id: item.season_id ?? null,
    league_id: item.league_id ?? null,
    home_team_id: item.home_team_id ?? null,
    away_team_id: item.away_team_id ?? null,
    date: item.date ?? null,
    status: item.status ?? "unknown",
    home_score: item.home_score ?? null,
    away_score: item.away_score ?? null
  }));
}
