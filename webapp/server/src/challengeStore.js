import fs from 'fs';
import path from 'path';
import mongoose from 'mongoose';

const ChallengeSchema = new mongoose.Schema(
  {
    slug: { type: String, unique: true, required: true },
    title: String,
    category: String,
    difficulty: { type: String, default: 'unknown' },
    shortDescription: String,
    files: [
      {
        name: String,
        url: String,
        size: Number
      }
    ],
    credentials: [
      {
        name: String,
        url: String
      }
    ],
    tags: [String]
  },
  { timestamps: true }
);

const ChallengeModel =
  mongoose.models.Challenge || mongoose.model('Challenge', ChallengeSchema);

const formatTitle = (slug) =>
  slug
    .split('-')
    .map((part) => part.replace(/\b\w/g, (c) => c.toUpperCase()))
    .join(' ');

export default class ChallengeStore {
  constructor({ challengeDir, keysDir, mongoUri }) {
    this.challengeDir = challengeDir;
    this.keysDir = keysDir;
    this.mongoUri = mongoUri;
    this.connected = false;
  }

  async init() {
    if (!this.mongoUri) return;

    try {
      await mongoose.connect(this.mongoUri);
      this.connected = true;
      // Ensure index exists for slug uniqueness
      await ChallengeModel.init();
      // Only seed if empty
      const count = await ChallengeModel.estimatedDocumentCount();
      if (count === 0) {
        const seeded = await ChallengeModel.insertMany(
          this.loadFromFilesystem()
        );
        console.log(`Seeded ${seeded.length} challenges into MongoDB`);
      }
    } catch (err) {
      console.error(
        'Mongo connection failed, falling back to filesystem data:',
        err.message
      );
      this.connected = false;
    }
  }

  async list() {
    if (this.connected) {
      return ChallengeModel.find().lean();
    }
    return this.loadFromFilesystem();
  }

  async get(slug) {
    if (this.connected) {
      return ChallengeModel.findOne({ slug }).lean();
    }
    return this.loadFromFilesystem().find((c) => c.slug === slug);
  }

  loadFromFilesystem() {
    if (!fs.existsSync(this.challengeDir)) return [];
    const challengeDirs = fs
      .readdirSync(this.challengeDir, { withFileTypes: true })
      .filter((entry) => entry.isDirectory());

    return challengeDirs.map((dirent) => {
      const slug = dirent.name;
      const basePath = path.join(this.challengeDir, slug);
      const [category, order] = slug.split('-');
      const keyPrefix = `${category}-${order}`;

      const files = this.collectFiles(basePath, (relativePath, fullPath) => ({
        name: relativePath,
        url: `/static/challenges/${slug}/${relativePath}`,
        size: this.safeFileSize(fullPath)
      }));

      const credentials = this.collectCredentials(keyPrefix);

      return {
        slug,
        title: formatTitle(slug),
        category,
        difficulty: 'unknown',
        shortDescription:
          'Challenge files and credentials available for download.',
        files,
        credentials,
        tags: [category]
      };
    });
  }

  collectFiles(basePath, mapper) {
    const results = [];
    const walk = (current, prefix = '') => {
      const entries = fs.readdirSync(current, { withFileTypes: true });
      entries.forEach((entry) => {
        const full = path.join(current, entry.name);
        const rel = path.join(prefix, entry.name);
        if (entry.isDirectory()) {
          walk(full, rel);
        } else {
          results.push(mapper(rel, full));
        }
      });
    };

    if (fs.existsSync(basePath)) {
      walk(basePath);
    }

    return results;
  }

  collectCredentials(keyPrefix) {
    if (!fs.existsSync(this.keysDir)) return [];

    const keyFiles = fs
      .readdirSync(this.keysDir, { withFileTypes: true })
      .filter(
        (entry) =>
          entry.isFile() &&
          entry.name.toLowerCase().startsWith(keyPrefix.toLowerCase())
      );

    return keyFiles.map((entry) => ({
      name: entry.name,
      url: `/static/keys/${entry.name}`
    }));
  }

  safeFileSize(fullPath) {
    try {
      const stats = fs.statSync(fullPath);
      return stats.size;
    } catch (err) {
      return undefined;
    }
  }
}
