#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <errno.h>

// Encrypted data - target=0, header=50, prompt=78, success=117, denied=144, key_prefix=162, flag_prefix=167, fallback_flag=173
static const uint8_t enc_data[] = {
    0x43,0x44,0x02,0x4C,0x40,0x15,0x52,0x92,0x94,0x98,0x8F,0x9D,0xB9,0xCF,0x9E,0xC8,
    0xCF,0xCF,0xB2,0xE0,0xCD,0x85,0xC8,0xC8,0xC1,0xDD,0x3B,0x38,0x23,0x41,0x0E,0x56,
    0x71,0x66,0x67,0x77,0x75,0x72,0x36,0x3C,0x2A,0x36,0x3D,0x3F,0x59,0x73,0x3E,0x7A,
    0x54,0x69,0x0D,0x0C,0x1F,0x03,0x77,0x5A,0x58,0x91,0x9D,0x8A,0x99,0x82,0xB3,0xD3,
    0x9E,0xFE,0xD0,0xD1,0xB2,0xE5,0x95,0x8B,0x96,0x87,0x95,0x94,0x67,0x51,0x67,0x59,
    0x43,0x57,0x14,0x5C,0x45,0xD7,0x8C,0x91,0x8F,0xCB,0xAC,0xDC,0xCD,0xCC,0xD0,0xC9,
    0xE0,0xF2,0xD7,0xC0,0x86,0xC8,0xCE,0x89,0x2E,0x33,0x29,0x0D,0x58,0x4E,0x65,0x7D,
    0x76,0x3C,0x1E,0x2B,0x36,0x7E,0x54,0x56,0x54,0x5B,0x47,0x5D,0xD7,0xBF,0x98,0x9E,
    0x8E,0xAB,0xDC,0xC7,0x9F,0xE9,0xC5,0xF7,0xFD,0xD0,0xCC,0xC0,0xCE,0xCD,0xCD,0x50,
    0x67,0x43,0x4D,0x4D,0x53,0x15,0x46,0x96,0x8B,0x8A,0x9A,0x83,0xAE,0xDC,0xCD,0xDA,
    0x81,0xAB,0x7B,0x54,0x5B,0x19,0x14,0x76,0x5D,0x43,0x44,0x0E,0x15,0x64,0x75,0x6A,
    0x60,0x60,0x73,0x4D,0x94,0x97,0x97,0x8C,0x8E,0xAF,0xCE,0xD7,0xD0,0xCE,0xFE,0xF5,
    0xF2,0xD0,0xC0,0xD1,0xC6,0xD1,0xF6,0x2A,0x33,0x3E,0x4C,0x5D,0x4A,0x6D,0x1B
};

// Obfuscated key derivation
static uint32_t derive_key(void) {
    uint32_t k = 0x12345678;
    k = (k << 13) | (k >> 19);
    k ^= 0x87654321;
    k = (k * 0x41C64E6D) + 0x3039;
    return k & 0xFFFFFFFF;
}

// Multi-stage decryption with obfuscation
static void decrypt_block(const uint8_t *src, size_t len, uint8_t *dst, uint32_t key) {
    for (size_t i = 0; i < len; i++) {
        uint8_t k1 = (key + i) & 0xFF;
        uint8_t k2 = ((key >> 8) + (i * 3)) & 0xFF;
        uint8_t k3 = ((key >> 16) ^ (i * 5)) & 0xFF;
        dst[i] = src[i] ^ k1 ^ k2 ^ k3 ^ 0x5A;
    }
}

// Reconstruct string at runtime
static void get_string(uint8_t *out, size_t offset, size_t len) {
    uint32_t key = derive_key();
    decrypt_block(enc_data + offset, len, out, key);
    out[len] = 0;
}

// Anti-debugging check
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

// Obfuscated helper - computes index transformations
static inline int compute_idx1(int i) { return i; }
static inline int compute_idx2(int i) { return 50 - i - 1; }
static inline int compute_idx3(int i) { return 49 - i; }

// Obfuscated transformation stage 1 - split into multiple operations
static void stage1_transform(const char *input, char *s1) {
    for (int i = 0; i < 25; i++) {
        int idx1 = compute_idx1(i);
        int idx2 = compute_idx2(i);
        int idx3 = compute_idx3(i);
        s1[idx1] = input[idx2];
        s1[idx3] = input[i];
        // Decoy: perform unused computation
        volatile int unused = (idx1 * idx2) ^ idx3;
        (void)unused;
    }
}

// Obfuscated swap with decoy operations and indirect control flow
static void stage2_swap(char *s1) {
    int j = 0;
    while (j < 50) {
        if (j + 1 < 50) {
            // Decoy computation
            volatile int dummy = (j * 7 + 13) % 256;
            (void)dummy;
            char temp = s1[j];
            s1[j] = s1[j + 1];
            s1[j + 1] = temp;
        }
        j += 2;
    }
}

