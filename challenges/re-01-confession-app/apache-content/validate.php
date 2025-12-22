<?php
// Validate passphrase and return key/flag if correct
// Expected passphrase from reverse engineering the binary
$EXPECTED_PASSPHRASE = "The network gateway location is now revealed to us";

// Flag value - hardcoded in PHP
$CHALLENGE_FLAG = "TDHCTF{confession_gateway_phrase}";

header('Content-Type: application/json');

// Only accept POST requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['status' => 'error', 'message' => 'Method not allowed']);
    exit;
}

// Read JSON input
$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!isset($data['passphrase'])) {
    http_response_code(400);
    echo json_encode(['status' => 'error', 'message' => 'Missing passphrase']);
    exit;
}

$passphrase = $data['passphrase'];

// Validate passphrase
if ($passphrase === $EXPECTED_PASSPHRASE) {
    // Read key from file (similar to how it was before)
    $key_file = '/var/www/html/key.txt';
    $key = 'offline-session-key';
    
    if (file_exists($key_file)) {
        $key = trim(file_get_contents($key_file));
    }
    
    // Use flag from environment variable (set by entrypoint)
    $flag = $CHALLENGE_FLAG;
    
    // Return success with key and flag
    http_response_code(200);
    echo json_encode([
        'status' => 'success',
        'key' => $key,
        'flag' => $flag
    ], JSON_UNESCAPED_SLASHES);
} else {
    // Invalid passphrase
    http_response_code(403);
    echo json_encode([
        'status' => 'error',
        'message' => 'Invalid passphrase'
    ]);
}
?>

