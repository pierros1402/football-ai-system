// src/ingestion/providers/baseProvider.ts

export interface BaseProvider {
  // Επιτρέπουμε dynamic access (για health checks)
  [key: string]: any;

  // --- Core fetch methods ---
  fetchCompetition?(id: string): Promise<any>;
  fetchSeason?(id: string): Promise<any>;
  fetchTeam?(id: string): Promise<any>;
  fetchPlayer?(id: string): Promise<any>;
  fetchMatch?(id: string): Promise<any>;

  // --- Optional collections ---
  fetchEvents?(matchId: string): Promise<any[]>;
  fetchStats?(matchId: string): Promise<any[]>;
}
