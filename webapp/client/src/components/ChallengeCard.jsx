import { useState } from 'react';

export default function ChallengeCard({ challenge, categoryLabel }) {
  const { title, slug, shortDescription, files = [], difficulty, points = 0, sshCredentials, platformUrl, available = true } = challenge;

  const [isOpen, setIsOpen] = useState(false);
  const fileCount = files.length;

  const difficultyClass = difficulty && difficulty !== 'unknown' ? `card-difficulty-${difficulty}` : '';
  const inactiveClass = !available ? 'card-inactive' : '';

  const handleClick = () => {
    if (available) {
      setIsOpen(true);
    }
  };

  const handleKeyDown = (e) => {
    if (available && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault();
      setIsOpen(true);
    }
  };

  return (
    <>
      <article
        className={`card collapsed ${isOpen ? 'card-active' : ''} ${difficultyClass} ${inactiveClass}`}
        role="button"
        tabIndex={available ? 0 : -1}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        aria-disabled={!available}
      >
        <header className="card-header">
          <div className="card-headline">
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
              <div className="chip">{categoryLabel}</div>
              {!available && (
                <div className="coming-soon-badge">
                  Coming Soon
                </div>
              )}
              {available && difficulty && difficulty !== 'unknown' && (
                <div className={`difficulty-badge difficulty-${difficulty}`}>
                  {difficulty === 'easy' && '🥉 Easy'}
                  {difficulty === 'medium' && '🥈 Medium'}
                  {difficulty === 'hard' && '🥇 Hard'}
                </div>
              )}
              {available && points > 0 && (
                <div className="points-badge">
                  {points} pts
                </div>
              )}
            </div>
            <h2>{title}</h2>
          </div>
        </header>
      </article>

      {!isOpen ? null : (
        <div className="modal-backdrop" onClick={() => setIsOpen(false)}>
          <div
            className="modal-card"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-label={`${title} details`}
          >
            <div className="modal-header">
              <div>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap', marginBottom: '0.5rem' }}>
                  <div className="chip">{categoryLabel}</div>
                  {difficulty && difficulty !== 'unknown' && (
                    <div className={`difficulty-badge difficulty-${difficulty}`}>
                      {difficulty === 'easy' && '🥉 Easy'}
                      {difficulty === 'medium' && '🥈 Medium'}
                      {difficulty === 'hard' && '🥇 Hard'}
                    </div>
                  )}
                  {points > 0 && (
                    <div className="points-badge">
                      {points} pts
                    </div>
                  )}
                </div>
                <h2>{title}</h2>
              </div>
              <button
                className="pill action"
                type="button"
                onClick={() => setIsOpen(false)}
              >
                Close
              </button>
            </div>

            <p className="summary">
              {shortDescription ||
                'Intel package ready. Pull files and keys directly from the vault.'}
            </p>

            <div className="quick-stats">
              <span className="pill">
                {fileCount} {fileCount === 1 ? 'file' : 'files'}
              </span>
            </div>

            {sshCredentials && (
              <section className="lists" style={{ marginBottom: '1.5rem' }}>
                <div className="list">
                  <div className="list-title">SSH Access</div>
                  <div style={{ 
                    background: 'var(--surface-secondary, #1a1a1a)', 
                    padding: '1rem', 
                    borderRadius: '8px',
                    fontFamily: 'monospace',
                    fontSize: '0.9rem'
                  }}>
                    <div style={{ marginBottom: '0.5rem' }}>
                      <strong>Host:</strong> {sshCredentials.host || 'localhost'}
                    </div>
                    <div style={{ marginBottom: '0.5rem' }}>
                      <strong>Port:</strong> {sshCredentials.port || '22'}
                    </div>
                    <div style={{ marginBottom: '0.5rem' }}>
                      <strong>Username:</strong> {sshCredentials.username}
                    </div>
                    <div style={{ marginBottom: '0.5rem' }}>
                      <strong>Password:</strong> {sshCredentials.password}
                    </div>
                    <div style={{ 
                      marginTop: '0.75rem', 
                      padding: '0.75rem', 
                      background: 'var(--surface-primary, #0a0a0a)', 
                      borderRadius: '4px',
                      fontSize: '0.85rem',
                      color: 'var(--text-secondary, #888)'
                    }}>
                      <strong>Command:</strong><br />
                      <code style={{ 
                        display: 'block', 
                        marginTop: '0.25rem',
                        wordBreak: 'break-all'
                      }}>
                        ssh -p {sshCredentials.port || '22'} {sshCredentials.username}@{sshCredentials.host || 'localhost'}
                      </code>
                    </div>
                  </div>
                </div>
              </section>
            )}

            {platformUrl && (
              <section className="lists" style={{ marginBottom: '1.5rem' }}>
                <div className="list">
                  <div className="list-title">Platform Access</div>
                  <div style={{ 
                    background: 'var(--surface-secondary, #1a1a1a)', 
                    padding: '1rem', 
                    borderRadius: '8px',
                    fontFamily: 'monospace',
                    fontSize: '0.9rem'
                  }}>
                    <div style={{ marginBottom: '0.5rem' }}>
                      <strong>Platform URL:</strong>
                    </div>
                    <div style={{ 
                      marginTop: '0.5rem', 
                      padding: '0.75rem', 
                      background: 'var(--surface-primary, #0a0a0a)', 
                      borderRadius: '4px',
                      fontSize: '0.85rem',
                      wordBreak: 'break-all'
                    }}>
                      <a 
                        href={`http://${platformUrl.host || 'localhost'}:${platformUrl.port}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{ 
                          color: 'var(--accent, #ff6b6b)',
                          textDecoration: 'none'
                        }}
                      >
                        http://{platformUrl.host || 'localhost'}:{platformUrl.port}
                      </a>
                    </div>
                  </div>
                </div>
              </section>
            )}

            {files.length === 0 ? (
              <div className="muted">No files available yet.</div>
            ) : (
              <section className="lists">
                <div className="list">
                  <div className="list-title">Download Challenge Files</div>
                  <ul>
                    {files.map((file) => (
                      <li key={file.url}>
                        <a href={file.url} download>
                          {file.name}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              </section>
            )}
          </div>
        </div>
      )}
    </>
  );
}
