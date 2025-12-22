<?php
// Validate timestamp and return key/flag if correct
// Expected timestamp: 6510615554653383697 (computed from reverse engineering)
// The validation logic: ((timestamp ^ 0x5A5A5A5A5A5A5A5A) - 0x11111111) + 7 == 1700013377

// Flag value - hardcoded in PHP
$CHALLENGE_FLAG = "TDHCTF{tampered_time_offset}";

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

if (!isset($data['timestamp'])) {
    http_response_code(400);
    echo json_encode(['status' => 'error', 'message' => 'Missing timestamp']);
    exit;
}

$user_timestamp = $data['timestamp'];

// Validate timestamp using the same logic as the C binary
// Target value from encrypted data: 1700013377
$target_val = 1700013377;
$mask = 0x5A5A5A5A5A5A5A5A;
$bias = 0x11111111;

// Replicate the validation logic from evidence_tool.c
$temp1 = $user_timestamp ^ $mask;
$temp2 = $temp1 - $bias;
$computed = $temp2 + 7;

// Compare lower and upper 32 bits (same as C code)
$computed_low = $computed & 0xFFFFFFFF;
$computed_high = ($computed >> 32) & 0xFFFFFFFF;
$target_low = $target_val & 0xFFFFFFFF;
$target_high = ($target_val >> 32) & 0xFFFFFFFF;

if ($computed_low == $target_low && $computed_high == $target_high) {
    // Read key from file
    $key_file = '/var/www/html/key.txt';
    $key = 'offline-session-key';
    
    if (file_exists($key_file)) {
        $key = trim(file_get_contents($key_file));
    }
    
    // Use hardcoded flag
    $flag = $CHALLENGE_FLAG;
    
    // Return success with key and flag
    http_response_code(200);
    echo json_encode([
        'status' => 'success',
        'key' => $key,
        'flag' => $flag
    ], JSON_UNESCAPED_SLASHES);
} else {
    // Invalid timestamp
    http_response_code(403);
    echo json_encode([
        'status' => 'error',
        'message' => 'Invalid timestamp'
    ]);
}
?>

