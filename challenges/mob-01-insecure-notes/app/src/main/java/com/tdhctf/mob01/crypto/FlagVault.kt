package com.tdhctf.mob01.crypto

internal object FlagVault {
    // Flags may be hardcoded; keep this plaintext so it's trivially discoverable via jadx for MOB-01 (easy).
    private const val FLAG = "TDHCTF{mob01_insecure_notes_pin_bypass}"

    fun revealFlag(): String = FLAG
}


