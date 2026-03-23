// backend/ingestion/sources/ai_extractor.ts

import * as cheerio from "cheerio";

/**
 * AI-like extraction module
 * Διαβάζει HTML και εξάγει fixtures σε structured μορφή.
 * Αυτό είναι το πρώτο στάδιο. Θα το εξελίξουμε σε πλήρη AI extraction.
 */
export async function extractFixturesFromHTML(html: string) {
  const $ = cheerio.load(html);

  const fixtures: any[] = [];

  // -------------------------------
  // ΠΑΡΑΔΕΙΓΜΑ: Αν το HTML έχει blocks με fixtures
  // Θα το κάνουμε πιο έξυπνο στα επόμενα βήματα
  // -------------------------------
  $(".fixture").each((_, el) => {
    const home = $(el).find(".home-team").text().trim();
    const away = $(el).find(".away-team").text().trim();
    const date = $(el).find(".match-date").text().trim();
    const score = $(el).find(".score").text().trim();

    let home_score = null;
    let away_score = null;

    if (score.includes("-")) {
      const parts = score.split("-");
      home_score = parseInt(parts[0].trim());
      away_score = parseInt(parts[1].trim());
    }

    fixtures.push({
      season_id: null, // θα μπει από mapping
      league_id: null, // θα μπει από mapping
      home_team: home,
      away_team: away,
      date: date,
      status: score ? "finished" : "not_started",
      home_score,
      away_score
    });
  });

  return fixtures;
}
