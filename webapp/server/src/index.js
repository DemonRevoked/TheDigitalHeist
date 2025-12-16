import express from 'express';
import cors from 'cors';
import morgan from 'morgan';
import dotenv from 'dotenv';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

import ChallengeStore from './challengeStore.js';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PORT = process.env.PORT || 4000;
const CLIENT_ORIGIN = process.env.CLIENT_ORIGIN;
// From /app/server/src -> /app
const PROJECT_ROOT = path.resolve(__dirname, '..', '..');
const CHALLENGES_DIR = path.resolve(
  PROJECT_ROOT,
  process.env.CHALLENGES_DIR || 'data/challenges'
);
const KEYS_DIR = path.resolve(
  PROJECT_ROOT,
  process.env.KEYS_DIR || 'data/keys'
);
const CLIENT_DIST = path.resolve(PROJECT_ROOT, 'client/dist');
const MONGODB_URI = process.env.MONGODB_URI;

const app = express();

app.use(
  cors({
    origin: CLIENT_ORIGIN || '*'
  })
);
app.use(express.json());
app.use(morgan('dev'));

// Expose challenge assets and key files for download
app.use('/static/challenges', express.static(CHALLENGES_DIR));
app.use('/static/keys', express.static(KEYS_DIR));

const store = new ChallengeStore({
  challengeDir: CHALLENGES_DIR,
  keysDir: KEYS_DIR,
  mongoUri: MONGODB_URI
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.get('/api/challenges', async (req, res, next) => {
  try {
    const challenges = await store.list();
    res.json({ challenges });
  } catch (err) {
    next(err);
  }
});

app.get('/api/challenges/:slug', async (req, res, next) => {
  try {
    const challenge = await store.get(req.params.slug);
    if (!challenge) {
      return res.status(404).json({ message: 'Challenge not found' });
    }
    res.json({ challenge });
  } catch (err) {
    next(err);
  }
});

app.use((err, req, res, _next) => {
  console.error(err);
  res
    .status(500)
    .json({ message: 'Unexpected server error', detail: err.message });
});

// Serve built client if available
if (fs.existsSync(CLIENT_DIST)) {
  app.use(express.static(CLIENT_DIST));
  app.get('*', (req, res, next) => {
    if (req.path.startsWith('/api')) return next();
    const indexPath = path.join(CLIENT_DIST, 'index.html');
    if (fs.existsSync(indexPath)) {
      return res.sendFile(indexPath);
    }
    return res.status(404).end();
  });
}

const start = async () => {
  await store.init();
  app.listen(PORT, () => {
    console.log(`Challenge landing server listening on :${PORT}`);
  });
};

start();
