package com.tdhctf.mob02.crypto

internal object SecretProvider {
    /**
     * The embedded JWT secret. Players recover this to forge admin tokens.
     *
     * Organizer note: change this string (and then re-generate the flag blob).
     */
    fun jwtSecretString(): String {
        // Mild obfuscation (still recoverable by reversing).
        val a = "TDH"
        val b = "_MOB03_"
        val c = "RESET"
        val d = "_TOKEN_"
        val e = "SIGNING_"
        val f = "KEY_2025"
        return a + b + c + d + e + f
    }

    fun jwtSecretBytes(): ByteArray = jwtSecretString().toByteArray(Charsets.UTF_8)
}


