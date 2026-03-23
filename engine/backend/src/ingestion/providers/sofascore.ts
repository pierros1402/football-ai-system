// src/ingestion/providers/sofascore.ts

const BASE = "https://api.sofascore.com/api/v1";

async function fetchJson(url: string) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Sofascore error: ${res.status}`);
  return res.json();
}

export const sofascoreApi = {
  async getCompetition(id: string) {
    const data = await fetchJson(`${BASE}/unique-tournament/${id}`);
    return data.uniqueTournament;
  },

  async getSeason(id: string) {
    const data = await fetchJson(`${BASE}/season/${id}`);
    return data.season;
  },

  async getTeam(id: string) {
    const data = await fetchJson(`${BASE}/team/${id}`);
    return data.team;
  },

  async getPlayer(id: string) {
    const data = await fetchJson(`${BASE}/player/${id}`);
    return data.player;
  },

  async getMatch(id: string) {
    const data = await fetchJson(`${BASE}/event/${id}`);
    console.log("RAW EVENT:", JSON.stringify(data.event, null, 2));
    return data.event;
  }, // <-- ΤΟ ΚΟΜΜΑ ΠΟΥ ΕΛΕΙΠΕ

  async getEvents(id: string) {
    const data = await fetchJson(`${BASE}/event/${id}/incidents`);
    return data.incidents;
  },

  async getStats(id: string) {
    const data = await fetchJson(`${BASE}/event/${id}/statistics`);
    return data.statistics;
  },
};
