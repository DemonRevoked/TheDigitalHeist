function runStartupSelfCheck({ safeJoinLogsPath, logsDir }) {
  // Validate inputs
  if (typeof safeJoinLogsPath !== 'function') {
    return false;
  }
  if (!logsDir || typeof logsDir !== 'string') {
    return false;
  }

  // Test 1: Legitimate file should work without throwing
  let test1Pass = false;
  try {
    const good = safeJoinLogsPath(logsDir, "heist.log");
    // Verify it returns a non-empty string
    test1Pass = !!(good && typeof good === 'string' && good.length > 0);
  } catch (e) {
    // If it throws for a legitimate file, that's bad
    test1Pass = false;
  }
  
  if (!test1Pass) {
    return false;
  }

  // Test 2: Traversal case must throw (be blocked)
  let test2Pass = false;
  try {
    safeJoinLogsPath(logsDir, "../secrets/vault.key");
    // If we get here, it didn't throw - that's bad
    test2Pass = false;
  } catch (e) {
    // Good! It threw, which means traversal is blocked
    // Verify it's the right kind of error
    test2Pass = !!(e && (e.message || e.toString()));
  }
  
  // Both tests must pass
  return test1Pass && test2Pass;
}

module.exports = { runStartupSelfCheck };

