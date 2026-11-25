package com.dhanraj.app.data

import com.google.gson.annotations.SerializedName

// --- Auth Models ---
data class LoginRequest(
    val identifier: String,
    val password: String
)

data class RegisterRequest(
    val username: String,
    val phone: String,
    val password: String
)

data class ChangePasswordRequest(
    @SerializedName("current_password") val currentPassword: String,
    @SerializedName("new_password") val newPassword: String
)

data class AuthResponse(
    val authenticated: Boolean = true,
    val username: String,
    val role: String,
    @SerializedName("must_change_password") val mustChangePassword: Boolean = false,
    val detail: String? = null
)

data class RegisterResponse(
    val registered: Boolean,
    val username: String? = null,
    val message: String? = null,
    val detail: String? = null
)

data class UserProfile(
    val id: String = "",
    val username: String,
    val phone: String? = null,
    val role: String = "user",
    @SerializedName("coin_balance") val coinBalance: Long = 0,
    @SerializedName("must_change_password") val mustChangePassword: Boolean = false,
    @SerializedName("account_holder_name") val accountHolderName: String? = null,
    @SerializedName("bank_account_number") val bankAccountNumber: String? = null,
    @SerializedName("ifsc_code") val ifscCode: String? = null
)

data class GenericMessageResponse(
    val message: String? = null,
    val detail: String? = null
)

// --- Upstream Live Market Results (/front/fetch_updated_results) ---
data class MarketResultItem(
    val id: String,
    @SerializedName("market_name") val marketName: String? = null,
    @SerializedName("open_time") val openTime: String? = null,
    @SerializedName("close_time") val closeTime: String? = null,
    @SerializedName("open_digit") val openDigit: String? = null,
    @SerializedName("open_result") val openResult: String? = null,
    @SerializedName("close_result") val closeResult: String? = null,
    @SerializedName("close_digit") val closeDigit: String? = null,
    @SerializedName("open_stat") val openStat: String? = null,
    @SerializedName("close_stat") val closeStat: String? = null
) {
    fun getFormattedOpenPanel(): String {
        return if (openStat == "1" && !openDigit.isNullOrBlank()) {
            if (openDigit == "0") "000" else openDigit
        } else {
            "***"
        }
    }

    fun getFormattedOpenResult(): String {
        return if (openStat == "1" && !openResult.isNullOrBlank()) openResult else "*"
    }

    fun getFormattedCloseResult(): String {
        return if (closeStat == "1" && !closeResult.isNullOrBlank()) closeResult else "*"
    }

    fun getFormattedClosePanel(): String {
        return if (closeStat == "1" && !closeDigit.isNullOrBlank()) {
            if (closeDigit == "0") "000" else closeDigit
        } else {
            "***"
        }
    }

    fun getDisplayResult(): String {
        val op = getFormattedOpenPanel()
        val ores = getFormattedOpenResult()
        val cres = getFormattedCloseResult()
        val cp = getFormattedClosePanel()
        return "$op-$ores$cres-$cp"
    }
}

// --- KingStarline Games Models ---
data class GameMarket(
    val id: Int,
    val name: String,
    @SerializedName("open_time") val openTime: String,
    @SerializedName("close_time") val closeTime: String,
    @SerializedName("open_time_24") val openTime24: String? = null,
    @SerializedName("close_time_24") val closeTime24: String? = null,
    val status: String, // RUNNING, CLOSED
    @SerializedName("betting_session") val bettingSession: String? = null,
    @SerializedName("next_cutoff") val nextCutoff: String? = null,
    @SerializedName("latest_result") val latestResult: String? = null,
    val paused: Boolean = false,
    @SerializedName("sort_order") val sortOrder: Int = 0,
    @SerializedName("active_days") val activeDays: String? = null,
    @SerializedName("bet_cutoff_minutes") val betCutoffMinutes: Int = 10
)

data class GameRound(
    @SerializedName("round_id") val roundId: Int,
    @SerializedName("market_id") val marketId: Int = 0,
    val date: String = "",
    val status: String = "",
    @SerializedName("open_betting") val openBetting: Boolean = false,
    @SerializedName("close_betting") val closeBetting: Boolean = false,
    @SerializedName("jodi_betting") val jodiBetting: Boolean = false,
    @SerializedName("open_cutoff") val openCutoff: String? = null,
    @SerializedName("close_cutoff") val closeCutoff: String? = null,
    @SerializedName("open_panna") val openPanna: String? = null,
    @SerializedName("open_single") val openSingle: String? = null,
    @SerializedName("close_panna") val closePanna: String? = null,
    @SerializedName("close_single") val closeSingle: String? = null
)

