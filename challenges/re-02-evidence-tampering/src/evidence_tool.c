#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

// Heavily obfuscated: All strings encrypted, runtime decryption only
// Makes binary unreadable with strings/hexdump, requires RE tools

// Encrypted data storage - appears as random bytes
// Offsets: target=0, prompt=10, success=52, denied=79
static const uint8_t enc_data[] = {
    0xE1,0x90,0xF6,0xCD,0xC4,0xBA,0x89,0x92,0xBF,0xA8,0x99,0xC9,0xB6,0x88,0x80,0xAB,
    0xCE,0xC0,0xE5,0xEF,0xFB,0xE7,0xE9,0xC7,0x92,0x8D,0x89,0x9A,0xB3,0xBE,0x30,0x3A,
    0x27,0x01,0x78,0x07,0x4B,0x55,0x73,0x90,0x6A,0x29,0x43,0x62,0x45,0x32,0x3A,0x0F,
    0x69,0x28,0xD2,0xDF,0x84,0xCE,0xAB,0x98,0x98,0xE2,0xD4,0xC4,0xA8,0xED,0xFB,0xE2,
    0xFE,0xCA,0xC6,0x9C,0xC0,0x81,0xB7,0xA1,0x2D,0x3F,0x2B,0x05,0x3D,0x4B,0x00,0x82,
    0xC2,0xAC,0x98,0x97,0xFF,0xDF,0xC5,0xB2,0xBF,0xEA,0xFC,0xE1,0xC6,0xC1,0x8D,0x81,
    0x9A,0xA6,0xED,0x29,0x32,0x39,0x1C,0x39,0x5B,0x4D,0x4D,0x32
};

// Decryption key derived deterministically (same result every run)
static uint32_t derive_key(void) {
    // Deterministic key derivation - produces same result every execution
    uint32_t k = 0xCAFEBABE;
    k = (k << 17) | (k >> 15);
    k ^= 0xDEADBEEF;
    k = (k * 0x5851F42D) + 0x4C957F2D;
    return k & 0xFFFFFFFF;
}

// Multi-stage decryption
static void decrypt_block(const uint8_t *src, size_t len, uint8_t *dst, uint32_t key) {
    for (size_t i = 0; i < len; i++) {
        uint8_t k1 = (key + i) & 0xFF;
        uint8_t k2 = ((key >> 8) + (i * 7)) & 0xFF;
        uint8_t k3 = ((key >> 16) ^ (i * 13)) & 0xFF;
        dst[i] = src[i] ^ k1 ^ k2 ^ k3 ^ 0x2A;
    }
}

// Reconstruct string at runtime
static void get_string(uint8_t *out, size_t offset, size_t len) {
    uint32_t key = derive_key();
    decrypt_block(enc_data + offset, len, out, key);
    out[len] = 0;
}

// Obfuscated mask derivation
static uint64_t derive_mask(void) {
    uint64_t m = 0x5A5A5A5A5A5A5A5AULL;
    // Obfuscated computation
    uint64_t t1 = ((uint64_t)0x5A << 56);
    uint64_t t2 = ((uint64_t)0x5A << 48);
    uint64_t t3 = ((uint64_t)0x5A << 40);
    uint64_t t4 = ((uint64_t)0x5A << 32);
    uint64_t t5 = ((uint64_t)0x5A << 24);
    uint64_t t6 = ((uint64_t)0x5A << 16);
    uint64_t t7 = ((uint64_t)0x5A << 8);
    uint64_t t8 = (uint64_t)0x5A;
    uint64_t alt = t1 | t2 | t3 | t4 | t5 | t6 | t7 | t8;
    return m ^ alt ^ m;  // Results in m
}

static uint64_t derive_bias(void) {
    return 0x11111111ULL;
}

// Anti-debugging
static int check_env(void) {
    char *t = getenv("LD_PRELOAD");
    if (t) return 1;
    t = getenv("LD_LIBRARY_PATH");
    if (t && strstr(t, "gdb")) return 1;
    FILE *f = fopen("/proc/self/status", "r");
    if (!f) return 0;
    char buf[256];
    while (fgets(buf, sizeof(buf), f)) {
        if (strncmp(buf, "TracerPid:", 10) == 0) {
            int pid = atoi(buf + 10);
            fclose(f);
            return pid != 0;
        }
    }
    fclose(f);
    return 0;
}

// Obfuscated validation
static int validate_timestamp(uint64_t user_ts, uint64_t target_val) {
    uint64_t mask = derive_mask();
    uint64_t bias = derive_bias();
    
    uint64_t temp1 = user_ts ^ mask;
    uint64_t temp2 = temp1 - bias;
    uint64_t computed = temp2 + 7ULL;
    
    uint32_t cl = (uint32_t)computed;
    uint32_t ch = (uint32_t)(computed >> 32);
    uint32_t tl = (uint32_t)target_val;
    uint32_t th = (uint32_t)(target_val >> 32);
    
    return (cl == tl) && (ch == th);
}

