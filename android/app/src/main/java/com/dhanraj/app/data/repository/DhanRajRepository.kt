package com.dhanraj.app.data.repository

import com.dhanraj.app.data.*
import com.dhanraj.app.data.remote.DhanRajApi
import com.google.gson.JsonParser
import retrofit2.HttpException
import java.io.IOException

class DhanRajRepository(private val api: DhanRajApi) {

    suspend fun login(req: LoginRequest) = api.login(req)
    suspend fun register(req: RegisterRequest) = api.register(req)
    suspend fun me() = api.getProfile()
    suspend fun logout() = api.logout()
    suspend fun changePassword(req: ChangePasswordRequest) = api.changePassword(req)

    // Upstream live results
    suspend fun marketResults() = api.getMarketResults()

    // KingStarline Games
    suspend fun markets() = api.getGameMarkets()
    suspend fun round(marketId: Int, date: String? = null) = api.getMarketToday(marketId, date)
    suspend fun betTypes(includeDisabled: Boolean = false) = api.getBetTypes(includeDisabled)
    suspend fun pannaSuggestions(type: String, prefix: String) = api.suggestPanna(type, prefix)
    suspend fun placeBet(req: BetRequest) = api.placeBet(req)
    suspend fun bets() = api.getBets()
    suspend fun results() = api.getResultsHistory()
    suspend fun verifyRng(roundId: Int) = api.verifyRng(roundId)
    suspend fun resultMode() = api.getResultMode()

    // Wallet
    suspend fun wallet() = api.getWalletHistory()
    suspend fun requestCredit(amount: Long) = api.requestCredit(CreditRequestPayload(amount))
    suspend fun requestWithdrawal(req: WithdrawalRequestPayload) = api.requestWithdrawal(req)

    // Admin
    suspend fun adminRequests(type: String? = null, search: String? = null) = api.getAdminRequests(type, search)
    suspend fun approveRequest(id: String) = api.approveRequest(id)
    suspend fun rejectRequest(id: String) = api.rejectRequest(id)
    suspend fun adminCredit(req: AdminCoinAdjustmentRequest) = api.adminCredit(req)
    suspend fun adminDebit(req: AdminCoinAdjustmentRequest) = api.adminDebit(req)
    suspend fun declareResult(roundId: Int, req: AdminDeclareResultRequest) = api.declareRoundResult(roundId, req)
    suspend fun createMarket(req: AdminMarketUpsertRequest) = api.createMarket(req)
    suspend fun updateMarket(id: Int, req: AdminMarketUpsertRequest) = api.updateMarket(id, req)
    suspend fun updateBetType(code: String, req: AdminBetTypeUpdateRequest) = api.updateBetType(code, req)

    companion object {
        fun message(error: Throwable): String = when (error) {
            is HttpException -> {
                val body = runCatching { error.response()?.errorBody()?.string() }.getOrNull()
                val detail = runCatching {
                    val json = JsonParser.parseString(body).asJsonObject.get("detail")
                    if (json.isJsonArray) json.asJsonArray.joinToString(" ") { it.asJsonObject.get("msg").asString }
                    else json.asString
                }.getOrNull()
                detail?.takeIf(String::isNotBlank) ?: when (error.code()) {
                    401 -> "Your session has expired. Please sign in again."
                    403 -> "This action is not available for your account."
                    409 -> "Conflict: Insufficient wallet balance."
                    429 -> "Too many requests. Please try again shortly."
                    else -> "The request could not be completed (${error.code()})."
                }
            }
            is IOException -> "Could not reach DhanRAJ. Check your connection and API URL."
            else -> error.message ?: "Something went wrong. Please try again."
        }
    }
}
