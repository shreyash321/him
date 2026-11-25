package com.dhanraj.app.data.remote

import android.content.Context
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import com.google.gson.Gson
import okhttp3.Cookie
import okhttp3.CookieJar
import okhttp3.HttpUrl
import java.net.URLDecoder
import java.nio.charset.StandardCharsets

class SecureCookieJar(context: Context) : CookieJar {
    private val gson = Gson()
    private val preferences by lazy {
        val masterKey = MasterKey.Builder(context.applicationContext)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
        EncryptedSharedPreferences.create(
            context.applicationContext,
            "secure_http_cookies",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM,
        )
    }

    @Synchronized
    override fun saveFromResponse(url: HttpUrl, cookies: List<Cookie>) {
        val editor = preferences.edit()
        cookies.forEach { cookie ->
            val key = cookieKey(cookie)
            if (cookie.expiresAt <= System.currentTimeMillis()) editor.remove(key)
            else editor.putString(key, gson.toJson(StoredCookie.from(cookie)))
        }
        editor.apply()
    }

    @Synchronized
    override fun loadForRequest(url: HttpUrl): List<Cookie> {
        val now = System.currentTimeMillis()
        val valid = mutableListOf<Cookie>()
        val editor = preferences.edit()
        var hasExpired = false

        preferences.all.forEach { (key, value) ->
            val serialized = value as? String ?: return@forEach
            val stored = runCatching { gson.fromJson(serialized, StoredCookie::class.java) }.getOrNull()
            if (stored == null || stored.expiresAt <= now) {
                editor.remove(key)
                hasExpired = true
                return@forEach
            }
            val cookie = stored.toCookie() ?: return@forEach
            if (cookie.matches(url)) valid.add(cookie)
        }

        if (hasExpired) editor.apply()
        return valid
    }

    @Synchronized
    fun getCsrfToken(): String? {
        preferences.all.forEach { (key, value) ->
            if (key.endsWith("|site_csrf")) {
                val serialized = value as? String ?: return@forEach
                val stored = runCatching { gson.fromJson(serialized, StoredCookie::class.java) }.getOrNull()
                if (stored != null && stored.expiresAt > System.currentTimeMillis()) {
                    return try {
                        URLDecoder.decode(stored.value, StandardCharsets.UTF_8.name())
                    } catch (_: Exception) {
                        stored.value
                    }
                }
            }
        }
        return null
    }

    @Synchronized
    fun clear() = preferences.edit().clear().apply()

    private fun cookieKey(cookie: Cookie) = "${cookie.domain}|${cookie.path}|${cookie.name}"

    private data class StoredCookie(
        val name: String,
        val value: String,
        val expiresAt: Long,
        val domain: String,
        val path: String,
        val hostOnly: Boolean,
        val secure: Boolean,
        val httpOnly: Boolean,
    ) {
        fun toCookie(): Cookie? = runCatching {
            Cookie.Builder().name(name).value(value)
                .apply { if (hostOnly) hostOnlyDomain(domain) else domain(domain) }
                .path(path).expiresAt(expiresAt)
                .apply { if (secure) secure(); if (httpOnly) httpOnly() }
                .build()
        }.getOrNull()

        companion object {
            fun from(cookie: Cookie) = StoredCookie(
                cookie.name, cookie.value, cookie.expiresAt, cookie.domain, cookie.path,
                cookie.hostOnly, cookie.secure, cookie.httpOnly,
            )
        }
    }
}
