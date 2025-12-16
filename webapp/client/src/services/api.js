const API_BASE = import.meta.env.VITE_API_BASE || '';

export async function fetchChallenges() {
  const res = await fetch(`${API_BASE}/api/challenges`);
  if (!res.ok) {
    throw new Error(`API error ${res.status}`);
  }
  const { challenges = [] } = await res.json();
  return challenges;
}