data class BetType(
    val code: String,
    val label: String,
    @SerializedName("win_per_10") val winPer10: Long,
    @SerializedName("min_points") val minPoints: Long = 10,
    @SerializedName("max_points") val maxPoints: Long = 100000,
    val enabled: Boolean = true
)

data class PannaSuggestionResponse(
    val suggestions: List<String> = emptyList()
)

data class BetRequest(
    @SerializedName("round_id") val roundId: Int,
    @SerializedName("bet_type") val betType: String,
    val session: String, // "open", "close", "both"
    val selection: String,
    val points: Long,
    @SerializedName("idempotency_key") val idempotencyKey: String
)

data class BetResponse(
    val id: String = "",
    @SerializedName("coin_balance") val coinBalance: Long = 0,
    val message: String? = null
)

data class BetHistoryResponse(
    val items: List<BetHistoryItem> = emptyList()
)

data class BetHistoryItem(
    val id: String,
    val market: String,
    val game: String,
    val selection: String,
    val points: Long,
    val date: String,
    val session: String,
    val status: String,
    @SerializedName("created_at") val createdAt: String? = null
)

data class GameResultHistoryItem(
    @SerializedName("round_id") val roundId: Int,
    val market: String,
    val date: String,
    @SerializedName("open_panna") val openPanna: String? = null,
    val jodi: String? = null,
    @SerializedName("close_panna") val closePanna: String? = null
)

data class RngVerificationResponse(
    @SerializedName("round_id") val roundId: Int,
    val date: String = "",
    val seed: String? = null,
    val hash: String? = null,
    val verified: Boolean = true
)

data class ResultModeResponse(
    val mode: String
)

// --- Wallet & Requests Models ---
data class WalletHistory(
    val username: String,
    val phone: String? = null,
    @SerializedName("coin_balance") val coinBalance: Long = 0,
    val transactions: List<CoinTransactionItem> = emptyList(),
    @SerializedName("coins_are_redeemable") val coinsAreRedeemable: Boolean = false
)

data class CoinTransactionItem(
    val kind: String,
    @SerializedName("amount_delta") val amountDelta: Long,
    @SerializedName("balance_after") val balanceAfter: Long,
    val description: String,
    val market: String? = null,
    val selection: String? = null,
    @SerializedName("created_at") val createdAt: String
)

data class CreditRequestPayload(
    val amount: Long
)

data class WithdrawalRequestPayload(
    val amount: Long,
    @SerializedName("account_holder_name") val accountHolderName: String,
    @SerializedName("bank_account_number") val bankAccountNumber: String,
    @SerializedName("ifsc_code") val ifscCode: String
)

data class UserRequestItem(
    val id: String,
    val type: String, // "credit" or "withdrawal"
    @SerializedName("user_id") val userId: String = "",
    @SerializedName("user_name") val userName: String = "",
    val amount: Long,
    @SerializedName("requested_amount") val requestedAmount: Long? = null,
    @SerializedName("current_wallet_balance") val currentWalletBalance: Long = 0,
    val status: String = "PENDING", // "PENDING", "APPROVED", "REJECTED"
    @SerializedName("account_holder_name") val accountHolderName: String? = null,
    @SerializedName("bank_account_number") val bankAccountNumber: String? = null,
    @SerializedName("ifsc_code") val ifscCode: String? = null,
    val timestamp: String? = null,
    @SerializedName("created_at") val createdAt: String? = null
)

data class AdminRequestsResponse(
    val items: List<UserRequestItem> = emptyList()
)

data class AdminCoinAdjustmentRequest(
    val username: String,
    val phone: String,
    val amount: Long
)

data class AdminCoinAdjustmentResponse(
    val username: String,
    @SerializedName("amount_added") val amountAdded: Long? = null,
    @SerializedName("amount_removed") val amountRemoved: Long? = null,
    @SerializedName("coin_balance") val coinBalance: Long
)

// --- Admin Controls ---
data class AdminDeclareResultRequest(
    val session: String,
    val panna: String
)

data class AdminDeclareResultResponse(
    val message: String? = null,
    val settled: Int = 0
)

data class AdminMarketUpsertRequest(
    val name: String,
    @SerializedName("open_time") val openTime: String,
    @SerializedName("close_time") val closeTime: String,
    @SerializedName("active_days") val activeDays: List<Int>,
    @SerializedName("bet_cutoff_minutes") val betCutoffMinutes: Int,
    val paused: Boolean,
    @SerializedName("sort_order") val sortOrder: Int
)

data class AdminBetTypeUpdateRequest(
    @SerializedName("win_per_10") val winPer10: Long,
    @SerializedName("min_points") val minPoints: Long,
    @SerializedName("max_points") val maxPoints: Long,
    val enabled: Boolean
)
