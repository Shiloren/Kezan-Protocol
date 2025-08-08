const API_URL = 'http://localhost:8000/api';

async function fetchJson(path) {
  try {
    const resp = await fetch(`${API_URL}${path}`);
    if (!resp.ok) return [];
    return await resp.json();
  } catch {
    return [];
  }
}

export const getConsejo = () => fetchJson('/consejo');
export const getGangas = () => fetchJson('/gangas');
export const getCrafteables = () => fetchJson('/crafteables');
