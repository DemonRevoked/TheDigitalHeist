package com.tdhctf.mob02.crypto

import android.util.Base64
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import javax.crypto.Cipher
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.SecretKeySpec

internal object FlagVault {
    /**
     * base64( nonce_12_bytes || ciphertext_and_tag )
     *
     * Organizer: regenerate using tools/generate_flag_blob.py after changing the secret or flag.
     */
    private const val FLAG_BLOB_B64 =
        "M1wti2J0Lm7A4OfuYhUGAPIeOpXDGbXWPQKEoWF7Q9GI4QMreQu9tQVr53Gu46wsHiQhcGWyiEXR2At0ckjr"

    fun revealFlag(): String {
        val blob = Base64.decode(FLAG_BLOB_B64, Base64.DEFAULT)
        require(blob.size > 12 + 16) { "Blob too small" }

        val nonce = blob.copyOfRange(0, 12)
        val ciphertextAndTag = blob.copyOfRange(12, blob.size)

        val keyBytes = deriveAes128KeyFromSecret(SecretProvider.jwtSecretBytes())
        val key = SecretKeySpec(keyBytes, "AES")

        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.DECRYPT_MODE, key, GCMParameterSpec(128, nonce))

        val pt = cipher.doFinal(ciphertextAndTag)
        return String(pt, StandardCharsets.UTF_8)
    }

    private fun deriveAes128KeyFromSecret(secret: ByteArray): ByteArray {
        val digest = MessageDigest.getInstance("SHA-256").digest(secret)
        return digest.copyOfRange(0, 16)
    }
}


