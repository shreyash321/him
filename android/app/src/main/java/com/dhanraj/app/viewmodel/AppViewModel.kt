package com.dhanraj.app.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.dhanraj.app.data.*
import com.dhanraj.app.data.remote.SecureCookieJar
import com.dhanraj.app.data.repository.DhanRajRepository
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import java.util.UUID

data class AppState(
    val initializing: Boolean = true,
    val busy: Boolean = false,
    val user: UserProfile? = null,
    val wallet: WalletHistory? = null,
    val marketResults: List<MarketResultItem> = emptyList(),
    val resultsStatus: String = "Loading market results…",
    val markets: List<GameMarket> = emptyList(),
    val betTypes: List<BetType> = emptyList(),
    val pannaSuggestions: List<String> = emptyList(),
    val bets: List<BetHistoryItem> = emptyList(),
    val results: List<GameResultHistoryItem> = emptyList(),
    val selectedMarket: GameMarket? = null,
    val selectedRound: GameRound? = null,
    val adminRequests: List<UserRequestItem> = emptyList(),
    val error: String? = null,
    val notice: String? = null,
    val registerDialog: Pair<Boolean, String>? = null
)

class AppViewModel(
    private val repository: DhanRajRepository?,
    private val cookieJar: SecureCookieJar?,
) : ViewModel() {

    private val _state = MutableStateFlow(AppState())
    val state: StateFlow<AppState> = _state.asStateFlow()

    private var autoRefreshJob: Job? = null
    private var suggestionJob: Job? = null

    fun initialize() = viewModelScope.launch {
        val repo = repository ?: return@launch _state.update { it.copy(initializing = false) }
        try {
            val user = repo.me()
            _state.update { it.copy(user = user, initializing = false) }
        } catch (_: Exception) {
            _state.update { it.copy(user = null, initializing = false) }
        }
        refreshLiveMarkets()
        refreshGameMarkets()
        refreshBetTypes()
        startAutoRefresh()
    }

    private fun startAutoRefresh() {
        autoRefreshJob?.cancel()
        autoRefreshJob = viewModelScope.launch {
            while (isActive) {
                delay(60000)
                refreshLiveMarkets()
                if (_state.value.user != null) {
                    silentRefreshProfile()
                }
            }
        }
    }

    fun showNotice(msg: String) {
        _state.update { it.copy(notice = msg) }
    }

    fun clearNotice() {
        _state.update { it.copy(notice = null) }
    }

    fun clearError() {
        _state.update { it.copy(error = null) }
    }

    fun clearRegisterDialog() {
        _state.update { it.copy(registerDialog = null) }
    }

    private suspend fun silentRefreshProfile() {
        val repo = repository ?: return
        try {
            val user = repo.me()
            _state.update { it.copy(user = user) }
        } catch (_: Exception) {}
    }

    fun refreshLiveMarkets() = viewModelScope.launch {
        val repo = repository ?: return@launch
        try {
            val list = repo.marketResults()
            _state.update {
                it.copy(
                    marketResults = list,
                    resultsStatus = "Showing ${list.size} markets · Updated"
                )
            }
        } catch (_: Exception) {
            _state.update {
                it.copy(resultsStatus = "Market results are temporarily unavailable. Retrying…")
            }
        }
    }

    fun refreshGameMarkets() = viewModelScope.launch {
        val repo = repository ?: return@launch
        try {
            val list = repo.markets()
            _state.update { it.copy(markets = list) }
        } catch (_: Exception) {}
    }

    fun refreshBetTypes() = viewModelScope.launch {
        val repo = repository ?: return@launch
        try {
            val list = repo.betTypes()
            _state.update { it.copy(betTypes = list) }
        } catch (_: Exception) {}
    }

    fun selectMarket(market: GameMarket, onReady: () -> Unit) = viewModelScope.launch {
        val repo = repository ?: return@launch
        _state.update { it.copy(selectedMarket = market, busy = true) }
        try {
            val round = repo.round(market.id)
            _state.update { it.copy(selectedRound = round, busy = false) }
            onReady()
        } catch (e: Exception) {
            _state.update { it.copy(busy = false, notice = DhanRajRepository.message(e)) }
        }
    }

    fun refreshRound(date: String?) = viewModelScope.launch {
        val repo = repository ?: return@launch
        val market = _state.value.selectedMarket ?: return@launch
        try {
            val round = repo.round(market.id, date)
            _state.update { it.copy(selectedRound = round) }
        } catch (e: Exception) {
            _state.update { it.copy(notice = DhanRajRepository.message(e)) }
        }
    }

    fun suggestPanna(type: String, prefix: String) {
        suggestionJob?.cancel()
        if (prefix.isBlank()) {
            _state.update { it.copy(pannaSuggestions = emptyList()) }
            return
        }
        suggestionJob = viewModelScope.launch {
            val repo = repository ?: return@launch
            try {
                val res = repo.pannaSuggestions(type, prefix)
                _state.update { it.copy(pannaSuggestions = res.suggestions) }
            } catch (_: Exception) {
                _state.update { it.copy(pannaSuggestions = emptyList()) }
            }
        }
    }

    fun placeBet(
        betType: String,
        session: String,
        selection: String,
        points: Long,
        onSuccess: () -> Unit
    ) = viewModelScope.launch {
        val repo = repository ?: return@launch
        val round = _state.value.selectedRound ?: return@launch
        _state.update { it.copy(busy = true, error = null) }
        try {
            val req = BetRequest(
                roundId = round.roundId,
                betType = betType,
                session = session,
                selection = selection,
                points = points,
                idempotencyKey = UUID.randomUUID().toString()
            )
            val res = repo.placeBet(req)
            val currentBal = res.coinBalance
            _state.update {
                it.copy(
                    busy = false,
                    notice = "Virtual points entry recorded.",
                    user = it.user?.copy(coinBalance = currentBal)
                )
            }
            onSuccess()
        } catch (e: Exception) {
            val msg = DhanRajRepository.message(e)
            _state.update { it.copy(busy = false, error = msg, notice = msg) }
        }
    }

    fun refreshBets() = viewModelScope.launch {
        val repo = repository ?: return@launch
        try {
            val res = repo.bets()
            _state.update { it.copy(bets = res.items) }
        } catch (e: Exception) {
            _state.update { it.copy(notice = DhanRajRepository.message(e)) }
        }
    }

    fun refreshResults() = viewModelScope.launch {
        val repo = repository ?: return@launch
        try {
            val list = repo.results()
            _state.update { it.copy(results = list) }
        } catch (e: Exception) {
            _state.update { it.copy(notice = DhanRajRepository.message(e)) }
        }
    }

    fun refreshWallet() = viewModelScope.launch {
        val repo = repository ?: return@launch
        try {
            val hist = repo.wallet()
            _state.update {
                it.copy(
                    wallet = hist,
                    user = it.user?.copy(coinBalance = hist.coinBalance)
                )
            }
        } catch (e: Exception) {
            _state.update { it.copy(notice = DhanRajRepository.message(e)) }
        }
    }

    fun requestCredit(amount: Long, onSuccess: () -> Unit) = viewModelScope.launch {
        val repo = repository ?: return@launch
        _state.update { it.copy(busy = true, error = null) }
        try {
            repo.requestCredit(amount)
            refreshWallet()
            _state.update { it.copy(busy = false, notice = "Credit request submitted.") }
            onSuccess()
        } catch (e: Exception) {
            val msg = DhanRajRepository.message(e)
            _state.update { it.copy(busy = false, error = msg, notice = msg) }
        }
    }

    fun requestWithdrawal(
        amount: Long,
        name: String,
        account: String,
        ifsc: String,
        onSuccess: () -> Unit
    ) = viewModelScope.launch {
        val repo = repository ?: return@launch
        _state.update { it.copy(busy = true, error = null) }
        try {
            val payload = WithdrawalRequestPayload(
                amount = amount,
                accountHolderName = name,
                bankAccountNumber = account,
                ifscCode = ifsc
            )
            repo.requestWithdrawal(payload)
            refreshWallet()
            _state.update { it.copy(busy = false, notice = "Withdrawal request submitted.") }
            onSuccess()
        } catch (e: Exception) {
            val msg = DhanRajRepository.message(e)
            _state.update { it.copy(busy = false, error = msg, notice = msg) }
        }
    }

    fun login(identifier: String, pass: String, onSuccess: () -> Unit) = viewModelScope.launch {
        val repo = repository ?: return@launch
        _state.update { it.copy(busy = true, error = null) }
        try {
            val res = repo.login(LoginRequest(identifier, pass))
            val user = try { repo.me() } catch (_: Exception) {
                UserProfile(username = res.username, role = res.role, mustChangePassword = res.mustChangePassword)
            }
            _state.update { it.copy(user = user, busy = false) }
            onSuccess()
        } catch (e: Exception) {
            val msg = DhanRajRepository.message(e)
            _state.update { it.copy(busy = false, error = msg) }
        }
    }

    fun register(username: String, phone: String, pass: String, onSuccess: () -> Unit) = viewModelScope.launch {
        val repo = repository ?: return@launch
        _state.update { it.copy(busy = true, error = null) }
        try {
            val res = repo.register(RegisterRequest(username, phone, pass))
            val msg = res.message ?: "Registration successful."
            _state.update { it.copy(busy = false, registerDialog = Pair(true, msg)) }
            onSuccess()
        } catch (e: Exception) {
            val msg = DhanRajRepository.message(e)
            _state.update { it.copy(busy = false, error = msg, registerDialog = Pair(false, msg)) }
        }
    }

    fun changePassword(current: String, newPass: String, onComplete: () -> Unit) = viewModelScope.launch {
        val repo = repository ?: return@launch
        _state.update { it.copy(busy = true, error = null) }
        try {
            val res = repo.changePassword(ChangePasswordRequest(current, newPass))
            _state.update { it.copy(busy = false, notice = res.message ?: "Password changed.") }
            silentRefreshProfile()
            onComplete()
        } catch (e: Exception) {
            val msg = DhanRajRepository.message(e)
            _state.update { it.copy(busy = false, error = msg, notice = msg) }
        }
    }

    fun logout(onSuccess: () -> Unit) = viewModelScope.launch {
        val repo = repository ?: return@launch
        try {
            repo.logout()
        } catch (_: Exception) {}
        cookieJar?.clear()
        _state.update { it.copy(user = null, wallet = null) }
        onSuccess()
    }

    // --- Admin Operations ---
    fun loadAdminRequests(type: String? = null, search: String? = null) = viewModelScope.launch {
        val repo = repository ?: return@launch
        try {
            val res = repo.adminRequests(type, search)
            _state.update { it.copy(adminRequests = res.items) }
        } catch (e: Exception) {
            _state.update { it.copy(notice = DhanRajRepository.message(e)) }
        }
    }

    fun approveRequest(id: String) = viewModelScope.launch {
        val repo = repository ?: return@launch
        try {
            repo.approveRequest(id)
            showNotice("Request approved.")
            loadAdminRequests()
        } catch (e: Exception) {
            showNotice(DhanRajRepository.message(e))
        }
    }

    fun rejectRequest(id: String) = viewModelScope.launch {
        val repo = repository ?: return@launch
        try {
            repo.rejectRequest(id)
            showNotice("Request rejected.")
            loadAdminRequests()
        } catch (e: Exception) {
            showNotice(DhanRajRepository.message(e))
        }
    }

    fun adminCredit(username: String, phone: String, amount: Long, onDone: () -> Unit) = viewModelScope.launch {
        val repo = repository ?: return@launch
        _state.update { it.copy(busy = true) }
        try {
            val res = repo.adminCredit(AdminCoinAdjustmentRequest(username, phone, amount))
            showNotice("Added ${res.amountAdded} coins to ${res.username}. New balance: ${res.coinBalance}")
            _state.update { it.copy(busy = false) }
            onDone()
        } catch (e: Exception) {
            showNotice(DhanRajRepository.message(e))
            _state.update { it.copy(busy = false) }
        }
    }

    fun adminDebit(username: String, phone: String, amount: Long, onDone: () -> Unit) = viewModelScope.launch {
        val repo = repository ?: return@launch
        _state.update { it.copy(busy = true) }
        try {
            val res = repo.adminDebit(AdminCoinAdjustmentRequest(username, phone, amount))
            showNotice("Removed ${res.amountRemoved} coins from ${res.username}. New balance: ${res.coinBalance}")
            _state.update { it.copy(busy = false) }
            onDone()
        } catch (e: Exception) {
            showNotice(DhanRajRepository.message(e))
            _state.update { it.copy(busy = false) }
        }
    }

    fun declareRoundResult(roundId: Int, session: String, panna: String, onDone: () -> Unit) = viewModelScope.launch {
        val repo = repository ?: return@launch
        _state.update { it.copy(busy = true) }
        try {
            val res = repo.declareResult(roundId, AdminDeclareResultRequest(session, panna))
            showNotice("Result declared. ${res.settled} entries settled.")
            _state.update { it.copy(busy = false) }
            refreshGameMarkets()
            onDone()
        } catch (e: Exception) {
            showNotice(DhanRajRepository.message(e))
            _state.update { it.copy(busy = false) }
        }
    }

    fun saveMarket(
        id: Int?,
        name: String,
        open: String,
        close: String,
        days: List<Int>,
        cutoff: Int,
        paused: Boolean,
        sortOrder: Int,
        onDone: () -> Unit
    ) = viewModelScope.launch {
        val repo = repository ?: return@launch
        _state.update { it.copy(busy = true) }
        try {
            val payload = AdminMarketUpsertRequest(name, open, close, days, cutoff, paused, sortOrder)
            if (id == null) {
                repo.createMarket(payload)
            } else {
                repo.updateMarket(id, payload)
            }
            showNotice("Market schedule saved.")
            _state.update { it.copy(busy = false) }
            refreshGameMarkets()
            onDone()
        } catch (e: Exception) {
            showNotice(DhanRajRepository.message(e))
            _state.update { it.copy(busy = false) }
        }
    }

    fun saveBetType(code: String, winPer10: Long, min: Long, max: Long, enabled: Boolean, onDone: () -> Unit) = viewModelScope.launch {
        val repo = repository ?: return@launch
        _state.update { it.copy(busy = true) }
        try {
            repo.updateBetType(code, AdminBetTypeUpdateRequest(winPer10, min, max, enabled))
            showNotice("Win rate saved.")
            _state.update { it.copy(busy = false) }
            refreshBetTypes()
            onDone()
        } catch (e: Exception) {
            showNotice(DhanRajRepository.message(e))
            _state.update { it.copy(busy = false) }
        }
    }

    companion object {
        fun factory(repository: DhanRajRepository, cookieJar: SecureCookieJar): ViewModelProvider.Factory =
            object : ViewModelProvider.Factory {
                @Suppress("UNCHECKED_CAST")
                override fun <T : ViewModel> create(modelClass: Class<T>): T {
                    return AppViewModel(repository, cookieJar) as T
                }
            }
    }
}