// Obfuscated swap stage 2 with indirect indexing and decoys
static void stage3_swap(char *s1) {
    for (int k = 0; k < 48; k += 2) {
        if (k + 1 < 50) {
            // Multiple decoy operations
            volatile int d1 = k ^ 0xAA;
            volatile int d2 = (k << 1) | (k >> 7);
            volatile char d3 = (char)(d1 ^ d2);
            (void)d1; (void)d2; (void)d3;
            char temp = s1[k];
            s1[k] = s1[k + 1];
            s1[k + 1] = temp;
        }
    }
}

// Obfuscated length check with decoy
static int verify_length(const char *input) {
    if (!input) return 0;
    size_t len = strlen(input);
    // Decoy: unused computation
    volatile size_t dummy_len = len * 2 + 1;
    (void)dummy_len;
    return len == 50;
}

// Obfuscated comparison function
static int compare_strings(const char *s1, const char *s2, size_t len) {
    int diff = 0;
    for (size_t i = 0; i < len; i++) {
        diff |= (s1[i] ^ s2[i]);
        // Decoy: unused computation
        volatile int dummy = (int)(s1[i] + s2[i]);
        (void)dummy;
    }
    return diff == 0;
}

// Main check function - heavily obfuscated
static int check(const char *input) {
    if (!verify_length(input)) return 0;
    
    char s1[64] = {0};
    char s2[56] = {0};
    
    // Decrypt target string at runtime (50 characters)
    get_string((uint8_t*)s2, 0, 50);
    
    // Apply transformations with obfuscated control flow
    stage1_transform(input, s1);
    
    // Decoy operations to confuse analysis
    volatile int x = 0;
    for (int i = 0; i < 10; i++) {
        x += i * 2;
    }
    volatile char dummy_buf[16];
    for (int i = 0; i < 16; i++) {
        dummy_buf[i] = (char)(i ^ 0x42);
    }
    (void)x; (void)dummy_buf;
    
    stage2_swap(s1);
    
    // More decoy operations
    volatile uint32_t dummy_hash = 0;
    for (int i = 0; i < 50; i++) {
        dummy_hash = (dummy_hash << 1) ^ (uint32_t)s1[i];
    }
    (void)dummy_hash;
    
    stage3_swap(s1);
    
    // Obfuscated comparison
    return compare_strings(s1, s2, 50);
}

// HTTP client to request key and flag from localhost server
static int request_key_and_flag(const char *passphrase, char *key_buf, size_t key_size, char *flag_buf, size_t flag_size) {
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
    
    // Build JSON request
    char json_req[512];
    snprintf(json_req, sizeof(json_req), "{\"passphrase\":\"%s\"}", passphrase);
    
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
    // The flag value may contain special characters, so we need to find the actual closing quote
    // Look for the next unescaped quote after the flag value starts
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
            // Flag is empty string
            flag_buf[0] = '\0';
        }
    } else {
        // No closing quote found - try to find end of JSON object
        // Look for the closing brace after the flag value
        char *json_end = strrchr(json_body, '}');
        if (json_end && json_end > flag_start) {
            // The flag value ends just before the closing brace (or comma/whitespace before it)
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
    // (even if flag is empty, we still return success)
    return (key_start && flag_start) ? 1 : 0;
}

int main(void) {
    if (check_env()) {
        volatile int x = 0;
        while (x == 0) { usleep(1000); }
        return 1;
    }
    
    const char *ck = getenv("CHALLENGE_KEY");
    if (!ck || !*ck) {
        #ifndef CHALLENGE_KEY_BUILD
        #error "CHALLENGE_KEY_BUILD must be provided at build time (no default challenge key allowed)"
        #endif
        ck = CHALLENGE_KEY_BUILD;
    }
    
    // Decrypt and display header
    uint8_t header[35];
    get_string(header, 50, 28);
    fwrite(header, 1, 28, stdout);
    
    // Decrypt prompt
    uint8_t prompt[50];
    get_string(prompt, 78, 39);
    fwrite(prompt, 1, strlen((char*)prompt), stdout);
    fflush(stdout);
    
    char input[128];
    if (!fgets(input, sizeof(input), stdin)) {
        return 1;
    }
    
    input[strcspn(input, "\r\n")] = '\0';
    
    if (check(input)) {
        uint8_t success[30];
        get_string(success, 117, 27);
        fwrite(success, 1, 27, stdout);
        
        // Request key and flag from localhost server
        char key[256] = {0};
        char flag[256] = {0};
        
        if (request_key_and_flag(input, key, sizeof(key), flag, sizeof(flag))) {
            // Decrypt key prefix
            uint8_t key_prefix[10];
            get_string(key_prefix, 162, 5);
            fwrite(key_prefix, 1, 5, stdout);
            printf("%s\n", key);
            
            // Decrypt flag prefix
            uint8_t flag_prefix[10];
            get_string(flag_prefix, 167, 6);
            fwrite(flag_prefix, 1, 6, stdout);
            printf("%s\n", flag);
        } else {
            // Apache server not available (running outside container)
            printf("Server connection failed. Run inside container.\n");
            printf("Make sure Apache is running on localhost:31337\n");
        }
        return 0;
    }
    
    uint8_t denied[20];
    get_string(denied, 144, 18);
    fwrite(denied, 1, 18, stdout);
    return 1;
}
