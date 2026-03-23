// backend/ingestion/mappers/league_mapper.ts

import fs from "fs";
import path from "path";

/**
 * League Mapper
 * Αντιστοιχεί raw league names σε unified league IDs.
 */

const MAPPING_FILE = path.join(__dirname, "../../mappings/leagues.json");

// --------------------------------------------------
// LOAD MAPPINGS
// --------------------------------------------------
function loadMappings() {
  try {
    if (!fs.existsSync(MAPPING_FILE)) return {};
    const data = fs.readFileSync(MAPPING_FILE, "utf8");
    return JSON.parse(data);
  } catch (err) {
    console.error("Error loading league mappings:", err);
    return {};
  }
}

// --------------------------------------------------
// SAVE MAPPINGS
// --------------------------------------------------
function saveMappings(mappings: any) {
  try {
    fs.mkdirSync(path.dirname(MAPPING_FILE), { recursive: true });
    fs.writeFileSync(MAPPING_FILE, JSON.stringify(mappings, null, 2));
  } catch (err) {
    console.error("Error saving league mappings:", err);
  }
}

// --------------------------------------------------
// MAIN MAPPING FUNCTION
// --------------------------------------------------
export async function mapLeagueName(rawName: string): Promise<string> {
  const mappings = loadMappings();

  // 1. Αν υπάρχει ήδη mapping → επιστρέφουμε το ID
  if (mappings[rawName]) {
    return mappings[rawName];
  }

  // 2. Fuzzy matching
  const matched = fuzzyMatch(rawName, Object.keys(mappings));
  if (matched) {
    return mappings[matched];
  }

  // 3. Αν δεν υπάρχει → δημιουργούμε νέο ID
  const newId = generateLeagueId(rawName);
  mappings[rawName] = newId;

  saveMappings(mappings);

  return newId;
}

// --------------------------------------------------
// SIMPLE FUZZY MATCHING
// --------------------------------------------------
function fuzzyMatch(raw: string, existing: string[]): string | null {
  const normalized = raw.toLowerCase().replace(/[^a-z0-9]/g, "");

  for (const name of existing) {
    const n = name.toLowerCase().replace(/[^a-z0-9]/g, "");
    if (n === normalized) return name;
    if (n.includes(normalized)) return name;
    if (normalized.includes(n)) return name;
  }

  return null;
}

// --------------------------------------------------
// ID GENERATOR
// --------------------------------------------------
function generateLeagueId(name: string): string {
  return "league_" + name.toLowerCase().replace(/[^a-z0-9]/g, "_");
}
