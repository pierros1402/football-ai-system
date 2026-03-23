// backend/ingestion/savers/saveFixtures.ts

import { Pool } from "pg";

// --------------------------------------------------
// POSTGRES CONNECTION POOL
// --------------------------------------------------
const pool = new Pool({
  host: process.env.DB_HOST,
  port: Number(process.env.DB_PORT ?? 5432),
  user: process.env.DB_USER,
  password: process.env.DB_PASS,
  database: process.env.DB_NAME,
  max: 10
});

// --------------------------------------------------
// MAIN SAVE FUNCTION
// --------------------------------------------------
export async function saveFixtures(fixtures: any[]) {
  if (fixtures.length === 0) {
    console.log("No fixtures to save.");
    return;
  }

  console.log(`Saving ${fixtures.length} fixtures to DB...`);

  const client = await pool.connect();

  try {
    await client.query("BEGIN");

    for (const f of fixtures) {
      await saveSingleFixture(client, f);
    }

    await client.query("COMMIT");
    console.log("Fixtures saved successfully.");
  } catch (err) {
    await client.query("ROLLBACK");
    console.error("Error saving fixtures:", err);
  } finally {
    client.release();
  }
}

// --------------------------------------------------
// SAVE A SINGLE FIXTURE (UPSERT)
// --------------------------------------------------
async function saveSingleFixture(client: any, f: any) {
  const query = `
    INSERT INTO fixtures (
      external_id,
      season_id,
      league_id,
      home_team_id,
      away_team_id,
      date,
      status,
      home_score,
      away_score
    )
    VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
    ON CONFLICT (external_id)
    DO UPDATE SET
      season_id = EXCLUDED.season_id,
      league_id = EXCLUDED.league_id,
      home_team_id = EXCLUDED.home_team_id,
      away_team_id = EXCLUDED.away_team_id,
      date = EXCLUDED.date,
      status = EXCLUDED.status,
      home_score = EXCLUDED.home_score,
      away_score = EXCLUDED.away_score;
  `;

  const values = [
    f.external_id ?? generateExternalId(f),
    f.season_id,
    f.league_id,
    f.home_team_id,
    f.away_team_id,
    f.date,
    f.status,
    f.home_score,
    f.away_score
  ];

  await client.query(query, values);
}

// --------------------------------------------------
// EXTERNAL ID GENERATOR (fallback)
// --------------------------------------------------
function generateExternalId(f: any) {
  return (
    "fx_" +
    `${f.home_team_id}_${f.away_team_id}_${f.date}`
      .toLowerCase()
      .replace(/[^a-z0-9]/g, "_")
  );
}
