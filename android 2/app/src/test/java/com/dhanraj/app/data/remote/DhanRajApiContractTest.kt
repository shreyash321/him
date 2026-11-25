package com.dhanraj.app.data.remote

import com.dhanraj.app.data.UserProfile
import kotlinx.coroutines.runBlocking
import okhttp3.OkHttpClient
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.Assert.assertEquals
import org.junit.Test
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class DhanRajApiContractTest {
    @Test
    fun mapsTheExistingMeEndpointAndSnakeCaseFields() = runBlocking {
        val server = MockWebServer()
        server.enqueue(
            MockResponse().setBody(
                """{"username":"player_1","phone":"+918600110099","role":"user","coin_balance":250,"must_change_password":false}""",
            ),
        )
        server.start()
        try {
            val api = Retrofit.Builder()
                .baseUrl(server.url("/"))
                .client(OkHttpClient())
                .addConverterFactory(GsonConverterFactory.create())
                .build()
                .create(DhanRajApi::class.java)

            val profile: UserProfile = api.me()
            val request = server.takeRequest()
            assertEquals("/auth/me", request.path)
            assertEquals("player_1", profile.username)
            assertEquals(250L, profile.coin_balance)
            assertEquals("+918600110099", profile.phone)
        } finally {
            server.shutdown()
        }
    }
}