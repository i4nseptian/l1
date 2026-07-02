const BASE = '/api';

export async function getLeagues() {
  const res = await fetch(`${BASE}/leagues`);
  return res.json();
}

export async function getMatches(league = '', date = '', includePredictions = false) {
  const params = new URLSearchParams();
  if (league) params.set('league', league);
  if (date) params.set('date', date);
  if (includePredictions) params.set('predictions', 'true');
  const res = await fetch(`${BASE}/matches?${params}`);
  return res.json();
}

export async function getMatch(id) {
  const res = await fetch(`${BASE}/matches/${id}`);
  return res.json();
}

export async function getPrediction(id) {
  const res = await fetch(`${BASE}/matches/${id}/prediction`);
  return res.json();
}

export async function getFactors() {
  const res = await fetch(`${BASE}/factors`);
  return res.json();
}

export async function getCustomRules() {
  const res = await fetch(`${BASE}/custom-logic/`);
  return res.json();
}

export async function createCustomRule(rule) {
  const res = await fetch(`${BASE}/custom-logic/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(rule),
  });
  return res.json();
}

export async function deleteCustomRule(id) {
  const res = await fetch(`${BASE}/custom-logic/${id}`, { method: 'DELETE' });
  return res.json();
}

export async function manualPredict(data) {
  const res = await fetch(`${BASE}/predict/manual`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function getTeams(search = '', league = '') {
  const params = new URLSearchParams();
  if (search) params.set('search', search);
  if (league) params.set('league', league);
  const res = await fetch(`${BASE}/teams?${params}`);
  return res.json();
}

export async function getTeamLeagues() {
  const res = await fetch(`${BASE}/teams/leagues`);
  return res.json();
}

export async function syncTeams() {
  const res = await fetch(`${BASE}/teams/sync`, { method: 'POST' });
  return res.json();
}

export async function syncTeamsFromScraper() {
  const res = await fetch(`${BASE}/teams/sync-from-scraper`, { method: 'POST' });
  return res.json();
}
