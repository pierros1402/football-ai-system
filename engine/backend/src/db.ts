import pkg from "pg";
const { Pool } = pkg;

import { drizzle } from "drizzle-orm/node-postgres";

const pool = new Pool({
  connectionString: "postgres://postgres:1234@localhost:5432/football",
});

export const db = drizzle(pool);
