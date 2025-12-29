import fs from 'fs';
import path from 'path';
import mongoose from 'mongoose';

const ChallengeSchema = new mongoose.Schema(
  {
    slug: { type: String, unique: true, required: true },
    title: String,
    category: String,
    difficulty: { type: String, default: 'unknown' },
    points: { type: Number, default: 0 },
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

// Calculate points based on difficulty
const calculatePoints = (difficulty) => {
  switch (difficulty) {
    case 'easy':
      return 100;
    case 'medium':
      return 250;
    case 'hard':
      return 500;
    default:
      return 0;
  }
};

// Difficulty order for sorting (easy first, then medium, then hard)
const difficultyOrder = {
  'easy': 1,
  'medium': 2,
  'hard': 3,
  'unknown': 4
};

const challengeStories = {
  're-01-confession-app':
    'The Directorate issues its agents a journaling app called "Confession App" for "well-being tracking." But the Professor suspects it hides secret operational logs. The team obtains the binary and reverse engineers it, decrypting obfuscated strings to find a hardcoded passphrase. When entered correctly, the app connects to a hidden server and reveals the first clue: the location of the Directorate\'s network gateway.',
  're-02-evidence-tampering':
    'Berlin discovers a heavily obfuscated binary called "Evidence Tampering Console" used by the Directorate\'s internal cleanup unit. The stripped binary contains encrypted strings and timestamp manipulation logic. Reverse engineering reveals the validation algorithm—players must derive the correct tampered timestamp that passes the Directorate\'s rewrite verification. This confirms they systematically rewrite digital history, critical intel for staging the heist without raising alarms.',
  'mob-01':
    'To infiltrate the Directorate\'s mobile ecosystem, Rio obtains an Android cloud backup of an operative\'s phone. The team extracts deleted SMS threads containing network authentication hints. These form the first foothold into their infrastructure.',
  'mob-02':
    'Tokyo uncovers a Directorate "Safety App" secretly tracking citizens. APK analysis identifies the tracking API endpoint—a covert beacon server that doubles as a clandestine command channel. This beacon server becomes the crew\'s entry tunnel.',
  'df-01-night-walk-photo':
    'A Directorate field agent posts a photo online. The crew performs EXIF reconstruction and metadata analysis, revealing a hidden operational unit behind the agent. This confirms multiple nodes in the Directorate’s surveillance chain.',
  'df-02-burned-usb':
    'A half-destroyed USB stick retrieved by Nairobi contains scrambled operational files. File carving reveals a fragmented network diagram of the Directorate’s core systems—the digital equivalent of the Royal Mint blueprint.',
  'web-01-royalmint':
    'Behind a public memorial page, Denver brute-forces directories and finds deleted policy documents explaining how A₀ automates digital manipulation. This is proof the AI exists.',
  'web-02-ticket-to-the-vault':
    'The Directorate\'s "tip portal" is vulnerable to SQLi/IDOR. The crew reads internally filed reports and finds an anonymous complaint from a whistleblower describing the system architecture.',
  'web-03-safehouse':
    'The Professor identifies the crew\'s final web target: the Directorate\'s internal network scanner with a hidden vault server. Helsinki discovers an SSRF vulnerability in the URL preview feature. Using a clever allowlist bypass with the @ character, the crew pivots to an internal-only service and retrieves the Professor\'s hidden escape route coordinates. This demonstrates how deeply the Directorate\'s systems can be compromised through chained vulnerabilities.',
  'crypto-01-intercepted-comms':
    'An operative\'s encrypted notes use a weak cipher. Decrypting them reveals internal codenames for A₀ submodules.',
  'crypto-02-vault-breach':
    'Lisbon identifies an AES-encrypted memo. Using known plaintext structures, the crew recovers a name: The Directorate\'s chief architect. They now know who built A₀.',
  'crypto-03-quantum-safe':
    'The Directorate\'s RSA vault uses poor padding. The crew factors it and extracts the master key index, giving theoretical access to the Digital Vault. The final heist phase begins.',
  'net-01-onion-pcap':
    'Tokyo recovers a span-port PCAP from a compromised switch. The payloads are noise, but the headers aren’t: VLAN + GRE tunnels and timestamp patterns hide a deliberate signal. Rebuild the hidden message and identify the rogue engineer feeding Δ₀.',
  'net-02-doh-rhythm':
    'The Directorate claims their DNS is “safe” because it’s encrypted. Nairobi spots a rhythm in TLS record sizes and timing—an exfil channel hiding in metadata. Reconstruct the message without decrypting anything and extract the tunnel key.',
  'sc-01':
    'An educational portal used by Directorate interns contains an input flaw leaking internal communications. These messages contain API tokens for the development server.',
  'sc-02':
    'The crew analyzes a file-upload backend that silently overwrites files. This vulnerability becomes their method to replace surveillance logs with fabricated decoy logs—the same tactic the Directorate used, now turned against them.',
  'exp-01':
    'A compromised Directorate laptop is locked, but privilege escalation gives the crew access. Inside they find local credentials for the AI training environment.',
  'exp-02':
    'This is the final vault. A chained exploit grants root access to the Directorate\'s central server. Inside, they uncover: the full A₀ source code, the training dataset, communication logs, and instructions for future mass surveillance rollouts. This is the digital equivalent of breaking into the Bank of Spain\'s gold vault.',
  'ai-01-artemis':
    'The team analyzes chat logs between agents and the A₀ system. Patterns show the AI has been impersonating human field officers, steering decisions. A₀ is not just a tool. It is an autonomous strategist—like a digital Alicia Sierra.',
  'ai-02-cerberus':
    'The final revelation: A₀ generates deepfake audio messages to mislead operatives and shape narratives. The crew identifies inconsistencies and proves the system manipulates internal command structures. The world must see this.'
};

// Difficulty mapping based on Tasks.md
const challengeDifficulties = {
  're-01-confession-app': 'easy',
  're-02-evidence-tampering': 'hard',
  'mob-01': 'easy',
  'mob-02': 'hard',
  'df-01-night-walk-photo': 'medium',
  'df-02-burned-usb': 'hard',
  'web-01-royalmint': 'easy',
  'web-02-ticket-to-the-vault': 'medium',
  'web-03-safehouse': 'hard',
  'crypto-01-intercepted-comms': 'easy',
  'crypto-02-vault-breach': 'medium',
  'crypto-03-quantum-safe': 'hard',
  'net-01-onion-pcap': 'medium',
  'net-02-doh-rhythm': 'hard',
  'sc-01': 'easy',
  'sc-02': 'medium',
  'exp-01': 'medium',
  'exp-02': 'hard',
  'ai-01-artemis': 'easy',
  'ai-02-cerberus': 'hard'
};

// Narrative order for cards on the landing page
const challengeOrder = [
  're-01-confession-app',
  're-02-evidence-tampering',
  'mob-01',
  'mob-02',
  'df-01-night-walk-photo',
  'df-02-burned-usb',
  'web-01-royalmint',
  'web-02-ticket-to-the-vault',
  'web-03-safehouse',
  'crypto-01-intercepted-comms',
  'crypto-02-vault-breach',
  'crypto-03-quantum-safe',
  'net-01-onion-pcap',
  'net-02-doh-rhythm',
  'sc-01',
  'sc-02',
  'exp-01',
  'exp-02',
  'ai-01-artemis',
  'ai-02-cerberus'
];

export default class ChallengeStore {
  constructor({ challengeFilesDir, mongoUri, sshHost }) {
    this.challengeFilesDir = challengeFilesDir;
    this.mongoUri = mongoUri;
    this.sshHost = sshHost;
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
    // Get challenges from filesystem directories
    const filesystemChallenges = [];
    if (fs.existsSync(this.challengeFilesDir)) {
      const challengeDirs = fs
        .readdirSync(this.challengeFilesDir, { withFileTypes: true })
        .filter((entry) => entry.isDirectory());

      filesystemChallenges.push(...challengeDirs.map((dirent) => dirent.name));
    }

    // Get all defined challenges (from challengeStories)
    const allDefinedChallenges = Object.keys(challengeStories);
    
    // Combine filesystem and defined challenges, removing duplicates
    const allChallengeSlugs = [...new Set([...filesystemChallenges, ...allDefinedChallenges])];

    const items = allChallengeSlugs.map((slug) => {
      const basePath = path.join(this.challengeFilesDir, slug);
      const [category, order] = slug.split('-');

      // Collect files if directory exists
      const files = this.collectFiles(basePath, (relativePath, fullPath) => ({
        name: relativePath,
        url: `/static/challenge-files/${slug}/${relativePath}`,
        size: this.safeFileSize(fullPath)
      }));

      const difficulty = challengeDifficulties[slug] || 'unknown';
      
      // Add SSH credentials for challenges that need them
      // Host will be set dynamically in the API based on request or environment variable
      const sshCredentials = {};
      if (slug === 're-01-confession-app') {
        sshCredentials.username = 'rio';
        sshCredentials.password = 'RedCipher@1';
        sshCredentials.host = this.sshHost; // Will be set in API if not provided
        sshCredentials.port = 2222;
      } else if (slug === 're-02-evidence-tampering') {
        sshCredentials.username = 'denver';
        sshCredentials.password = 'RedCipher@2';
        sshCredentials.host = this.sshHost; // Will be set in API if not provided
        sshCredentials.port = 2223;
      }
      
      // Add platform URLs for challenges that have web interfaces
      // Host will be set dynamically in the API based on request or environment variable
      const platformUrl = {};
      if (slug === 'ai-01-artemis') {
        platformUrl.port = 8080;
        platformUrl.host = this.sshHost; // Will be set in API if not provided
      } else if (slug === 'ai-02-cerberus') {
        platformUrl.port = 8081;
        platformUrl.host = this.sshHost; // Will be set in API if not provided
      } else if (slug === 'web-01-royalmint') {
        platformUrl.port = 5001;
        platformUrl.host = this.sshHost; // Will be set in API if not provided
      } else if (slug === 'web-02-ticket-to-the-vault') {
        platformUrl.port = 5002;
        platformUrl.host = this.sshHost; // Will be set in API if not provided
      } else if (slug === 'web-03-safehouse') {
        platformUrl.port = 5003;
        platformUrl.host = this.sshHost; // Will be set in API if not provided
      }
      
      // Check if challenge is available:
      // - Has files in challenge-files directory, OR
      // - Has SSH credentials configured, OR
      // - Has platform URL configured
      const hasSshCredentials = Object.keys(sshCredentials).length > 0;
      const hasPlatformUrl = Object.keys(platformUrl).length > 0;
      const hasFiles = files.length > 0;
      const challengeAvailable = hasFiles || hasSshCredentials || hasPlatformUrl;
      
      return {
        slug,
        title: formatTitle(slug),
        category,
        difficulty,
        points: calculatePoints(difficulty),
        shortDescription: challengeStories[slug] || 'Challenge files available for download.',
        files,
        credentials: [],
        sshCredentials: hasSshCredentials ? sshCredentials : undefined,
        platformUrl: hasPlatformUrl ? platformUrl : undefined,
        tags: [category],
        available: challengeAvailable
      };
    });

    // Sort by difficulty first (easy, medium, hard), then by narrative order within each difficulty
    return items.sort((a, b) => {
      // First, sort by difficulty
      const difficultyA = difficultyOrder[a.difficulty] || difficultyOrder['unknown'];
      const difficultyB = difficultyOrder[b.difficulty] || difficultyOrder['unknown'];
      if (difficultyA !== difficultyB) {
        return difficultyA - difficultyB;
      }
      // If same difficulty, sort by narrative order
      const ia = challengeOrder.indexOf(a.slug);
      const ib = challengeOrder.indexOf(b.slug);
      const va = ia === -1 ? Number.MAX_SAFE_INTEGER : ia;
      const vb = ib === -1 ? Number.MAX_SAFE_INTEGER : ib;
      if (va !== vb) return va - vb;
      // If not in narrative order, sort alphabetically
      return a.slug.localeCompare(b.slug);
    });
  }

  collectFiles(basePath, mapper) {
    const results = [];
    const walk = (current, prefix = '') => {
      if (!fs.existsSync(current)) return;
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


  safeFileSize(fullPath) {
    try {
      const stats = fs.statSync(fullPath);
      return stats.size;
    } catch (err) {
      return undefined;
    }
  }
}
