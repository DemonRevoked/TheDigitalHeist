import { useState } from 'react';

export default function ChallengeCard({ challenge, categoryLabel }) {
  const { title, slug, shortDescription, files = [], credentials = [] } =
    challenge;

  const [isOpen, setIsOpen] = useState(false);
  const fileCount = files.length;
  const credCount = credentials.length;
  const firstFile = files[0];

  return (
    <article className={`card ${isOpen ? 'expanded' : 'collapsed'}`}>
      <header className="card-header">
        <div className="card-headline">
          <div className="chip">{categoryLabel}</div>
          <h2>{title}</h2>
          <p className="slug">/{slug}</p>
        </div>
        <button
          className="pill action"
          type="button"
          onClick={() => setIsOpen((v) => !v)}
        >
          {isOpen ? 'Close dossier' : 'Open dossier'}
        </button>
      </header>

      <p className="summary">
        {shortDescription || 'Briefing ready. Tap to view details.'}
      </p>

      {!isOpen ? null : (
        <section className="details">
          <div className="quick-stats">
            <span className="pill">
              {fileCount} {fileCount === 1 ? 'file' : 'files'}
            </span>
            <span className="pill ghost">
              {credCount} {credCount === 1 ? 'key' : 'keys'}
            </span>
          </div>

          {firstFile ? (
            <a className="primary-btn" href={firstFile.url} download>
              Download files
            </a>
          ) : (
            <div className="muted">No files available yet.</div>
          )}

          <section className="lists">
            <div className="list">
              <div className="list-title">Payload</div>
              {files.length === 0 ? (
                <p className="muted">No payload files yet.</p>
              ) : (
                <ul>
                  {files.map((file) => (
                    <li key={file.url}>
                      <a href={file.url} download>
                        {file.name}
                      </a>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="list">
              <div className="list-title">Access Keys / Creds</div>
              {credentials.length === 0 ? (
                <p className="muted">No matching keys in the vault.</p>
              ) : (
                <ul>
                  {credentials.map((cred) => (
                    <li key={cred.url}>
                      <a href={cred.url} download>
                        {cred.name}
                      </a>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </section>
        </section>
      )}
    </article>
  );
}