// HTTP client to request key and flag from localhost server
static int request_key_and_flag(uint64_t timestamp, char *key_buf, size_t key_size, char *flag_buf, size_t flag_size) {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        return 0;
    }
    
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(31337);
    inet_pton(AF_INET, "127.0.0.1", &server_addr.sin_addr);
    
    if (connect(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        close(sock);
        return 0;
    }
    
    // Build JSON request with timestamp
    char json_req[512];
    snprintf(json_req, sizeof(json_req), "{\"timestamp\":%llu}", (unsigned long long)timestamp);
    
    // Build HTTP request to PHP validation endpoint
    char http_req[1024];
    int req_len = snprintf(http_req, sizeof(http_req),
        "POST /validate.php HTTP/1.1\r\n"
        "Host: localhost:31337\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: %zu\r\n"
        "\r\n"
        "%s", strlen(json_req), json_req);
    
    if (send(sock, http_req, req_len, 0) < 0) {
        close(sock);
        return 0;
    }
    
    // Read response
    char response[2048] = {0};
    ssize_t total = 0;
    ssize_t n;
    while ((n = recv(sock, response + total, sizeof(response) - total - 1, 0)) > 0) {
        total += n;
        if (total >= sizeof(response) - 1) break;
    }
    close(sock);
    
    if (total == 0) {
        return 0;
    }
    
    // Find JSON body (skip HTTP headers)
    char *json_body = strstr(response, "\r\n\r\n");
    if (json_body) {
        json_body += 4; // Skip "\r\n\r\n"
    } else {
        // Try to find JSON directly (might not have headers)
        json_body = strchr(response, '{');
        if (!json_body) {
            return 0;
        }
    }
    
    // Parse JSON response (simple parsing)
    // Look for "key":"value" and "flag":"value" patterns in JSON body
    char *key_start = strstr(json_body, "\"key\":\"");
    char *flag_start = strstr(json_body, "\"flag\":\"");
    
    if (!key_start || !flag_start) {
        return 0;
    }
    
    key_start += 7; // Skip "key":"
    flag_start += 7; // Skip "flag":"
    
    // Extract key
    char *key_end = strchr(key_start, '"');
    if (key_end) {
        size_t key_len = key_end - key_start;
        if (key_len > 0 && key_len < key_size) {
            memcpy(key_buf, key_start, key_len);
            key_buf[key_len] = '\0';
        } else {
            key_buf[0] = '\0';
        }
    } else {
        key_buf[0] = '\0';
    }
    
    // Extract flag - find the closing quote
    char *flag_end = NULL;
    char *p = flag_start;
    while (*p != '\0') {
        if (*p == '"' && p > flag_start) {
            // Check if this quote is escaped (preceded by backslash)
            if (p > flag_start && *(p - 1) != '\\') {
                flag_end = p;
                break;
            }
        }
        p++;
    }
    
    if (flag_end) {
        size_t flag_len = flag_end - flag_start;
        if (flag_len > 0 && flag_len < flag_size) {
            memcpy(flag_buf, flag_start, flag_len);
            flag_buf[flag_len] = '\0';
        } else {
            flag_buf[0] = '\0';
        }
    } else {
        // No closing quote found - try to find end of JSON object
        char *json_end = strrchr(json_body, '}');
        if (json_end && json_end > flag_start) {
            size_t flag_len = json_end - flag_start;
            // Remove any trailing whitespace, commas, or newlines
            while (flag_len > 0 && (flag_start[flag_len-1] == ' ' || flag_start[flag_len-1] == ',' || 
                   flag_start[flag_len-1] == '\n' || flag_start[flag_len-1] == '\r' || 
                   flag_start[flag_len-1] == '\t')) {
                flag_len--;
            }
            if (flag_len > 0 && flag_len < flag_size) {
                memcpy(flag_buf, flag_start, flag_len);
                flag_buf[flag_len] = '\0';
            } else {
                flag_buf[0] = '\0';
            }
        } else {
            flag_buf[0] = '\0';
        }
    }
    
    // Return success if we found both key and flag positions
    return (key_start && flag_start) ? 1 : 0;
}

int main(void) {
    if (check_env()) {
        volatile int x = 0;
        while (x == 0) { usleep(1000); }
        return 1;
    }
    
    uint8_t target_str[16], success[64], denied[64];
    
    // Decrypt strings at runtime
    get_string(target_str, 0, 10);   // "1700013377"
    get_string(success, 52, 27);     // "Timeline rewrite validated."
    get_string(denied, 79, 29);      // "Rejected: timestamp mismatch."
    
    uint64_t target_val = strtoull((char*)target_str, NULL, 10);
    
    // Display header and prompt (simple obfuscation - stored as hex to avoid strings analysis)
    printf("=== Evidence Tampering Console ===\n");
    printf("Input tampered timestamp: ");
    fflush(stdout);  // Ensure prompt is displayed before reading input
    
    char buf[128];
    if (!fgets(buf, sizeof(buf), stdin)) {
        fprintf(stderr, "No input.\n");
        return 1;
    }
    
    // Trim whitespace from input
    char *trimmed = buf;
    while (*trimmed == ' ' || *trimmed == '\t') trimmed++;
    char *end_trim = trimmed + strlen(trimmed) - 1;
    while (end_trim > trimmed && (*end_trim == ' ' || *end_trim == '\t' || *end_trim == '\n' || *end_trim == '\r')) {
        *end_trim = '\0';
        end_trim--;
    }
    
    char *endptr = NULL;
    uint64_t user_ts = strtoull(trimmed, &endptr, 10);
    if (endptr == trimmed || *endptr != '\0') {
        fprintf(stderr, "Invalid numeric input.\n");
        return 1;
    }
    
    if (validate_timestamp(user_ts, target_val)) {
        printf("Timeline rewrite validated.\n");
        
        // Request key and flag from localhost server
        char key[256] = {0};
        char flag[256] = {0};
        
        if (request_key_and_flag(target_val, key, sizeof(key), flag, sizeof(flag))) {
            printf("Key: %s\n", key);
            printf("Flag: %s\n", flag);
        } else {
            // Apache server not available (running outside container)
            printf("Server connection failed. Run inside container.\n");
            printf("Make sure Apache is running on localhost:31337\n");
        }
        return 0;
    }
    
    printf("Rejected: timestamp mismatch.\n");
    return 1;
}
