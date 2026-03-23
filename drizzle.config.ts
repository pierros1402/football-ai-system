import { defineConfig } from "drizzle-kit";

export default defineConfig({
  schema: "./backend/src/schema.ts",
  out: "./drizzle",
  dialect: "postgresql",
  dbCredentials: {
    url: "postgres://postgres:1234@localhost:5432/football"
  }
});
