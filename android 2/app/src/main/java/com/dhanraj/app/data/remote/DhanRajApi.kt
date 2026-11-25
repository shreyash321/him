package com.dhanraj.app.data.remote

import com.dhanraj.app.data.*
import retrofit2.http.*

interface DhanRajApi {

    // --- Authentication ---
    @POST("auth/login")
    suspend fun login(@Body body: LoginRequest): AuthResponse

    @POST("auth/register")
    suspend fun register(@Body body: RegisterRequest): RegisterResponse

    @POST("auth/change-password")
    suspend fun changePassword(@Body body: ChangePasswordRequest): GenericMessageResponse

    @GET("auth/me")
    suspend fun getProfile(): UserProfile

    @POST("auth/logout")
    suspend fun logout(): GenericMessageResponse

    // --- Upstream Live Market Results ---
    @GET("front/fetch_updated_results")
    @Headers("X-Requested-With: XMLHttpRequest")
    suspend fun getMarketResults(): List<MarketResultItem>

    // --- KingStarline Games ---
    @GET("api/markets")
    suspend fun getGameMarkets(): List<GameMarket>

    @GET("api/markets/{id}/today")
    suspend fun getMarketToday(
        @Path("id") marketId: Int,
        @Query("round_date") roundDate: String? = null
    ): GameRound

    @GET("api/bet-types")
    suspend fun getBetTypes(
        @Query("include_disabled") includeDisabled: Boolean = false
    ): List<BetType>

    @GET("api/panna/suggest")
    suspend fun suggestPanna(
        @Query("type") type: String,
        @Query("prefix") prefix: String
    ): PannaSuggestionResponse

    @POST("api/bets")
    suspend fun placeBet(@Body body: BetRequest): BetResponse

    @GET("api/bets")
    suspend fun getBets(): BetHistoryResponse

    @GET("api/results/history")
    suspend fun getResultsHistory(): List<GameResultHistoryItem>

    @GET("api/verify/{round_id}")
    suspend fun verifyRng(@Path("round_id") roundId: Int): RngVerificationResponse

    @GET("api/result-mode")
    suspend fun getResultMode(): ResultModeResponse

    // --- Wallet ---
    @GET("wallet/history")
    suspend fun getWalletHistory(): WalletHistory

    @POST("api/requests/credit")
    suspend fun requestCredit(@Body body: CreditRequestPayload): UserRequestItem

    @POST("api/requests/withdraw")
    suspend fun requestWithdrawal(@Body body: WithdrawalRequestPayload): UserRequestItem

    // --- Admin Operations ---
    @GET("api/admin/requests")
    suspend fun getAdminRequests(
        @Query("type") type: String? = null,
        @Query("search") search: String? = null
    ): AdminRequestsResponse

    @POST("api/admin/requests/{id}/approve")
    suspend fun approveRequest(@Path("id") requestId: String): UserRequestItem

    @POST("api/admin/requests/{id}/reject")
    suspend fun rejectRequest(@Path("id") requestId: String): UserRequestItem

    @POST("admin/credits")
    suspend fun adminCredit(@Body body: AdminCoinAdjustmentRequest): AdminCoinAdjustmentResponse

    @POST("admin/debits")
    suspend fun adminDebit(@Body body: AdminCoinAdjustmentRequest): AdminCoinAdjustmentResponse

    @POST("api/admin/rounds/{id}/result")
    suspend fun declareRoundResult(
        @Path("id") roundId: Int,
        @Body body: AdminDeclareResultRequest
    ): AdminDeclareResultResponse

    @POST("api/admin/markets")
    suspend fun createMarket(@Body body: AdminMarketUpsertRequest): GameMarket

    @PUT("api/admin/markets/{id}")
    suspend fun updateMarket(
        @Path("id") marketId: Int,
        @Body body: AdminMarketUpsertRequest
    ): GameMarket

    @PUT("api/admin/bet-types/{code}")
    suspend fun updateBetType(
        @Path("code") code: String,
        @Body body: AdminBetTypeUpdateRequest
    ): BetType
}
