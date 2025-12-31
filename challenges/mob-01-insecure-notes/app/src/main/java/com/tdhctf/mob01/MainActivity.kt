package com.tdhctf.mob01

import android.os.Bundle
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import com.tdhctf.mob01.crypto.AccessPhraseGate
import com.tdhctf.mob01.crypto.ChallengeKeyVault
import com.tdhctf.mob01.crypto.FlagVault
import com.tdhctf.mob01.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        try {
            super.onCreate(savedInstanceState)
            binding = ActivityMainBinding.inflate(layoutInflater)
            setContentView(binding.root)

            binding.btnSubmitToken.setOnClickListener {
                val token = binding.etToken.text?.toString()?.trim().orEmpty()
                if (token.isBlank()) {
                    toast("Enter access phrase")
                    return@setOnClickListener
                }

                // Easy path: hidden access phrase split across Manifest + strings.xml + assets/config.txt
                if (!AccessPhraseGate.isValid(this, token)) {
                    toast("Incorrect phrase")
                    return@setOnClickListener
                }

                val challengeKey = try {
                    ChallengeKeyVault.revealChallengeKey()
                } catch (_: Exception) {
                    toast("Key error")
                    return@setOnClickListener
                }

                val flag = try {
                    FlagVault.revealFlag()
                } catch (_: Exception) {
                    toast("Decryption error")
                    return@setOnClickListener
                }

                AlertDialog.Builder(this)
                    .setTitle("KEY + FLAG")
                    .setMessage("KEY:\n$challengeKey\n\nFLAG:\n$flag")
                    .setPositiveButton("OK", null)
                    .show()
            }
        } catch (t: Throwable) {
            // Avoid "opens then closes" with no context: show the crash reason on-screen.
            val tv = TextView(this).apply {
            text = "MOB-01 crashed on startup:\n\n${t.stackTraceToString()}"
                setPadding(32, 32, 32, 32)
                textSize = 12f
            }
            val sv = ScrollView(this).apply { addView(tv) }
            setContentView(sv)
        }
    }

    private fun toast(msg: String) {
        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show()
    }
}


