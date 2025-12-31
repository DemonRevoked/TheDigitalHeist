package com.tdhctf.mob01.crypto

import android.content.Context
import android.content.pm.PackageManager
import com.tdhctf.mob01.R

/**
 * MOB-01 (easy): offline access phrase gate.
 *
 * Student objective: find the hidden phrase and enter it.
 */
internal object AccessPhraseGate {
    fun isValid(context: Context, input: String): Boolean =
        input.trim() == requiredPhrase(context)

    /**
     * Required phrase is split across:
     * - AndroidManifest.xml (meta-data)
     * - res/values/strings.xml
     * - assets/config.txt
     */
    private fun requiredPhrase(context: Context): String {
        val pm = context.packageManager
        val appInfo = pm.getApplicationInfo(context.packageName, PackageManager.GET_META_DATA)
        val fromManifest =
            appInfo.metaData?.getString("mob01_phrase_part_manifest").orEmpty()

        val fromStrings = context.getString(R.string.mob01_phrase_part_strings)

        val fromAssets = context.assets.open("config.txt").bufferedReader().use { it.readText() }
            .trim()

        // Expect config.txt to contain "7429-PROFESSOR"
        return fromManifest + fromStrings + fromAssets
    }
}


