package com.tdhctf.mob02.crypto

import org.json.JSONObject
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec

internal object JwtUtil {
    private const val ALG = "HS256"

    data class VerifyResult(
        val ok: Boolean,
        val error: String? = null,
        val email: String? = null,
        val role: String? = null,
    )

    fun mintUserResetToken(email: String): String {
        val nowSec = System.currentTimeMillis() / 1000L
        val expSec = nowSec + (15 * 60) // 15 minutes

        val header = JSONObject()
            .put("alg", ALG)
            .put("typ", "JWT")

        val payload = JSONObject()
            .put("email", email)
            .put("role", "user")
            .put("iat", nowSec)
            .put("exp", expSec)

        val headerB64 = B64Url.encode(header.toString().toByteArray(StandardCharsets.UTF_8))
        val payloadB64 = B64Url.encode(payload.toString().toByteArray(StandardCharsets.UTF_8))
        val signingInput = "$headerB64.$payloadB64"
        val sigB64 = sign(signingInput)

        return "$signingInput.$sigB64"
    }

    fun verifyAndDecode(jwt: String): VerifyResult {
        val parts = jwt.split(".")
        if (parts.size != 3) return VerifyResult(false, "Malformed token")

        val headerB64 = parts[0]
        val payloadB64 = parts[1]
        val sigB64 = parts[2]

        val headerJson = try {
            JSONObject(String(B64Url.decode(headerB64), StandardCharsets.UTF_8))
        } catch (_: Exception) {
            return VerifyResult(false, "Bad header")
        }

        val alg = headerJson.optString("alg", "")
        if (alg != ALG) return VerifyResult(false, "Unsupported alg")

        val signingInput = "$headerB64.$payloadB64"
        val expectedSig = sign(signingInput)

        // Constant-time compare (bytes) to avoid timing leaks.
        val okSig = try {
            MessageDigest.isEqual(B64Url.decode(sigB64), B64Url.decode(expectedSig))
        } catch (_: Exception) {
            false
        }
        if (!okSig) return VerifyResult(false, "Bad signature")

        val payloadJson = try {
            JSONObject(String(B64Url.decode(payloadB64), StandardCharsets.UTF_8))
        } catch (_: Exception) {
            return VerifyResult(false, "Bad payload")
        }

        val exp = payloadJson.optLong("exp", 0L)
        val nowSec = System.currentTimeMillis() / 1000L
        if (exp <= 0L || nowSec >= exp) return VerifyResult(false, "Token expired")

        val email = payloadJson.optString("email", "")
        val role = payloadJson.optString("role", "")
        if (email.isBlank() || role.isBlank()) {
            return VerifyResult(false, "Missing claims")
        }

        return VerifyResult(true, email = email, role = role)
    }

    private fun sign(signingInput: String): String {
        val mac = Mac.getInstance("HmacSHA256")
        val key = SecretKeySpec(SecretProvider.jwtSecretBytes(), "HmacSHA256")
        mac.init(key)
        val sig = mac.doFinal(signingInput.toByteArray(StandardCharsets.UTF_8))
        return B64Url.encode(sig)
    }
}


