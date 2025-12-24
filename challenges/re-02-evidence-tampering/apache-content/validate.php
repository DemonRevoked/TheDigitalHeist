<?php
// Return key/flag for evidence tampering challenge
// Validation is done by the C binary, not here

// Flag value - hardcoded in PHP
$CHALLENGE_FLAG = "TDHCTF{tampered_time_offset}";

header('Content-Type: application/json');

// Only accept POST requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['status' => 'error', 'message' => 'Method not allowed']);
    exit;
}

// Read key from file
$key_file = '/var/www/html/key.txt';
$key = 'offline-session-key';

if (file_exists($key_file)) {
    $key = trim(file_get_contents($key_file));
}

// Use flag from environment variable (set by entrypoint)
$flag = $CHALLENGE_FLAG;

// Return success with key and flag (no validation needed - C binary handles that)
http_response_code(200);
echo json_encode([
    'status' => 'success',
    'key' => $key,
    'flag' => $flag
], JSON_UNESCAPED_SLASHES);
?>

