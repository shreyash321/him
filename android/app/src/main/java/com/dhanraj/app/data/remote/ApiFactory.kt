package com.dhanraj.app.data.remote

import android.content.Context
import com.dhanraj.app.BuildConfig
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

data class ApiClient(val api: DhanRajApi, val cookies: SecureCookieJar)

object ApiFactory {
    fun create(context: Context): ApiClient {
        val baseUrl = if (BuildConfig.DEBUG) BuildConfig.DEBUG_API_BASE_URL
        else BuildConfig.PRODUCTION_API_BASE_URL
        require(baseUrl.startsWith("https://") || (BuildConfig.DEBUG && baseUrl.startsWith("http://"))) {
            "Configure a reachable API URL. Production requires HTTPS."
        }
        val origin = java.net.URL(baseUrl).let { "${it.protocol}://${it.authority}" }
        val cookieJar = SecureCookieJar(context)
        val headers = Interceptor { chain ->
            val request = chain.request()
            val builder = request.newBuilder().header("Origin", origin)
            if (request.method != "GET") {
                cookieJar.loadForRequest(request.url).firstOrNull { it.name == "site_csrf" }
                    ?.let { builder.header("X-CSRF-Token", it.value) }
            }
            val response = chain.proceed(builder.build())
            if (response.code == 401 && !request.url.encodedPath.endsWith("/auth/login")) cookieJar.clear()
            response
        }
        val client = OkHttpClient.Builder()
            .cookieJar(cookieJar)
            .addInterceptor(headers)
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(20, TimeUnit.SECONDS)
            .writeTimeout(20, TimeUnit.SECONDS)
            .followRedirects(false)
            .build()
        val api = Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(DhanRajApi::class.java)
        return ApiClient(api, cookieJar)
    }
}