package com.tdhctf.mob02.crypto

import android.util.Base64

internal object B64Url {
    fun encode(data: ByteArray): String {
        // Base64 URL-safe, no padding, no wrap
        return Base64.encodeToString(data, Base64.URL_SAFE or Base64.NO_PADDING or Base64.NO_WRAP)
    }

    fun decode(str: String): ByteArray {
        // android.util.Base64 can decode URL_SAFE without padding
        return Base64.decode(str, Base64.URL_SAFE or Base64.NO_WRAP)
    }
}


