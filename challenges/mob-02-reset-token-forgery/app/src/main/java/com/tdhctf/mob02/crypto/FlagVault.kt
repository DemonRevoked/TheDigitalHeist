package com.tdhctf.mob02.crypto

internal object FlagVault {
    // Flags may be hardcoded; keep this plaintext so it's discoverable via jadx after extracting the JWT secret.
    private const val FLAG = "TDHCTF{offline_reset_token_forgery}"

    fun revealFlag(): String = FLAG
}


