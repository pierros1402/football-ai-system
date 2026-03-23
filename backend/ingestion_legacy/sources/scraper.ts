// backend/ingestion/sources/scraper.ts

import axios from "axios";

/**
 * Βασικός internal scraper
 * Διαβάζει HTML από οποιοδήποτε URL χωρίς API keys.
 */
export async function fetchHTML(url: string): Promise<string> {
  try {
    const response = await axios.get(url, {
      headers: {
        "User-Agent": "Mozilla/5.0 (InternalAutonomousEngine/1.0)"
      }
    });

    return response.data;
  } catch (err) {
    console.error("Scraper error:", err);
    return "";
  }
}
