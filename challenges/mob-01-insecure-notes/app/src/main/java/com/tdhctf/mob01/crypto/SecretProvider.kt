package com.tdhctf.mob01.crypto

internal object SecretProvider {
    /**
     * Legacy: previously used to decrypt an encrypted flag blob.
     * MOB-01 now keeps the flag plaintext for easy jadx discovery.
     */
    fun appSecretString(): String {
        return "TDH_MOB01_INSECURE_NOTES_APP_SECRET"
    }

    fun appSecretBytes(): ByteArray = appSecretString().toByteArray(Charsets.UTF_8)
}


