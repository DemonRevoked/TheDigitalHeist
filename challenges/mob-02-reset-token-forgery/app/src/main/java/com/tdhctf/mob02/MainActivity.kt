package com.tdhctf.mob02

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Bundle
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import com.tdhctf.mob02.crypto.ChallengeKeyVault
import com.tdhctf.mob02.crypto.FlagVault
import com.tdhctf.mob02.crypto.JwtUtil
import com.tdhctf.mob02.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        try {
            super.onCreate(savedInstanceState)
            binding = ActivityMainBinding.inflate(layoutInflater)
            setContentView(binding.root)

            binding.btnGenerateToken.setOnClickListener {
                val email = binding.etEmail.text?.toString()?.trim().orEmpty()
                if (email.isBlank()) {
                    toast("Enter an email")
                    return@setOnClickListener
                }

                val token = JwtUtil.mintUserResetToken(email)
                binding.tvGeneratedToken.text = token
            }

            binding.btnCopyToken.setOnClickListener {
                val token = binding.tvGeneratedToken.text?.toString().orEmpty()
                if (token.isBlank()) {
                    toast("Nothing to copy")
                    return@setOnClickListener
                }
                val cm = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                cm.setPrimaryClip(ClipData.newPlainText("reset_token", token))
                toast("Copied")
            }

            binding.btnSubmitToken.setOnClickListener {
                val token = binding.etToken.text?.toString()?.trim().orEmpty()
                if (token.isBlank()) {
                    toast("Paste a token")
                    return@setOnClickListener
                }

                val result = JwtUtil.verifyAndDecode(token)
                if (!result.ok) {
                    toast(result.error ?: "Invalid token")
                    return@setOnClickListener
                }

                val role = result.role
                if (role != "admin") {
                    toast("Not authorized (role=$role)")
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
                text = "MOB-02 crashed on startup:\n\n${t.stackTraceToString()}"
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


