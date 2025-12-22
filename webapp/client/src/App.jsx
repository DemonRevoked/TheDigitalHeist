import { useEffect, useState } from 'react';
import ChallengeCard from './components/ChallengeCard.jsx';
import { fetchChallenges } from './services/api.js';

const categories = {
  re: 'Reverse Engineering',
  ai: 'AI/ML',
  crypto: 'Cryptography',
  df: 'Digital Forensics',
  exp: 'Exploitation',
  mob: 'Mobile',
  net: 'Networking',
  sc: 'Secure Coding',
  web: 'Web'
};

export default function App() {
  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const data = await fetchChallenges();
        setChallenges(data);
      } catch (err) {
        setError(err.message || 'Failed to load challenges');
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const filtered = challenges.filter((c) => {
    const matchesSearch =
      c.title.toLowerCase().includes(search.toLowerCase()) ||
      c.slug.toLowerCase().includes(search.toLowerCase());
    const matchesCategory =
      categoryFilter === 'all' || c.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="page">
      <header className="hero hero-centered">
        <div className="hero-copy">
          <p className="eyebrow">The Digital Heist</p>
          <h1 className="heist-title">Heist Briefing Board</h1>
          <p className="welcome-note">
            Welcome to Operation Red Cipher. The Professor has assembled a crew
            of hackers, analysts, and cryptographers to breach the Directorate's
            Digital Vault and expose the A₀ surveillance system. Each challenge
            contains files and intel needed to progress. Solve them, extract the
            flags, and submit your findings on the WhizRange platform. The heist
            begins now.
          </p>
        </div>
      </header>

      {error && <div className="callout error">{error}</div>}

      {loading ? (
        <div className="loading">Fetching challenges...</div>
      ) : (
        <div className="grid">
          {filtered.map((challenge) => (
            <ChallengeCard
              key={challenge.slug}
              challenge={challenge}
              categoryLabel={categories[challenge.category] || 'General'}
            />
          ))}
          {filtered.length === 0 && (
            <div className="callout">No challenges match that filter.</div>
          )}
        </div>
      )}
      <footer className="footer">
        <p className="disclaimer">
          <strong>Disclaimer:</strong> This CTF is inspired by "La Casa de
          Papel" (Money Heist). All original rights remain with the creators of
          La Casa de Papel / Money Heist. This is a fan-created educational
          cybersecurity challenge.
        </p>
      </footer>
    </div>
  );
}
