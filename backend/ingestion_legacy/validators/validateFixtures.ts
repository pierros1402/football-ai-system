// backend/ingestion/validators/validateFixtures.ts

/**
 * Full Validation Engine for Fixtures
 * Περιλαμβάνει:
 * - Basic validation
 * - Structural validation
 * - Intelligent validation
 * - Consistency checks
 */

export function validateFixtures(fixtures: any[]) {
  const valid: any[] = [];
  const errors: any[] = [];

  for (const f of fixtures) {
    const result = validateFixture(f);

    if (result.valid) {
      valid.push(f);
    } else {
      errors.push({
        fixture: f,
        errors: result.errors
      });
    }
  }

  if (errors.length > 0) {
    console.log("Validation errors detected:", JSON.stringify(errors, null, 2));
  }

  return valid;
}

// --------------------------------------------------
// VALIDATE SINGLE FIXTURE
// --------------------------------------------------
function validateFixture(f: any) {
  const errors: string[] = [];

  // -------------------------
  // BASIC VALIDATION
  // -------------------------
  if (!f.home_team_id) errors.push("Missing home_team_id");
  if (!f.away_team_id) errors.push("Missing away_team_id");
  if (!f.league_id) errors.push("Missing league_id");
  if (!f.season_id) errors.push("Missing season_id");
  if (!f.date) errors.push("Missing date");

  // -------------------------
  // STRUCTURAL VALIDATION
  // -------------------------
  if (f.home_team_id === f.away_team_id) {
    errors.push("Home and away team cannot be the same");
  }

  if (f.home_score != null && f.home_score < 0) {
    errors.push("Home score cannot be negative");
  }

  if (f.away_score != null && f.away_score < 0) {
    errors.push("Away score cannot be negative");
  }

  // -------------------------
  // INTELLIGENT VALIDATION
  // -------------------------
  if (f.status === "finished") {
    if (f.home_score == null || f.away_score == null) {
      errors.push("Finished match must have scores");
    }
  }

  if (f.status === "not_started") {
    if (f.home_score != null || f.away_score != null) {
      errors.push("Not started match cannot have scores");
    }
  }

  // -------------------------
  // DATE VALIDATION
  // -------------------------
  if (isNaN(Date.parse(f.date))) {
    errors.push("Invalid date format");
  }

  // -------------------------
  // FINAL RESULT
  // -------------------------
  return {
    valid: errors.length === 0,
    errors
  };
}
