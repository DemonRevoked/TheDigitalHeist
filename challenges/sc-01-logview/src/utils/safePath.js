const path = require("path");

/**
 * TODO (player): Fix path traversal.
 *
 * Requirements:
 * - Only allow access to files inside logsDir
 * - Block:
 *   - ../ and ..\
 *   - absolute paths
 *   - url-encoded traversal (treat input as-is)
 * - Allow typical log filenames like "heist.log"
 */
function safeJoinLogsPath(logsDir, userFile) {
  // VULNERABLE: naive join
  return path.join(logsDir, userFile);
}

module.exports = { safeJoinLogsPath };
