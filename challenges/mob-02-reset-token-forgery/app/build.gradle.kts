plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

import java.io.File

android {
    namespace = "com.tdhctf.mob02"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.tdhctf.mob02"
        minSdk = 24
        targetSdk = 35
        versionCode = 1
        versionName = "1.0"

        // Injected at build time (NOT committed). This is the challenge KEY output.
        // Provide via:
        //   -Pmob02ChallengeKey=...    OR
        //   -Pmob02ChallengeKeyFile=/abs/path/to/keys/mob-02.key
        val injectedKey = resolveMob02ChallengeKey(providers)
        buildConfigField("String", "MOB02_CHALLENGE_KEY", "\"${escapeForJava(injectedKey)}\"")
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        viewBinding = true
        buildConfig = true
    }
}

fun resolveMob02ChallengeKey(providers: ProviderFactory): String {
    val direct = providers.gradleProperty("mob02ChallengeKey").orNull
    if (!direct.isNullOrBlank()) return direct.trim()

    val file = providers.gradleProperty("mob02ChallengeKeyFile").orNull
    if (!file.isNullOrBlank()) {
        val f = File(file)
        if (!f.exists()) throw GradleException("mob02ChallengeKeyFile not found: $file")
        return f.readText().trim()
    }

    // Keep IDE sync usable; the build/publish script enforces a real key.
    return "MOB02_KEY_NOT_SET"
}

fun escapeForJava(s: String): String =
    s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "").replace("\r", "")

dependencies {
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("com.google.android.material:material:1.12.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
}


