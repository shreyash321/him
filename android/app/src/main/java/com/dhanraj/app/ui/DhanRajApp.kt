package com.dhanraj.app.ui

import android.app.DatePickerDialog
import android.content.Intent
import android.net.Uri
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.*
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import com.dhanraj.app.data.*
import com.dhanraj.app.ui.theme.*
import com.dhanraj.app.viewmodel.AppState
import com.dhanraj.app.viewmodel.AppViewModel
import java.text.SimpleDateFormat
import java.util.*

enum class AppDestination {
    MARKETS_HOME,
    KINGSTARLINE,
    WALLET,
    LOGIN,
    REGISTER,
    ADMIN
}

enum class NavigationTab(val label: String, val icon: String) {
    ACTIVITY("My Activity", "▤"),
    PASSBOOK("Passbook", "◷"),
    MARKETS("Markets", "⌂"),
    COINS("Coins", "▣"),
    SUPPORT("Support", "•••")
}

@Composable
fun DhanRajApp(viewModel: AppViewModel) {
    val state by viewModel.state.collectAsState()
    val context = LocalContext.current

    var currentDest by remember { mutableStateOf(AppDestination.MARKETS_HOME) }
    var currentTab by remember { mutableStateOf(NavigationTab.MARKETS) }
    var walletInitialTab by remember { mutableStateOf("home") }

    LaunchedEffect(Unit) {
        viewModel.initialize()
    }

    DhanRajTheme {
        Scaffold(
            topBar = {
                SiteTopHeader(
                    user = state.user,
                    onNavigateHome = {
                        currentDest = AppDestination.MARKETS_HOME
                        currentTab = NavigationTab.MARKETS
                    },
                    onNavigateLogin = { currentDest = AppDestination.LOGIN },
                    onNavigateRegister = { currentDest = AppDestination.REGISTER },
                    onNavigateWallet = {
                        walletInitialTab = "home"
                        currentDest = AppDestination.WALLET
                        currentTab = NavigationTab.COINS
                    },
                    onNavigateAdmin = { currentDest = AppDestination.ADMIN },
                    onLogout = {
                        viewModel.logout {
                            currentDest = AppDestination.MARKETS_HOME
                            currentTab = NavigationTab.MARKETS
                        }
                    }
                )
            },
            bottomBar = {
                MarketBottomNavBar(
                    currentTab = currentTab,
                    onTabSelected = { tab ->
                        currentTab = tab
                        when (tab) {
                            NavigationTab.MARKETS -> {
                                currentDest = AppDestination.MARKETS_HOME
                            }
                            NavigationTab.ACTIVITY -> {
                                if (state.user == null) {
                                    currentDest = AppDestination.LOGIN
                                } else {
                                    walletInitialTab = "bids"
                                    viewModel.refreshWallet()
                                    currentDest = AppDestination.WALLET
                                }
                            }
                            NavigationTab.PASSBOOK -> {
                                if (state.user == null) {
                                    currentDest = AppDestination.LOGIN
                                } else {
                                    walletInitialTab = "passbook"
                                    viewModel.refreshWallet()
                                    currentDest = AppDestination.WALLET
                                }
                            }
                            NavigationTab.COINS -> {
                                if (state.user == null) {
                                    currentDest = AppDestination.LOGIN
                                } else {
                                    walletInitialTab = "funds"
                                    viewModel.refreshWallet()
                                    currentDest = AppDestination.WALLET
                                }
                            }
                            NavigationTab.SUPPORT -> {
                                if (state.user == null) {
                                    currentDest = AppDestination.LOGIN
                                } else {
                                    walletInitialTab = "support"
                                    currentDest = AppDestination.WALLET
                                }
                            }
                        }
                    }
                )
            }
        ) { paddingValues ->
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .background(WebsiteBackgroundBrush)
            ) {
                when (currentDest) {
                    AppDestination.MARKETS_HOME -> {
                        HomeScreen(
                            state = state,
                            viewModel = viewModel,
                            onNavigateKingStarline = { currentDest = AppDestination.KINGSTARLINE },
                            onNavigateWallet = {
                                if (state.user == null) currentDest = AppDestination.LOGIN
                                else {
                                    walletInitialTab = "home"
                                    currentDest = AppDestination.WALLET
                                    currentTab = NavigationTab.COINS
                                }
                            },
                            onNavigateCoinRequest = {
                                if (state.user == null) currentDest = AppDestination.LOGIN
                                else {
                                    walletInitialTab = "fund-request"
                                    currentDest = AppDestination.WALLET
                                    currentTab = NavigationTab.COINS
                                }
                            }
                        )
                    }
                    AppDestination.KINGSTARLINE -> {
                        KingStarlineScreen(
                            state = state,
                            viewModel = viewModel,
                            onNavigateWallet = {
                                walletInitialTab = "home"
                                currentDest = AppDestination.WALLET
                                currentTab = NavigationTab.COINS
                            },
                            onNavigateLogin = { currentDest = AppDestination.LOGIN }
                        )
                    }
                    AppDestination.WALLET -> {
                        WalletScreen(
                            state = state,
                            viewModel = viewModel,
                            initialTab = walletInitialTab,
                            onNavigateHome = {
                                currentDest = AppDestination.MARKETS_HOME
                                currentTab = NavigationTab.MARKETS
                            },
                            onLogout = {
                                viewModel.logout {
                                    currentDest = AppDestination.MARKETS_HOME
                                    currentTab = NavigationTab.MARKETS
                                }
                            }
                        )
                    }
                    AppDestination.LOGIN -> {
                        LoginScreen(
                            state = state,
                            viewModel = viewModel,
                            onSuccess = {
                                if (state.user?.role == "admin" || state.user?.mustChangePassword == true) {
                                    currentDest = AppDestination.ADMIN
                                } else {
                                    walletInitialTab = "home"
                                    currentDest = AppDestination.WALLET
                                    currentTab = NavigationTab.COINS
                                }
                            },
                            onNavigateRegister = { currentDest = AppDestination.REGISTER }
                        )
                    }
                    AppDestination.REGISTER -> {
                        RegisterScreen(
                            state = state,
                            viewModel = viewModel,
                            onSuccess = { currentDest = AppDestination.LOGIN },
                            onNavigateLogin = { currentDest = AppDestination.LOGIN }
                        )
                    }
                    AppDestination.ADMIN -> {
                        AdminScreen(
                            state = state,
                            viewModel = viewModel,
                            onNavigateWallet = {
                                walletInitialTab = "home"
                                currentDest = AppDestination.WALLET
                            },
                            onLogout = {
                                viewModel.logout {
                                    currentDest = AppDestination.MARKETS_HOME
                                    currentTab = NavigationTab.MARKETS
                                }
                            }
                        )
                    }
                }

                // Global Toast
                GlobalToast(message = state.notice, onDismiss = { viewModel.clearNotice() })

                // Registration Dialog
                if (state.registerDialog != null) {
                    RegistrationResultDialog(
                        result = state.registerDialog,
                        onDismiss = { success ->
                            viewModel.clearRegisterDialog()
                            if (success) currentDest = AppDestination.LOGIN
                        }
                    )
                }
            }
        }
    }
}

// -------------------------------------------------------------
// Top Header & Bottom Nav
// -------------------------------------------------------------
@Composable
fun DhanRajWordmark(modifier: Modifier = Modifier, fontSize: Int = 24) {
    Row(modifier = modifier, verticalAlignment = Alignment.CenterVertically) {
        Box(
            modifier = Modifier
                .size((fontSize * 1.05).dp)
                .clip(CircleShape)
                .background(LogoRed),
            contentAlignment = Alignment.Center
        ) {
            Text(text = "D", color = Color.White, fontSize = (fontSize * 0.85).sp, fontWeight = FontWeight.Black)
        }
        Spacer(modifier = Modifier.width(2.dp))
        Text(text = "han", color = TextDark, fontSize = fontSize.sp, fontWeight = FontWeight.Bold)
        Text(text = "RAJ", color = LogoRed, fontSize = fontSize.sp, fontWeight = FontWeight.Black)
    }
}

@Composable
fun SiteTopHeader(
    user: UserProfile?,
    onNavigateHome: () -> Unit,
    onNavigateLogin: () -> Unit,
    onNavigateRegister: () -> Unit,
    onNavigateWallet: () -> Unit,
    onNavigateAdmin: () -> Unit,
    onLogout: () -> Unit
) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        color = LavenderLight,
        shadowElevation = 4.dp
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .border(width = 1.dp, color = LineBorder)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 12.dp, vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                if (user == null) {
                    Button(
                        onClick = onNavigateLogin,
                        colors = ButtonDefaults.buttonColors(containerColor = RedPrimary),
                        shape = RoundedCornerShape(8.dp),
                        contentPadding = PaddingValues(horizontal = 10.dp, vertical = 4.dp),
                        modifier = Modifier.height(34.dp)
                    ) {
                        Text(text = "Login", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    }
                    DhanRajWordmark(fontSize = 22, modifier = Modifier.clickable { onNavigateHome() })
                    Button(
                        onClick = onNavigateRegister,
                        colors = ButtonDefaults.buttonColors(containerColor = RedPrimary),
                        shape = RoundedCornerShape(8.dp),
                        contentPadding = PaddingValues(horizontal = 10.dp, vertical = 4.dp),
                        modifier = Modifier.height(34.dp)
                    ) {
                        Text(text = "Register", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    }
                } else {
                    Surface(
                        color = PanelWhite,
                        shape = RoundedCornerShape(16.dp),
                        border = androidx.compose.foundation.BorderStroke(1.dp, CardBorder),
                        modifier = Modifier
                            .height(34.dp)
                            .clickable { onNavigateWallet() }
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.padding(horizontal = 8.dp)) {
                            Text(
                                text = "☻ ${user.username}",
                                color = Wine,
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold,
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis
                            )
                        }
                    }

                    DhanRajWordmark(fontSize = 20, modifier = Modifier.clickable { onNavigateHome() })

                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        Surface(
                            color = Wine,
                            shape = RoundedCornerShape(16.dp),
                            modifier = Modifier
                                .height(32.dp)
                                .clickable { onNavigateWallet() }
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.padding(horizontal = 8.dp)) {
                                Text(
                                    text = "${user.coinBalance} coins",
                                    color = Color.White,
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }
                        if (user.role == "admin") {
                            Button(
                                onClick = onNavigateAdmin,
                                colors = ButtonDefaults.buttonColors(containerColor = WineDeep),
                                shape = RoundedCornerShape(8.dp),
                                contentPadding = PaddingValues(horizontal = 8.dp, vertical = 2.dp),
                                modifier = Modifier.height(32.dp)
                            ) {
                                Text(text = "Admin", color = Color.White, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                            }
                        }
                        Button(
                            onClick = onLogout,
                            colors = ButtonDefaults.buttonColors(containerColor = RedPrimary),
                            shape = RoundedCornerShape(8.dp),
                            contentPadding = PaddingValues(horizontal = 8.dp, vertical = 2.dp),
                            modifier = Modifier.height(32.dp)
                        ) {
                            Text(text = "Logout", color = Color.White, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun MarketBottomNavBar(
    currentTab: NavigationTab,
    onTabSelected: (NavigationTab) -> Unit
) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        color = PanelAlt,
        shadowElevation = 10.dp
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .border(width = 1.dp, color = CardBorder)
                .navigationBarsPadding()
                .padding(vertical = 4.dp),
            horizontalArrangement = Arrangement.SpaceAround,
            verticalAlignment = Alignment.CenterVertically
        ) {
            NavigationTab.values().forEach { tab ->
                val isSelected = currentTab == tab
                Column(
                    modifier = Modifier
                        .weight(1f)
                        .clickable { onTabSelected(tab) }
                        .padding(vertical = 4.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    Box(
                        modifier = Modifier
                            .size(28.dp)
                            .clip(CircleShape)
                            .background(if (isSelected) RedPrimary else Color.Transparent),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = tab.icon,
                            color = if (isSelected) Color.White else MutedPurple,
                            fontSize = 15.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                    Spacer(modifier = Modifier.height(2.dp))
                    Text(
                        text = tab.label,
                        color = if (isSelected) RedPrimary else MutedPurple,
                        fontSize = 10.sp,
                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal
                    )
                }
            }
        }
    }
}

// -------------------------------------------------------------
// Home Screen (Markets Tab)
// -------------------------------------------------------------
@Composable
fun HomeScreen(
    state: AppState,
    viewModel: AppViewModel,
    onNavigateKingStarline: () -> Unit,
    onNavigateWallet: () -> Unit,
    onNavigateCoinRequest: () -> Unit
) {
    val context = LocalContext.current
    val infiniteTransition = rememberInfiniteTransition(label = "cta-glow")
    val glowElevation by infiniteTransition.animateFloat(
        initialValue = 4f,
        targetValue = 12f,
        animationSpec = infiniteRepeatable(
            animation = tween(1200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "glow"
    )

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 12.dp),
        contentPadding = PaddingValues(top = 12.dp, bottom = 24.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // KingStarline CTA Card
        item {
            Surface(
                modifier = Modifier.fillMaxWidth(),
                color = PanelCard,
                shape = RoundedCornerShape(18.dp),
                border = androidx.compose.foundation.BorderStroke(1.dp, CardBorder),
                shadowElevation = 6.dp
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "VIRTUAL POINTS GAME",
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        color = MutedPurple,
                        letterSpacing = 1.sp
                    )
                    Spacer(modifier = Modifier.height(10.dp))
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .shadow(glowElevation.dp, RoundedCornerShape(16.dp))
                            .clip(RoundedCornerShape(16.dp))
                            .background(CtaButtonBrush)
                            .clickable { onNavigateKingStarline() }
                            .padding(horizontal = 18.dp, vertical = 14.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Column {
                                Text(text = "KingStarline", color = Color.White, fontSize = 19.sp, fontWeight = FontWeight.ExtraBold)
                                Text(text = "Tap to Play", color = Color.White.copy(alpha = 0.9f), fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
                            }
                            Text(text = "▶", color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }

        // Shortcuts Grid
        item {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    ShortcutCard(
                        icon = "▶",
                        title = "Market results",
                        modifier = Modifier.weight(1f),
                        onClick = { viewModel.refreshLiveMarkets() }
                    )
                    ShortcutCard(
                        icon = "◉",
                        title = "Virtual coin account",
                        modifier = Modifier.weight(1f),
                        onClick = onNavigateWallet
                    )
                }
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    ShortcutCard(
                        icon = "◉",
                        title = "WhatsApp support",
                        modifier = Modifier.weight(1f),
                        onClick = {
                            val user = state.user
                            val text = if (user != null) {
                                "Hello, I need help with my DhanRAJ account.\nUsername: ${user.username}\nPhone: ${user.phone ?: "Not provided"}\nRequest: Please help me with my account or service issue."
                            } else {
                                "Hello, I need help with my DhanRAJ account."
                            }
                            val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://wa.me/918699915927?text=${Uri.encode(text)}"))
                            try { context.startActivity(intent) } catch (_: Exception) { viewModel.showNotice("WhatsApp not available.") }
                        }
                    )
                    ShortcutCard(
                        icon = "＋",
                        title = "Request coin adjustment",
                        modifier = Modifier.weight(1f),
                        onClick = onNavigateCoinRequest
                    )
                }
            }
        }

        // Live Market Results Section Header
        item {
            Surface(modifier = Modifier.fillMaxWidth(), color = Wine, shape = RoundedCornerShape(12.dp)) {
                Text(
                    text = "Live Market Results",
                    color = Color.White,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(12.dp)
                )
            }
        }

        // Status
        item {
            Text(
                text = state.resultsStatus,
                color = MutedPurple,
                fontSize = 12.sp,
                modifier = Modifier.fillMaxWidth(),
                textAlign = TextAlign.Center
            )
        }

        // Results Cards
        if (state.marketResults.isEmpty()) {
            item {
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    color = PanelAlt,
                    shape = RoundedCornerShape(14.dp),
                    border = androidx.compose.foundation.BorderStroke(1.dp, CardBorder)
                ) {
                    Box(modifier = Modifier.padding(24.dp), contentAlignment = Alignment.Center) {
                        Text(text = "Loading market data…", color = MutedPurple, fontSize = 14.sp)
                    }
                }
            }
        } else {
            items(state.marketResults) { market ->
                MarketResultCard(
                    market = market,
                    onPlay = onNavigateKingStarline,
                    onChart = { viewModel.showNotice("${market.marketName ?: "Market"} Chart: ${market.getDisplayResult()}") }
                )
            }
        }

        // Disclaimer
        item {
            Text(
                text = "Virtual points only. No real money. For entertainment.",
                fontSize = 12.sp,
                color = MutedPurple,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 16.dp),
                textAlign = TextAlign.Center
            )
        }
    }
}

@Composable
fun ShortcutCard(icon: String, title: String, modifier: Modifier = Modifier, onClick: () -> Unit) {
    Surface(
        modifier = modifier
            .height(48.dp)
            .clickable { onClick() },
        color = LavenderLight,
        shape = RoundedCornerShape(22.dp),
        shadowElevation = 3.dp
    ) {
        Row(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 10.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center
        ) {
            Box(
                modifier = Modifier
                    .size(24.dp)
                    .clip(CircleShape)
                    .background(RedPrimary),
                contentAlignment = Alignment.Center
            ) {
                Text(text = icon, color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold)
            }
            Spacer(modifier = Modifier.width(6.dp))
            Text(text = title, color = Ink, fontSize = 11.sp, fontWeight = FontWeight.SemiBold, maxLines = 1)
        }
    }
}

@Composable
fun MarketResultCard(market: MarketResultItem, onPlay: () -> Unit, onChart: () -> Unit) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        color = PanelAlt,
        shape = RoundedCornerShape(15.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, CardBorder),
        shadowElevation = 3.dp
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text(text = "Open: ${market.openTime ?: "--:--"}", fontSize = 11.sp, color = MutedPurple)
                Text(text = "Close: ${market.closeTime ?: "--:--"}", fontSize = 11.sp, color = MutedPurple)
            }
            Spacer(modifier = Modifier.height(6.dp))
            Text(text = market.marketName ?: "MARKET", fontSize = 15.sp, fontWeight = FontWeight.Bold, color = Ink)
            Spacer(modifier = Modifier.height(6.dp))
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.Center) {
                Text(text = market.getFormattedOpenPanel(), fontSize = 18.sp, fontWeight = FontWeight.Bold, color = RedPrimary)
                Text(text = "-", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = RedPrimary)
                Text(
                    text = "${market.getFormattedOpenResult()}${market.getFormattedCloseResult()}",
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Black,
                    color = RedDeep
                )
                Text(text = "-", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = RedPrimary)
                Text(text = market.getFormattedClosePanel(), fontSize = 18.sp, fontWeight = FontWeight.Bold, color = RedPrimary)
            }
            Spacer(modifier = Modifier.height(10.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                Button(
                    onClick = onChart,
                    colors = ButtonDefaults.buttonColors(containerColor = RedPrimary),
                    shape = RoundedCornerShape(16.dp),
                    contentPadding = PaddingValues(horizontal = 14.dp, vertical = 2.dp),
                    modifier = Modifier.height(30.dp)
                ) {
                    Text(text = "Chart", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                }
                Button(
                    onClick = onPlay,
                    colors = ButtonDefaults.buttonColors(containerColor = RedPrimary),
                    shape = RoundedCornerShape(16.dp),
                    contentPadding = PaddingValues(horizontal = 14.dp, vertical = 2.dp),
                    modifier = Modifier.height(30.dp)
                ) {
                    Text(text = "Play", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}

// -------------------------------------------------------------
// KingStarline Screen
// -------------------------------------------------------------
enum class GameView { MARKETS, MENU, BET, RATES, BETS, RESULTS }

data class GameType(val code: String, val label: String, val kind: String, val hasSession: Boolean)

val GAME_TYPES = listOf(
    GameType("SINGLE_DIGIT", "Single Digit", "digit", true),
    GameType("JODI", "Jodi Digit", "jodi", false),
    GameType("SINGLE_PANNA", "Single Panna", "single", true),
    GameType("DOUBLE_PANNA", "Double Panna", "double", true),
    GameType("TRIPLE_PANNA", "Triple Panna", "triple", true)
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun KingStarlineScreen(
    state: AppState,
    viewModel: AppViewModel,
    onNavigateWallet: () -> Unit,
    onNavigateLogin: () -> Unit
) {
    val context = LocalContext.current
    var currentView by remember { mutableStateOf(GameView.MARKETS) }
    var selectedType by remember { mutableStateOf<GameType?>(null) }

    val dateFormat = remember { SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()) }
    var betDate by remember { mutableStateOf(dateFormat.format(Date())) }
    var betSession by remember { mutableStateOf("open") }
    var selection by remember { mutableStateOf("") }
    var points by remember { mutableStateOf("10") }
    var formError by remember { mutableStateOf<String?>(null) }
    var showConfirmSheet by remember { mutableStateOf(false) }

    var calcType by remember { mutableStateOf("SINGLE_DIGIT") }
    var calcPoints by remember { mutableStateOf("10") }

    Column(modifier = Modifier.fillMaxSize()) {
        // KingStarline top indicator
        Surface(modifier = Modifier.fillMaxWidth(), color = LavenderLight, shadowElevation = 2.dp) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 14.dp, vertical = 10.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(text = "King", fontSize = 20.sp, fontWeight = FontWeight.Black, color = Ink)
                    Text(text = "Starline", fontSize = 20.sp, fontWeight = FontWeight.Black, color = RedPrimary)
                }
                Surface(
                    color = Color.White,
                    shape = RoundedCornerShape(20.dp),
                    modifier = Modifier.clickable { onNavigateWallet() }
                ) {
                    Text(
                        text = if (state.user != null) "Points: ${state.user.coinBalance}" else "Log in for Points",
                        color = Wine,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)
                    )
                }
            }
        }

        Box(modifier = Modifier.fillMaxSize().padding(horizontal = 12.dp)) {
            when (currentView) {
                GameView.MARKETS -> {
                    LazyColumn(
                        modifier = Modifier.fillMaxSize(),
                        contentPadding = PaddingValues(top = 12.dp, bottom = 24.dp),
                        verticalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        item {
                            Surface(
                                modifier = Modifier.fillMaxWidth(),
                                color = PanelAlt,
                                shape = RoundedCornerShape(16.dp),
                                border = androidx.compose.foundation.BorderStroke(1.dp, CardBorder)
                            ) {
                                Column(modifier = Modifier.padding(16.dp)) {
                                    Text(text = "KingStarline", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = Ink)
                                    Text(text = "Choose a market to view its sessions and available games.", fontSize = 13.sp, color = MutedPurple)
                                }
                            }
                        }

                        if (state.markets.isEmpty()) {
                            item {
                                Text(text = "Loading markets...", color = MutedPurple, fontSize = 14.sp, modifier = Modifier.padding(16.dp))
                            }
                        } else {
                            items(state.markets) { market ->
                                val isRunning = market.status == "RUNNING"
                                Surface(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .clickable {
                                            if (isRunning) {
                                                viewModel.selectMarket(market) { currentView = GameView.MENU }
                                            } else {
                                                viewModel.showNotice("Betting is closed for this market.")
                                            }
                                        },
                                    color = if (isRunning) PanelCard else Color(0xFFE8E5EA),
                                    shape = RoundedCornerShape(14.dp),
                                    border = if (isRunning) androidx.compose.foundation.BorderStroke(2.dp, GreenBadge) else null,
                                    shadowElevation = 2.dp
                                ) {
                                    Column(modifier = Modifier.padding(12.dp)) {
                                        Row(
                                            modifier = Modifier.fillMaxWidth(),
                                            horizontalArrangement = Arrangement.SpaceBetween,
                                            verticalAlignment = Alignment.CenterVertically
                                        ) {
                                            Text(
                                                text = market.name,
                                                fontSize = 15.sp,
                                                fontWeight = FontWeight.Bold,
                                                color = if (isRunning) Ink else ClosedBadgeText
                                            )
                                            Surface(
                                                color = if (isRunning) GreenBadgeBg else ClosedBadgeBg,
                                                shape = RoundedCornerShape(20.dp)
                                            ) {
                                                Row(
                                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp),
                                                    verticalAlignment = Alignment.CenterVertically
                                                ) {
                                                    if (isRunning) {
                                                        Box(modifier = Modifier.size(6.dp).clip(CircleShape).background(GreenBadge))
                                                        Spacer(modifier = Modifier.width(4.dp))
                                                    }
                                                    Text(
                                                        text = if (isRunning) "Market Running" else "Betting Closed",
                                                        color = if (isRunning) GreenBadge else ClosedBadgeText,
                                                        fontSize = 11.sp,
                                                        fontWeight = FontWeight.Bold
                                                    )
                                                }
                                            }
                                        }
                                        Spacer(modifier = Modifier.height(4.dp))
                                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                            Text(text = "Open: ${market.openTime} - Close: ${market.closeTime}", fontSize = 12.sp, color = MutedPurple)
                                            Text(text = market.latestResult ?: "", fontSize = 12.sp, color = MutedPurple)
                                        }
                                        if (!market.bettingSession.isNullOrBlank()) {
                                            Text(text = market.bettingSession, fontSize = 11.sp, color = Wine, fontWeight = FontWeight.SemiBold)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                GameView.MENU -> {
                    LazyColumn(
                        modifier = Modifier.fillMaxSize(),
                        contentPadding = PaddingValues(top = 12.dp, bottom = 24.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        item {
                            Surface(
                                modifier = Modifier.fillMaxWidth(),
                                color = PanelAlt,
                                shape = RoundedCornerShape(16.dp),
                                border = androidx.compose.foundation.BorderStroke(1.dp, CardBorder)
                            ) {
                                Column(modifier = Modifier.padding(16.dp)) {
                                    Row(
                                        modifier = Modifier.fillMaxWidth(),
                                        horizontalArrangement = Arrangement.SpaceBetween,
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Button(
                                            onClick = { currentView = GameView.MARKETS },
                                            colors = ButtonDefaults.buttonColors(containerColor = PanelCard),
                                            shape = RoundedCornerShape(12.dp),
                                            border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder)
                                        ) {
                                            Text("Back", color = Ink, fontWeight = FontWeight.Bold)
                                        }
                                        Surface(color = Color.White, shape = RoundedCornerShape(16.dp)) {
                                            Text(
                                                text = state.selectedMarket?.name ?: "",
                                                color = Wine,
                                                fontWeight = FontWeight.Bold,
                                                fontSize = 12.sp,
                                                modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)
                                            )
                                        }
                                    }

                                    Spacer(modifier = Modifier.height(14.dp))
                                    Text(text = "Choose a game", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Ink)
                                    Spacer(modifier = Modifier.height(10.dp))

                                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                        GAME_TYPES.forEach { gType ->
                                            Surface(
                                                modifier = Modifier
                                                    .fillMaxWidth()
                                                    .clickable {
                                                        if (state.user == null) {
                                                            onNavigateLogin()
                                                        } else {
                                                            selectedType = gType
                                                            selection = ""
                                                            points = "10"
                                                            formError = null
                                                            betSession = "open"
                                                            currentView = GameView.BET
                                                        }
                                                    },
                                                color = PanelCard,
                                                shape = RoundedCornerShape(12.dp),
                                                border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder)
                                            ) {
                                                Row(
                                                    modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 14.dp),
                                                    horizontalArrangement = Arrangement.SpaceBetween,
                                                    verticalAlignment = Alignment.CenterVertically
                                                ) {
                                                    Text(text = gType.label, fontSize = 14.sp, fontWeight = FontWeight.Bold, color = Ink)
                                                    Text("▶", color = RedPrimary, fontSize = 14.sp)
                                                }
                                            }
                                        }
                                    }

                                    Spacer(modifier = Modifier.height(16.dp))

                                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                                        Button(
                                            onClick = { currentView = GameView.RATES },
                                            modifier = Modifier.weight(1f),
                                            colors = ButtonDefaults.buttonColors(containerColor = PanelCard),
                                            shape = RoundedCornerShape(10.dp),
                                            border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder),
                                            contentPadding = PaddingValues(4.dp)
                                        ) {
                                            Text("Win Rates", color = Ink, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                                        }
                                        Button(
                                            onClick = {
                                                viewModel.refreshBets()
                                                currentView = GameView.BETS
                                            },
                                            modifier = Modifier.weight(1f),
                                            colors = ButtonDefaults.buttonColors(containerColor = PanelCard),
                                            shape = RoundedCornerShape(10.dp),
                                            border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder),
                                            contentPadding = PaddingValues(4.dp)
                                        ) {
                                            Text("My Bets", color = Ink, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                                        }
                                        Button(
                                            onClick = {
                                                viewModel.refreshResults()
                                                currentView = GameView.RESULTS
                                            },
                                            modifier = Modifier.weight(1f),
                                            colors = ButtonDefaults.buttonColors(containerColor = PanelCard),
                                            shape = RoundedCornerShape(10.dp),
                                            border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder),
                                            contentPadding = PaddingValues(4.dp)
                                        ) {
                                            Text("Results", color = Ink, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                                        }
                                        Button(
                                            onClick = onNavigateWallet,
                                            modifier = Modifier.weight(1f),
                                            colors = ButtonDefaults.buttonColors(containerColor = PanelCard),
                                            shape = RoundedCornerShape(10.dp),
                                            border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder),
                                            contentPadding = PaddingValues(4.dp)
                                        ) {
                                            Text("Wallet", color = Ink, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                GameView.BET -> {
                    val currentType = selectedType ?: GAME_TYPES.first()
                    val round = state.selectedRound

                    LazyColumn(
                        modifier = Modifier.fillMaxSize(),
                        contentPadding = PaddingValues(top = 12.dp, bottom = 24.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        item {
                            Surface(
                                modifier = Modifier.fillMaxWidth(),
                                color = PanelAlt,
                                shape = RoundedCornerShape(16.dp),
                                border = androidx.compose.foundation.BorderStroke(1.dp, CardBorder)
                            ) {
                                Column(modifier = Modifier.padding(16.dp)) {
                                    Row(
                                        modifier = Modifier.fillMaxWidth(),
                                        horizontalArrangement = Arrangement.SpaceBetween,
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Button(
                                            onClick = { currentView = GameView.MENU },
                                            colors = ButtonDefaults.buttonColors(containerColor = PanelCard),
                                            shape = RoundedCornerShape(12.dp),
                                            border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder)
                                        ) {
                                            Text("Back", color = Ink, fontWeight = FontWeight.Bold)
                                        }
                                        Surface(
                                            color = Color.White,
                                            shape = RoundedCornerShape(16.dp),
                                            modifier = Modifier.clickable { currentView = GameView.RATES }
                                        ) {
                                            Text(
                                                text = "Win Rates",
                                                color = Wine,
                                                fontWeight = FontWeight.Bold,
                                                fontSize = 12.sp,
                                                modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)
                                            )
                                        }
                                    }

                                    Spacer(modifier = Modifier.height(12.dp))
                                    Text(text = currentType.label, fontSize = 19.sp, fontWeight = FontWeight.Bold, color = Ink)
                                    Text(text = "Market: ${state.selectedMarket?.name ?: ""} · Minimum 10 points", fontSize = 12.sp, color = MutedPurple)

                                    Spacer(modifier = Modifier.height(14.dp))
                                    Text("Choose Date", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = Ink)
                                    OutlinedTextField(
                                        value = betDate,
                                        onValueChange = {},
                                        readOnly = true,
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .clickable {
                                                val c = Calendar.getInstance()
                                                DatePickerDialog(context, { _, year, month, dayOfMonth ->
                                                    val picked = String.format(Locale.getDefault(), "%04d-%02d-%02d", year, month + 1, dayOfMonth)
                                                    betDate = picked
                                                    viewModel.refreshRound(picked)
                                                }, c.get(Calendar.YEAR), c.get(Calendar.MONTH), c.get(Calendar.DAY_OF_MONTH)).show()
                                            },
                                        shape = RoundedCornerShape(12.dp),
                                        colors = OutlinedTextFieldDefaults.colors(
                                            focusedContainerColor = PanelCard,
                                            unfocusedContainerColor = PanelCard
                                        )
                                    )

                                    if (currentType.hasSession) {
                                        Spacer(modifier = Modifier.height(10.dp))
                                        Text("Choose Session", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = Ink)
                                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                                            val openEnabled = round?.openBetting != false
                                            val closeEnabled = round?.closeBetting != false

                                            Surface(
                                                modifier = Modifier.weight(1f).clickable(enabled = openEnabled) { betSession = "open" },
                                                color = if (betSession == "open") LavenderLight else PanelCard,
                                                shape = RoundedCornerShape(12.dp),
                                                border = androidx.compose.foundation.BorderStroke(1.dp, if (betSession == "open") RedPrimary else LineBorder)
                                            ) {
                                                Row(modifier = Modifier.padding(10.dp), verticalAlignment = Alignment.CenterVertically) {
                                                    RadioButton(selected = betSession == "open", onClick = { betSession = "open" }, enabled = openEnabled)
                                                    Text(text = "Open", fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
                                                }
                                            }

                                            Surface(
                                                modifier = Modifier.weight(1f).clickable(enabled = closeEnabled) { betSession = "close" },
                                                color = if (betSession == "close") LavenderLight else PanelCard,
                                                shape = RoundedCornerShape(12.dp),
                                                border = androidx.compose.foundation.BorderStroke(1.dp, if (betSession == "close") RedPrimary else LineBorder)
                                            ) {
                                                Row(modifier = Modifier.padding(10.dp), verticalAlignment = Alignment.CenterVertically) {
                                                    RadioButton(selected = betSession == "close", onClick = { betSession = "close" }, enabled = closeEnabled)
                                                    Text(text = "Close", fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
                                                }
                                            }
                                        }
                                    }

                                    Spacer(modifier = Modifier.height(10.dp))
                                    Text(
                                        text = when (currentType.kind) {
                                            "digit" -> "Selection (0-9)"
                                            "jodi" -> "Selection (00-99)"
                                            else -> "Selection (3-digit panna)"
                                        },
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = Ink
                                    )
                                    OutlinedTextField(
                                        value = selection,
                                        onValueChange = { newVal ->
                                            val filtered = newVal.filter { it.isDigit() }
                                            val maxLen = when (currentType.kind) {
                                                "digit" -> 1
                                                "jodi" -> 2
                                                else -> 3
                                            }
                                            val truncated = filtered.take(maxLen)
                                            selection = truncated
                                            if (currentType.kind in listOf("single", "double", "triple")) {
                                                viewModel.suggestPanna(currentType.kind, truncated)
                                            }
                                        },
                                        modifier = Modifier.fillMaxWidth(),
                                        shape = RoundedCornerShape(12.dp),
                                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                        colors = OutlinedTextFieldDefaults.colors(
                                            focusedContainerColor = PanelCard,
                                            unfocusedContainerColor = PanelCard
                                        )
                                    )

                                    if (state.pannaSuggestions.isNotEmpty()) {
                                        Spacer(modifier = Modifier.height(6.dp))
                                        Text("Suggestions:", fontSize = 11.sp, color = MutedPurple)
                                        LazyRow(horizontalArrangement = Arrangement.spacedBy(6.dp), modifier = Modifier.padding(vertical = 4.dp)) {
                                            items(state.pannaSuggestions) { sug ->
                                                Surface(
                                                    color = LavenderLight,
                                                    shape = RoundedCornerShape(14.dp),
                                                    border = androidx.compose.foundation.BorderStroke(1.dp, CardBorder),
                                                    modifier = Modifier.clickable { selection = sug }
                                                ) {
                                                    Text(
                                                        text = sug,
                                                        fontSize = 12.sp,
                                                        fontWeight = FontWeight.Bold,
                                                        color = Ink,
                                                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                                    )
                                                }
                                            }
                                        }
                                    }

                                    Spacer(modifier = Modifier.height(10.dp))
                                    Text("Points", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = Ink)
                                    OutlinedTextField(
                                        value = points,
                                        onValueChange = { points = it.filter { ch -> ch.isDigit() } },
                                        modifier = Modifier.fillMaxWidth(),
                                        shape = RoundedCornerShape(12.dp),
                                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                        colors = OutlinedTextFieldDefaults.colors(
                                            focusedContainerColor = PanelCard,
                                            unfocusedContainerColor = PanelCard
                                        )
                                    )

                                    if (!formError.isNullOrBlank()) {
                                        Spacer(modifier = Modifier.height(6.dp))
                                        Text(text = formError.orEmpty(), color = RedDeep, fontSize = 12.sp)
                                    }

                                    Spacer(modifier = Modifier.height(16.dp))
                                    Button(
                                        onClick = {
                                            formError = null
                                            val pts = points.toLongOrNull() ?: 0
                                            val userBal = state.user?.coinBalance ?: 0
                                            if (currentType.kind == "digit" && (selection.length != 1 || !selection[0].isDigit())) {
                                                formError = "Enter one digit from 0 to 9."
                                            } else if (currentType.kind == "jodi" && (selection.length != 2 || !selection.all { it.isDigit() })) {
                                                formError = "Enter a two-digit Jodi."
                                            } else if (currentType.kind in listOf("single", "double", "triple") && selection.length != 3) {
                                                formError = "Invalid panna."
                                            } else if (pts < 10) {
                                                formError = "Minimum points are 10."
                                            } else if (pts > userBal) {
                                                formError = "Should be less than wallet balance $userBal"
                                                viewModel.showNotice("Should be less than wallet balance $userBal")
                                            } else {
                                                showConfirmSheet = true
                                            }
                                        },
                                        colors = ButtonDefaults.buttonColors(containerColor = RedPrimary),
                                        shape = RoundedCornerShape(14.dp),
                                        modifier = Modifier.fillMaxWidth().height(48.dp)
                                    ) {
                                        Text("Proceed", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 15.sp)
                                    }
                                }
                            }
                        }
                    }
                }

                GameView.RATES -> {
                    LazyColumn(
                        modifier = Modifier.fillMaxSize(),
                        contentPadding = PaddingValues(top = 12.dp, bottom = 24.dp),
                        verticalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        item {
                            Surface(
                                modifier = Modifier.fillMaxWidth(),
                                color = PanelAlt,
                                shape = RoundedCornerShape(16.dp),
                                border = androidx.compose.foundation.BorderStroke(1.dp, CardBorder)
                            ) {
                                Column(modifier = Modifier.padding(16.dp)) {
                                    Row(
                                        modifier = Modifier.fillMaxWidth(),
                                        horizontalArrangement = Arrangement.SpaceBetween,
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Button(
                                            onClick = { currentView = GameView.MENU },
                                            colors = ButtonDefaults.buttonColors(containerColor = PanelCard),
                                            shape = RoundedCornerShape(12.dp),
                                            border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder)
                                        ) {
                                            Text("Back", color = Ink, fontWeight = FontWeight.Bold)
                                        }
                                        Text(text = "Win Rates", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Ink)
                                    }

                                    Spacer(modifier = Modifier.height(8.dp))
                                    Text(text = "Winning amount includes your stake.", fontSize = 12.sp, color = MutedPurple)
                                    Spacer(modifier = Modifier.height(12.dp))

                                    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                                        state.betTypes.forEach { rate ->
                                            Surface(
                                                modifier = Modifier.fillMaxWidth(),
                                                color = PanelCard,
                                                shape = RoundedCornerShape(10.dp),
                                                border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder)
                                            ) {
                                                Row(
                                                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 10.dp),
                                                    horizontalArrangement = Arrangement.SpaceBetween
                                                ) {
                                                    Text(rate.label, fontWeight = FontWeight.Bold, color = Ink)
                                                    Text("10 - ${rate.winPer10}", fontWeight = FontWeight.Bold, color = RedPrimary)
                                                }
                                            }
                                        }
                                    }

                                    Spacer(modifier = Modifier.height(16.dp))
                                    Text("Interactive Win Calculator", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = Ink)
                                    Spacer(modifier = Modifier.height(8.dp))

                                    OutlinedTextField(
                                        value = calcPoints,
                                        onValueChange = { calcPoints = it.filter { ch -> ch.isDigit() } },
                                        label = { Text("Points") },
                                        modifier = Modifier.fillMaxWidth(),
                                        shape = RoundedCornerShape(12.dp),
                                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
                                    )

                                    Spacer(modifier = Modifier.height(8.dp))
                                    val pts = calcPoints.toLongOrNull() ?: 10
                                    val matchedRate = state.betTypes.find { it.code == calcType } ?: state.betTypes.firstOrNull()
                                    val winPoints = if (matchedRate != null) (pts * matchedRate.winPer10) / 10 else 0

                                    Surface(
                                        color = PanelWhite,
                                        shape = RoundedCornerShape(12.dp),
                                        border = androidx.compose.foundation.BorderStroke(1.dp, CardBorder),
                                        modifier = Modifier.fillMaxWidth()
                                    ) {
                                        Text(
                                            text = "You win: $winPoints points",
                                            fontSize = 15.sp,
                                            fontWeight = FontWeight.Bold,
                                            color = Wine,
                                            modifier = Modifier.padding(12.dp)
                                        )
                                    }
                                }
                            }
                        }
                    }
                }

                GameView.BETS -> {
                    LazyColumn(
                        modifier = Modifier.fillMaxSize(),
                        contentPadding = PaddingValues(top = 12.dp, bottom = 24.dp),
                        verticalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        item {
                            Surface(
                                modifier = Modifier.fillMaxWidth(),
                                color = PanelAlt,
                                shape = RoundedCornerShape(16.dp),
                                border = androidx.compose.foundation.BorderStroke(1.dp, CardBorder)
                            ) {
                                Row(
                                    modifier = Modifier.fillMaxWidth().padding(14.dp),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Button(
                                        onClick = { currentView = GameView.MENU },
                                        colors = ButtonDefaults.buttonColors(containerColor = PanelCard),
                                        shape = RoundedCornerShape(12.dp),
                                        border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder)
                                    ) {
                                        Text("Back", color = Ink, fontWeight = FontWeight.Bold)
                                    }
                                    Text(text = "My Bets", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Ink)
                                }
                            }
                        }

                        if (state.bets.isEmpty()) {
                            item {
                                Text(text = "No entries yet.", color = MutedPurple, fontSize = 13.sp, modifier = Modifier.padding(16.dp))
                            }
                        } else {
                            items(state.bets) { item ->
                                Surface(
                                    modifier = Modifier.fillMaxWidth(),
                                    color = PanelCard,
                                    shape = RoundedCornerShape(12.dp),
                                    border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder)
                                ) {
                                    Row(modifier = Modifier.padding(12.dp), horizontalArrangement = Arrangement.SpaceBetween) {
                                        Column {
                                            Text(text = "${item.market} · ${item.game} ${item.selection}", fontWeight = FontWeight.Bold, color = Ink, fontSize = 13.sp)
                                            Text(text = "${item.date} · ${item.session}", fontSize = 11.sp, color = MutedPurple)
                                        }
                                        Column(horizontalAlignment = Alignment.End) {
                                            Text(text = item.status, fontWeight = FontWeight.Bold, color = if (item.status == "WON") GreenBadge else Wine, fontSize = 12.sp)
                                            Text(text = "${item.points} pts", fontWeight = FontWeight.SemiBold, fontSize = 12.sp, color = RedPrimary)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                GameView.RESULTS -> {
                    LazyColumn(
                        modifier = Modifier.fillMaxSize(),
                        contentPadding = PaddingValues(top = 12.dp, bottom = 24.dp),
                        verticalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        item {
                            Surface(
                                modifier = Modifier.fillMaxWidth(),
                                color = PanelAlt,
                                shape = RoundedCornerShape(16.dp),
                                border = androidx.compose.foundation.BorderStroke(1.dp, CardBorder)
                            ) {
                                Row(
                                    modifier = Modifier.fillMaxWidth().padding(14.dp),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Button(
                                        onClick = { currentView = GameView.MENU },
                                        colors = ButtonDefaults.buttonColors(containerColor = PanelCard),
                                        shape = RoundedCornerShape(12.dp),
                                        border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder)
                                    ) {
                                        Text("Back", color = Ink, fontWeight = FontWeight.Bold)
                                    }
                                    Text(text = "Results", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Ink)
                                }
                            }
                        }

                        if (state.results.isEmpty()) {
                            item {
                                Text(text = "No declared results yet.", color = MutedPurple, fontSize = 13.sp, modifier = Modifier.padding(16.dp))
                            }
                        } else {
                            items(state.results) { res ->
                                Surface(
                                    modifier = Modifier.fillMaxWidth(),
                                    color = PanelCard,
                                    shape = RoundedCornerShape(12.dp),
                                    border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder)
                                ) {
                                    Row(modifier = Modifier.padding(12.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                                        Column {
                                            Text(text = "${res.market} · ${res.date}", fontWeight = FontWeight.Bold, color = Ink, fontSize = 13.sp)
                                            Text(text = "Verified RNG", fontSize = 11.sp, color = GreenBadge, fontWeight = FontWeight.SemiBold)
                                        }
                                        Text(
                                            text = "${res.openPanna ?: "***"}-${res.jodi ?: "**"}-${res.closePanna ?: "***"}",
                                            fontWeight = FontWeight.Bold,
                                            fontSize = 15.sp,
                                            color = RedPrimary
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    if (showConfirmSheet) {
        val currentType = selectedType ?: GAME_TYPES.first()
        val pts = points.toLongOrNull() ?: 10
        val currentBal = state.user?.coinBalance ?: 0

        ModalBottomSheet(onDismissRequest = { showConfirmSheet = false }, containerColor = PanelCard) {
            Column(modifier = Modifier.fillMaxWidth().padding(20.dp)) {
                Text(text = "Confirm entry", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Ink)
                Spacer(modifier = Modifier.height(14.dp))
                DetailRow("Market", state.selectedMarket?.name.orEmpty())
                DetailRow("Date", betDate)
                DetailRow("Session", if (currentType.hasSession) betSession.replaceFirstChar { it.uppercase() } else "Open + Close")
                DetailRow("Selection", selection)
                DetailRow("Points", pts.toString())
                DetailRow("Balance after entry", (currentBal - pts).toString())

                Spacer(modifier = Modifier.height(20.dp))
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    Button(
                        onClick = { showConfirmSheet = false },
                        colors = ButtonDefaults.buttonColors(containerColor = PanelWhite),
                        shape = RoundedCornerShape(12.dp),
                        border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder),
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("Cancel", color = Ink, fontWeight = FontWeight.Bold)
                    }
                    Button(
                        onClick = {
                            viewModel.placeBet(
                                betType = currentType.code,
                                session = if (currentType.hasSession) betSession else "both",
                                selection = selection,
                                points = pts,
                                onSuccess = {
                                    showConfirmSheet = false
                                    currentView = GameView.MENU
                                }
                            )
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = RedPrimary),
                        shape = RoundedCornerShape(12.dp),
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("Confirm", color = Color.White, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}

@Composable
fun DetailRow(label: String, value: String) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(text = label, color = MutedPurple, fontSize = 13.sp)
        Text(text = value, fontWeight = FontWeight.Bold, color = Ink, fontSize = 13.sp)
    }
}

// -------------------------------------------------------------
// Wallet Screen (Tabs: Home, Activity, Passbook, Coins, Request, Support)
// -------------------------------------------------------------
@Composable
fun WalletScreen(
    state: AppState,
    viewModel: AppViewModel,
    initialTab: String = "home",
    onNavigateHome: () -> Unit,
    onLogout: () -> Unit
) {
    val context = LocalContext.current
    var selectedWalletTab by remember { mutableStateOf(initialTab) }

    var requestType by remember { mutableStateOf("credit") }
    var requestAmount by remember { mutableStateOf("") }
    var bankHolder by remember { mutableStateOf("") }
    var bankAccount by remember { mutableStateOf("") }
    var bankIfsc by remember { mutableStateOf("") }
    var requestMessage by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(initialTab) {
        selectedWalletTab = initialTab
    }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 14.dp),
        contentPadding = PaddingValues(top = 12.dp, bottom = 24.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // App Greeting & Profile Strip
        item {
            Surface(
                modifier = Modifier.fillMaxWidth(),
                color = LavenderLight,
                shape = RoundedCornerShape(14.dp),
                border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder)
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 14.dp, vertical = 10.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(text = state.user?.username ?: "Account", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Ink)
                        Text(text = state.user?.phone ?: "Signed in", fontSize = 12.sp, color = MutedPurple)
                    }
                    Button(
                        onClick = onLogout,
                        colors = ButtonDefaults.buttonColors(containerColor = RedPrimary),
                        shape = RoundedCornerShape(16.dp),
                        contentPadding = PaddingValues(horizontal = 12.dp, vertical = 4.dp),
                        modifier = Modifier.height(32.dp)
                    ) {
                        Text("Log out", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }

        // Subtabs selector
        item {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                listOf(
                    "home" to "Overview",
                    "bids" to "My Activity",
                    "passbook" to "Passbook",
                    "funds" to "Coins",
                    "fund-request" to "Request Adjustment",
                    "support" to "Support"
                ).forEach { (key, label) ->
                    val isSel = selectedWalletTab == key
                    Button(
                        onClick = { selectedWalletTab = key },
                        colors = ButtonDefaults.buttonColors(containerColor = if (isSel) RedPrimary else PanelCard),
                        shape = RoundedCornerShape(18.dp),
                        contentPadding = PaddingValues(horizontal = 12.dp, vertical = 4.dp),
                        modifier = Modifier.height(34.dp)
                    ) {
                        Text(text = label, color = if (isSel) Color.White else Ink, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }

        when (selectedWalletTab) {
            "home" -> {
                item {
                    // Balance Card
                    Surface(
                        modifier = Modifier.fillMaxWidth(),
                        color = PanelCard,
                        shape = RoundedCornerShape(16.dp),
                        shadowElevation = 5.dp
                    ) {
                        Column(modifier = Modifier.padding(18.dp)) {
                            Text(text = "VIRTUAL COIN BALANCE", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = MutedPurple)
                            Text(
                                text = "${state.user?.coinBalance ?: 0} coins",
                                fontSize = 30.sp,
                                fontWeight = FontWeight.Black,
                                color = RedPrimary
                            )
                            Text(
                                text = "Virtual coins only. No cash value, deposits, withdrawals, or payouts.",
                                fontSize = 12.sp,
                                color = MutedPurple
                            )
                        }
                    }
                }

                item {
                    // Quick Actions
                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                        ShortcutCard(
                            icon = "＋",
                            title = "Request virtual coins",
                            modifier = Modifier.weight(1f),
                            onClick = { selectedWalletTab = "fund-request" }
                        )
                        ShortcutCard(
                            icon = "◷",
                            title = "Coin history",
                            modifier = Modifier.weight(1f),
                            onClick = { selectedWalletTab = "passbook" }
                        )
                    }
                }

                item {
                    // Account details panel
                    Surface(
                        modifier = Modifier.fillMaxWidth(),
                        color = PanelAlt,
                        shape = RoundedCornerShape(14.dp),
                        border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder)
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text(text = "Account details", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Ink)
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = "${state.user?.phone ?: "Administrator account"} · Signed in",
                                fontSize = 12.sp,
                                color = MutedPurple
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = "Coin credits are added by an administrator. Keep your login password private; an admin never needs it.",
                                fontSize = 12.sp,
                                color = Ink
                            )
                        }
                    }
                }

                item {
                    // Navigation Rows
                    Surface(
                        modifier = Modifier.fillMaxWidth(),
                        color = PanelAlt,
                        shape = RoundedCornerShape(14.dp),
                        border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder)
                    ) {
                        Column {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clickable { selectedWalletTab = "passbook" }
                                    .padding(14.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Box(modifier = Modifier.size(32.dp).clip(CircleShape).background(RedPrimary), contentAlignment = Alignment.Center) {
                                    Text(text = "◷", color = Color.White, fontWeight = FontWeight.Bold)
                                }
                                Spacer(modifier = Modifier.width(10.dp))
                                Column(modifier = Modifier.weight(1f)) {
                                    Text(text = "Coin activity", fontWeight = FontWeight.Bold, fontSize = 13.sp, color = Ink)
                                    Text(text = "View credits and virtual entries", fontSize = 11.sp, color = MutedPurple)
                                }
                                Text(text = "›", color = Wine, fontSize = 20.sp)
                            }
                            Divider(color = LineBorder)
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clickable { onNavigateHome() }
                                    .padding(14.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Box(modifier = Modifier.size(32.dp).clip(CircleShape).background(RedPrimary), contentAlignment = Alignment.Center) {
                                    Text(text = "⌂", color = Color.White, fontWeight = FontWeight.Bold)
                                }
                                Spacer(modifier = Modifier.width(10.dp))
                                Column(modifier = Modifier.weight(1f)) {
                                    Text(text = "Market results", fontWeight = FontWeight.Bold, fontSize = 13.sp, color = Ink)
                                    Text(text = "Return to the results page", fontSize = 11.sp, color = MutedPurple)
                                }
                                Text(text = "›", color = Wine, fontSize = 20.sp)
                            }
                        }
                    }
                }
            }

            "bids" -> {
                item {
                    Surface(
                        modifier = Modifier.fillMaxWidth(),
                        color = PanelAlt,
                        shape = RoundedCornerShape(14.dp),
                        border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder)
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text(text = "My Activity", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Ink)
                            Text(text = "Your previous virtual-point activity appears here.", fontSize = 12.sp, color = MutedPurple)
                            Spacer(modifier = Modifier.height(12.dp))

                            val txs = state.wallet?.transactions.orEmpty()
                            if (txs.isEmpty()) {
                                Text(text = "No previous activity yet.", fontSize = 12.sp, color = MutedPurple)
                            } else {
                                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                    txs.forEach { item ->
                                        Row(
                                            modifier = Modifier
                                                .fillMaxWidth()
                                                .border(1.dp, LineBorder, RoundedCornerShape(8.dp))
                                                .padding(10.dp),
                                            horizontalArrangement = Arrangement.SpaceBetween
                                        ) {
                                            Column {
                                                Text(text = item.description, fontWeight = FontWeight.Bold, fontSize = 13.sp, color = Ink)
                                                Text(text = item.createdAt, fontSize = 11.sp, color = MutedPurple)
                                            }
                                            Column(horizontalAlignment = Alignment.End) {
                                                val isPlus = item.amountDelta > 0
                                                Text(
                                                    text = "${if (isPlus) "+" else ""}${item.amountDelta}",
                                                    fontWeight = FontWeight.Bold,
                                                    fontSize = 13.sp,
                                                    color = if (isPlus) GreenBadge else RedDeep
                                                )
                                                Text(text = "Bal: ${item.balanceAfter}", fontSize = 11.sp, color = MutedPurple)
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            "passbook" -> {
                item {
                    Surface(
                        modifier = Modifier.fillMaxWidth(),
                        color = PanelAlt,
                        shape = RoundedCornerShape(14.dp),
                        border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder)
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text(text = "Passbook", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Ink)
                            Text(text = "All virtual-point transactions, including reason and resulting balance.", fontSize = 12.sp, color = MutedPurple)
                            Spacer(modifier = Modifier.height(12.dp))

                            val txs = state.wallet?.transactions.orEmpty()
                            if (txs.isEmpty()) {
                                Text(text = "No transactions yet.", fontSize = 12.sp, color = MutedPurple)
                            } else {
                                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                    txs.forEach { item ->
                                        Surface(
                                            color = PanelCard,
                                            shape = RoundedCornerShape(10.dp),
                                            border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder)
                                        ) {
                                            Column(modifier = Modifier.fillMaxWidth().padding(10.dp)) {
                                                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                                    Text(text = item.kind.replace("_", " "), fontWeight = FontWeight.Bold, fontSize = 12.sp, color = Wine)
                                                    Text(text = item.createdAt, fontSize = 10.sp, color = MutedPurple)
                                                }
                                                Spacer(modifier = Modifier.height(4.dp))
                                                Text(text = item.description, fontSize = 12.sp, color = Ink)
                                                Spacer(modifier = Modifier.height(4.dp))
                                                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                                    val isPlus = item.amountDelta > 0
                                                    Text(
                                                        text = if (isPlus) "Credited: +${item.amountDelta}" else "Debited: ${item.amountDelta}",
                                                        fontSize = 12.sp,
                                                        fontWeight = FontWeight.Bold,
                                                        color = if (isPlus) GreenBadge else RedDeep
                                                    )
                                                    Text(text = "Balance: ${item.balanceAfter}", fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = Ink)
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            "funds" -> {
                item {
                    Surface(
                        modifier = Modifier.fillMaxWidth(),
                        color = PanelCard,
                        shape = RoundedCornerShape(16.dp),
                        shadowElevation = 4.dp
                    ) {
                        Column(modifier = Modifier.padding(18.dp)) {
                            Text(text = "Coins", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Ink)
                            Text(
                                text = "${state.user?.coinBalance ?: 0} coins",
                                fontSize = 28.sp,
                                fontWeight = FontWeight.Black,
                                color = RedPrimary
                            )
                            Text(
                                text = "Admin-granted demo credits only. No cash deposits, withdrawals, or payouts are available.",
                                fontSize = 12.sp,
                                color = MutedPurple
                            )
                        }
                    }
                }

                item {
                    Surface(
                        modifier = Modifier.fillMaxWidth(),
                        color = PanelAlt,
                        shape = RoundedCornerShape(14.dp),
                        border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder)
                    ) {
                        Column {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clickable { selectedWalletTab = "fund-request" }
                                    .padding(14.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Box(modifier = Modifier.size(32.dp).clip(CircleShape).background(RedPrimary), contentAlignment = Alignment.Center) {
                                    Text(text = "＋", color = Color.White, fontWeight = FontWeight.Bold)
                                }
                                Spacer(modifier = Modifier.width(10.dp))
                                Column(modifier = Modifier.weight(1f)) {
                                    Text(text = "Request virtual credits", fontWeight = FontWeight.Bold, fontSize = 13.sp, color = Ink)
                                    Text(text = "Send a request to support; credits are added by an admin", fontSize = 11.sp, color = MutedPurple)
                                }
                                Text(text = "›", color = Wine, fontSize = 20.sp)
                            }
                            Divider(color = LineBorder)
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clickable { selectedWalletTab = "passbook" }
                                    .padding(14.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Box(modifier = Modifier.size(32.dp).clip(CircleShape).background(RedPrimary), contentAlignment = Alignment.Center) {
                                    Text(text = "◷", color = Color.White, fontWeight = FontWeight.Bold)
                                }
                                Spacer(modifier = Modifier.width(10.dp))
                                Column(modifier = Modifier.weight(1f)) {
                                    Text(text = "Coin history", fontWeight = FontWeight.Bold, fontSize = 13.sp, color = Ink)
                                    Text(text = "Review admin credits and virtual entries", fontSize = 11.sp, color = MutedPurple)
                                }
                                Text(text = "›", color = Wine, fontSize = 20.sp)
                            }
                        }
                    }
                }
            }

            "fund-request" -> {
                item {
                    Surface(
                        modifier = Modifier.fillMaxWidth(),
                        color = PanelAlt,
                        shape = RoundedCornerShape(14.dp),
                        border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder)
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text(text = "Request a coin adjustment", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Ink)
                            Text(
                                text = "This opens WhatsApp to support with a prefilled request. Coins change only after an administrator reviews and applies it.",
                                fontSize = 12.sp,
                                color = MutedPurple
                            )
                            Spacer(modifier = Modifier.height(12.dp))

                            // Radio request type
                            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                                Surface(
                                    modifier = Modifier.weight(1f).clickable { requestType = "credit" },
                                    color = if (requestType == "credit") LavenderLight else PanelCard,
                                    shape = RoundedCornerShape(10.dp),
                                    border = androidx.compose.foundation.BorderStroke(1.dp, if (requestType == "credit") RedPrimary else LineBorder)
                                ) {
                                    Row(modifier = Modifier.padding(8.dp), verticalAlignment = Alignment.CenterVertically) {
                                        RadioButton(selected = requestType == "credit", onClick = { requestType = "credit" })
                                        Text(text = "Credit (add)", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                                    }
                                }
                                Surface(
                                    modifier = Modifier.weight(1f).clickable { requestType = "withdrawal" },
                                    color = if (requestType == "withdrawal") LavenderLight else PanelCard,
                                    shape = RoundedCornerShape(10.dp),
                                    border = androidx.compose.foundation.BorderStroke(1.dp, if (requestType == "withdrawal") RedPrimary else LineBorder)
                                ) {
                                    Row(modifier = Modifier.padding(8.dp), verticalAlignment = Alignment.CenterVertically) {
                                        RadioButton(selected = requestType == "withdrawal", onClick = { requestType = "withdrawal" })
                                        Text(text = "Withdrawal", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                                    }
                                }
                            }

                            Spacer(modifier = Modifier.height(10.dp))
                            Text("Coins Amount", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = Ink)
                            OutlinedTextField(
                                value = requestAmount,
                                onValueChange = { requestAmount = it.filter { ch -> ch.isDigit() } },
                                placeholder = { Text(if (requestType == "credit") "Min 500" else "Min 1,000") },
                                modifier = Modifier.fillMaxWidth(),
                                shape = RoundedCornerShape(12.dp),
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
                            )

                            if (requestType == "withdrawal") {
                                Spacer(modifier = Modifier.height(8.dp))
                                Text("Full Name", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = Ink)
                                OutlinedTextField(
                                    value = bankHolder,
                                    onValueChange = { bankHolder = it },
                                    placeholder = { Text("Account holder name") },
                                    modifier = Modifier.fillMaxWidth(),
                                    shape = RoundedCornerShape(12.dp)
                                )
                                Spacer(modifier = Modifier.height(8.dp))
                                Text("Bank Account Number", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = Ink)
                                OutlinedTextField(
                                    value = bankAccount,
                                    onValueChange = { bankAccount = it },
                                    placeholder = { Text("Bank account number") },
                                    modifier = Modifier.fillMaxWidth(),
                                    shape = RoundedCornerShape(12.dp)
                                )
                                Spacer(modifier = Modifier.height(8.dp))
                                Text("IFSC Code", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = Ink)
                                OutlinedTextField(
                                    value = bankIfsc,
                                    onValueChange = { bankIfsc = it.uppercase() },
                                    placeholder = { Text("IFSC code") },
                                    modifier = Modifier.fillMaxWidth(),
                                    shape = RoundedCornerShape(12.dp)
                                )
                            }

                            if (!requestMessage.isNullOrBlank()) {
                                Spacer(modifier = Modifier.height(6.dp))
                                Text(text = requestMessage.orEmpty(), fontSize = 12.sp, color = RedDeep)
                            }

                            Spacer(modifier = Modifier.height(14.dp))
                            Button(
                                onClick = {
                                    val amt = requestAmount.toLongOrNull() ?: 0
                                    val user = state.user
                                    if (user == null) {
                                        requestMessage = "Please log in again before sending a request."
                                        return@Button
                                    }
                                    if (requestType == "credit" && amt < 500) {
                                        requestMessage = "Minimum credit request is 500 coins."
                                        return@Button
                                    }
                                    if (requestType == "withdrawal" && amt < 1000) {
                                        requestMessage = "Minimum withdrawal request is 1,000 coins."
                                        return@Button
                                    }

                                    val whatsappText = if (requestType == "withdrawal") {
                                        "Withdrawal request\nName: ${bankHolder.ifBlank { user.username }}\nAmount: $amt coins\nAccount: ${bankAccount.ifBlank { "Not provided" }}\nIFSC: ${bankIfsc.ifBlank { "Not provided" }}\nUser ID: ${user.username}"
                                    } else {
                                        "Credit request\nUser: ${user.username}\nUser ID: ${user.username}\nAmount: $amt coins\nPlease review and process this request."
                                    }

                                    if (requestType == "credit") {
                                        viewModel.requestCredit(amt) {
                                            val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://wa.me/918699915927?text=${Uri.encode(whatsappText)}"))
                                            try { context.startActivity(intent) } catch (_: Exception) {}
                                            requestMessage = "Request saved. WhatsApp is opening for confirmation."
                                        }
                                    } else {
                                        viewModel.requestWithdrawal(amt, bankHolder, bankAccount, bankIfsc) {
                                            val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://wa.me/918699915927?text=${Uri.encode(whatsappText)}"))
                                            try { context.startActivity(intent) } catch (_: Exception) {}
                                            requestMessage = "Request saved. WhatsApp is opening for confirmation."
                                        }
                                    }
                                },
                                colors = ButtonDefaults.buttonColors(containerColor = RedPrimary),
                                shape = RoundedCornerShape(20.dp),
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Text("Send request on WhatsApp · 8699915927", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 13.sp)
                            }
                        }
                    }
                }
            }

            "support" -> {
                item {
                    Surface(
                        modifier = Modifier.fillMaxWidth(),
                        color = PanelAlt,
                        shape = RoundedCornerShape(14.dp),
                        border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder)
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text(text = "Support", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Ink)
                            Text(
                                text = "Chat about your DhanRAJ account. Your username and phone number are included in the prefilled message. Never send anyone your password.",
                                fontSize = 12.sp,
                                color = MutedPurple
                            )
                            Spacer(modifier = Modifier.height(14.dp))

                            ShortcutCard(
                                icon = "◉",
                                title = "WhatsApp support · 8699915927",
                                modifier = Modifier.fillMaxWidth(),
                                onClick = {
                                    val user = state.user
                                    val identity = if (user != null) {
                                        "Hello, I need help with my DhanRAJ account.\nUsername: ${user.username}\nPhone: ${user.phone ?: "Not provided"}\nRequest: Please help me with my account or service issue."
                                    } else {
                                        "Hello, I need help with my DhanRAJ account."
                                    }
                                    val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://wa.me/918699915927?text=${Uri.encode(identity)}"))
                                    try { context.startActivity(intent) } catch (_: Exception) { viewModel.showNotice("WhatsApp not available.") }
                                }
                            )

                            Spacer(modifier = Modifier.height(10.dp))
                            Text(text = "Support cannot process cash deposits or withdrawals.", fontSize = 11.sp, color = MutedPurple)
                        }
                    }
                }
            }
        }
    }
}

// -------------------------------------------------------------
// Auth Screens (Login & Register)
// -------------------------------------------------------------
@Composable
fun LoginScreen(
    state: AppState,
    viewModel: AppViewModel,
    onSuccess: () -> Unit,
    onNavigateRegister: () -> Unit
) {
    var identifier by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        contentAlignment = Alignment.Center
    ) {
        Surface(
            modifier = Modifier.fillMaxWidth(),
            color = Lavender,
            shape = RoundedCornerShape(18.dp),
            border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder),
            shadowElevation = 8.dp
        ) {
            Column(
                modifier = Modifier.padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(text = "Log in to your account", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Ink)
                Spacer(modifier = Modifier.height(18.dp))

                OutlinedTextField(
                    value = identifier,
                    onValueChange = { identifier = it },
                    placeholder = { Text("Username or phone number") },
                    leadingIcon = { Text("●", color = RedPrimary, fontWeight = FontWeight.Bold) },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedContainerColor = PanelWhite,
                        unfocusedContainerColor = PanelWhite
                    )
                )

                Spacer(modifier = Modifier.height(12.dp))

                OutlinedTextField(
                    value = password,
                    onValueChange = { password = it },
                    placeholder = { Text("Password") },
                    leadingIcon = { Text("◆", color = Wine, fontWeight = FontWeight.Bold) },
                    visualTransformation = PasswordVisualTransformation(),
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedContainerColor = PanelWhite,
                        unfocusedContainerColor = PanelWhite
                    )
                )

                if (!state.error.isNullOrBlank()) {
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(text = state.error.orEmpty(), color = RedDeep, fontSize = 12.sp)
                }

                Spacer(modifier = Modifier.height(20.dp))

                Button(
                    onClick = {
                        viewModel.clearError()
                        viewModel.login(identifier, password, onSuccess)
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = RedPrimary),
                    shape = RoundedCornerShape(24.dp),
                    modifier = Modifier
                        .width(160.dp)
                        .height(46.dp)
                ) {
                    Text(text = "LOGIN", color = Color.White, fontWeight = FontWeight.Bold)
                }

                Spacer(modifier = Modifier.height(14.dp))

                Row {
                    Text(text = "Don't have an account? ", fontSize = 13.sp, color = Ink)
                    Text(
                        text = "Register now",
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Bold,
                        color = Wine,
                        modifier = Modifier.clickable { onNavigateRegister() }
                    )
                }

                Spacer(modifier = Modifier.height(10.dp))
                Text(
                    text = "Your password is private. Administrators can grant coins without seeing your login credentials.",
                    fontSize = 11.sp,
                    color = MutedPurple,
                    textAlign = TextAlign.Center
                )
            }
        }
    }
}

@Composable
fun RegisterScreen(
    state: AppState,
    viewModel: AppViewModel,
    onSuccess: () -> Unit,
    onNavigateLogin: () -> Unit
) {
    var username by remember { mutableStateOf("") }
    var phone by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var termsAgreed by remember { mutableStateOf(false) }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        contentAlignment = Alignment.Center
    ) {
        Surface(
            modifier = Modifier.fillMaxWidth(),
            color = Lavender,
            shape = RoundedCornerShape(18.dp),
            border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder),
            shadowElevation = 8.dp
        ) {
            Column(
                modifier = Modifier.padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(text = "Create your account", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Ink)
                Spacer(modifier = Modifier.height(18.dp))

                OutlinedTextField(
                    value = username,
                    onValueChange = { username = it },
                    placeholder = { Text("Username") },
                    leadingIcon = { Text("●", color = RedPrimary, fontWeight = FontWeight.Bold) },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedContainerColor = PanelWhite,
                        unfocusedContainerColor = PanelWhite
                    )
                )

                Spacer(modifier = Modifier.height(10.dp))

                OutlinedTextField(
                    value = phone,
                    onValueChange = { phone = it },
                    placeholder = { Text("Mobile number") },
                    leadingIcon = { Text("▯", color = Wine, fontWeight = FontWeight.Bold) },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedContainerColor = PanelWhite,
                        unfocusedContainerColor = PanelWhite
                    )
                )

                Spacer(modifier = Modifier.height(10.dp))

                OutlinedTextField(
                    value = password,
                    onValueChange = { password = it },
                    placeholder = { Text("Password (at least 12 characters)") },
                    leadingIcon = { Text("◆", color = Wine, fontWeight = FontWeight.Bold) },
                    visualTransformation = PasswordVisualTransformation(),
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedContainerColor = PanelWhite,
                        unfocusedContainerColor = PanelWhite
                    )
                )

                Spacer(modifier = Modifier.height(10.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Checkbox(
                        checked = termsAgreed,
                        onCheckedChange = { termsAgreed = it },
                        colors = CheckboxDefaults.colors(checkedColor = RedPrimary)
                    )
                    Text(
                        text = "I agree: Virtual points only. No real money. For entertainment.",
                        fontSize = 11.sp,
                        color = Ink
                    )
                }

                if (!state.error.isNullOrBlank()) {
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(text = state.error.orEmpty(), color = RedDeep, fontSize = 12.sp)
                }

                Spacer(modifier = Modifier.height(16.dp))

                Button(
                    onClick = {
                        if (!termsAgreed) {
                            viewModel.showNotice("Please accept terms.")
                            return@Button
                        }
                        if (password.length < 12) {
                            viewModel.showNotice("Password must be at least 12 characters.")
                            return@Button
                        }
                        viewModel.clearError()
                        viewModel.register(username, phone, password, onSuccess)
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = RedPrimary),
                    shape = RoundedCornerShape(24.dp),
                    modifier = Modifier
                        .width(160.dp)
                        .height(46.dp)
                ) {
                    Text(text = "REGISTER", color = Color.White, fontWeight = FontWeight.Bold)
                }

                Spacer(modifier = Modifier.height(14.dp))

                Row {
                    Text(text = "Already have an account? ", fontSize = 13.sp, color = Ink)
                    Text(
                        text = "Log in",
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Bold,
                        color = Wine,
                        modifier = Modifier.clickable { onNavigateLogin() }
                    )
                }

                Spacer(modifier = Modifier.height(10.dp))
                Text(
                    text = "Phone ownership is not verified. Use a number you control. Never share your password.",
                    fontSize = 11.sp,
                    color = MutedPurple,
                    textAlign = TextAlign.Center
                )
            }
        }
    }
}

// -------------------------------------------------------------
// Admin Screen
// -------------------------------------------------------------
@Composable
fun AdminScreen(
    state: AppState,
    viewModel: AppViewModel,
    onNavigateWallet: () -> Unit,
    onLogout: () -> Unit
) {
    var adminTab by remember { mutableStateOf("credit_requests") }

    // Change password form
    var curPass by remember { mutableStateOf("") }
    var newPass by remember { mutableStateOf("") }

    // Coin Adjust form
    var adjUser by remember { mutableStateOf("") }
    var adjPhone by remember { mutableStateOf("") }
    var adjAmount by remember { mutableStateOf("") }

    // Declare Result form
    var decRoundId by remember { mutableStateOf("") }
    var decSession by remember { mutableStateOf("open") }
    var decPanna by remember { mutableStateOf("") }

    // Market Schedule form
    var mktName by remember { mutableStateOf("") }
    var mktOpen by remember { mutableStateOf("10:00") }
    var mktClose by remember { mutableStateOf("23:00") }
    var mktDays by remember { mutableStateOf("0,1,2,3,4,5,6") }
    var mktCutoff by remember { mutableStateOf("10") }
    var mktPaused by remember { mutableStateOf(false) }
    var mktSort by remember { mutableStateOf("0") }

    // Win Rate form
    var rateCode by remember { mutableStateOf("SINGLE_DIGIT") }
    var rateWin by remember { mutableStateOf("95") }
    var rateMin by remember { mutableStateOf("10") }
    var rateMax by remember { mutableStateOf("100000") }
    var rateEnabled by remember { mutableStateOf(true) }

    LaunchedEffect(Unit) {
        viewModel.loadAdminRequests()
    }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 14.dp),
        contentPadding = PaddingValues(top = 12.dp, bottom = 24.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Admin Profile Top
        item {
            Surface(
                modifier = Modifier.fillMaxWidth(),
                color = LavenderLight,
                shape = RoundedCornerShape(14.dp),
                border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder)
            ) {
                Row(
                    modifier = Modifier.padding(14.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(text = "Signed in as ${state.user?.username ?: "Admin"}", fontWeight = FontWeight.Bold, color = Ink)
                    Button(
                        onClick = onLogout,
                        colors = ButtonDefaults.buttonColors(containerColor = RedPrimary),
                        shape = RoundedCornerShape(14.dp),
                        contentPadding = PaddingValues(horizontal = 10.dp, vertical = 2.dp),
                        modifier = Modifier.height(30.dp)
                    ) {
                        Text("Log out", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }

        // Must change password section
        if (state.user?.mustChangePassword == true) {
            item {
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    color = PanelAlt,
                    shape = RoundedCornerShape(14.dp),
                    border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(text = "Update administrator password", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = RedDeep)
                        Text(text = "Choose a new password of at least 12 characters before using admin tools.", fontSize = 12.sp, color = MutedPurple)
                        Spacer(modifier = Modifier.height(10.dp))

                        OutlinedTextField(
                            value = curPass,
                            onValueChange = { curPass = it },
                            label = { Text("Current password") },
                            visualTransformation = PasswordVisualTransformation(),
                            modifier = Modifier.fillMaxWidth()
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        OutlinedTextField(
                            value = newPass,
                            onValueChange = { newPass = it },
                            label = { Text("New password (min 12 chars)") },
                            visualTransformation = PasswordVisualTransformation(),
                            modifier = Modifier.fillMaxWidth()
                        )
                        Spacer(modifier = Modifier.height(12.dp))
                        Button(
                            onClick = { viewModel.changePassword(curPass, newPass) {} },
                            colors = ButtonDefaults.buttonColors(containerColor = RedPrimary),
                            shape = RoundedCornerShape(20.dp)
                        ) {
                            Text("Change password", color = Color.White, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        } else {
            // Admin Tabs selector
            item {
                Row(
                    modifier = Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    listOf(
                        "credit_requests" to "Credit Requests",
                        "withdraw_requests" to "Withdraw Requests",
                        "grant_coins" to "Grant/Debit Coins",
                        "declare_result" to "Declare Result",
                        "market_schedule" to "Market Schedule",
                        "win_rates" to "Win Rates"
                    ).forEach { (key, label) ->
                        val isSel = adminTab == key
                        Button(
                            onClick = {
                                adminTab = key
                                if (key in listOf("credit_requests", "withdraw_requests")) {
                                    viewModel.loadAdminRequests()
                                }
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = if (isSel) RedPrimary else PanelCard),
                            shape = RoundedCornerShape(16.dp),
                            contentPadding = PaddingValues(horizontal = 12.dp, vertical = 4.dp),
                            modifier = Modifier.height(34.dp)
                        ) {
                            Text(text = label, color = if (isSel) Color.White else Ink, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }

            when (adminTab) {
                "credit_requests", "withdraw_requests" -> {
                    val filterType = if (adminTab == "credit_requests") "credit" else "withdrawal"
                    val filtered = state.adminRequests.filter { it.type == filterType }

                    item {
                        Text(
                            text = if (filterType == "credit") "Pending Credit Requests" else "Pending Withdrawal Requests",
                            fontSize = 16.sp,
                            fontWeight = FontWeight.Bold,
                            color = Ink
                        )
                    }

                    if (filtered.isEmpty()) {
                        item {
                            Text(text = "No requests found.", color = MutedPurple, fontSize = 13.sp)
                        }
                    } else {
                        items(filtered) { req ->
                            Surface(
                                modifier = Modifier.fillMaxWidth(),
                                color = PanelCard,
                                shape = RoundedCornerShape(12.dp),
                                border = androidx.compose.foundation.BorderStroke(1.dp, CardBorder)
                            ) {
                                Column(modifier = Modifier.padding(12.dp)) {
                                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                        Text(text = req.userName, fontWeight = FontWeight.Bold, color = Ink)
                                        Text(text = "${req.amount} coins", fontWeight = FontWeight.Bold, color = RedPrimary)
                                    }
                                    if (req.type == "withdrawal") {
                                        Text(text = "Holder: ${req.accountHolderName.orEmpty()}", fontSize = 11.sp, color = MutedPurple)
                                        Text(text = "Account: ${req.bankAccountNumber.orEmpty()} · IFSC: ${req.ifscCode.orEmpty()}", fontSize = 11.sp, color = MutedPurple)
                                    }
                                    Text(text = "Status: ${req.status}", fontSize = 11.sp, color = if (req.status == "APPROVED") GreenBadge else RedDeep)
                                    Spacer(modifier = Modifier.height(8.dp))
                                    if (req.status == "PENDING") {
                                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                            Button(
                                                onClick = { viewModel.approveRequest(req.id) },
                                                colors = ButtonDefaults.buttonColors(containerColor = GreenBadge),
                                                shape = RoundedCornerShape(14.dp),
                                                modifier = Modifier.height(30.dp),
                                                contentPadding = PaddingValues(horizontal = 10.dp, vertical = 2.dp)
                                            ) {
                                                Text("Approve", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                                            }
                                            Button(
                                                onClick = { viewModel.rejectRequest(req.id) },
                                                colors = ButtonDefaults.buttonColors(containerColor = RedDeep),
                                                shape = RoundedCornerShape(14.dp),
                                                modifier = Modifier.height(30.dp),
                                                contentPadding = PaddingValues(horizontal = 10.dp, vertical = 2.dp)
                                            ) {
                                                Text("Reject", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                "grant_coins" -> {
                    item {
                        Surface(
                            modifier = Modifier.fillMaxWidth(),
                            color = PanelAlt,
                            shape = RoundedCornerShape(14.dp),
                            border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder)
                        ) {
                            Column(modifier = Modifier.padding(16.dp)) {
                                Text(text = "Grant virtual coins", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Ink)
                                OutlinedTextField(value = adjUser, onValueChange = { adjUser = it }, label = { Text("Username") }, modifier = Modifier.fillMaxWidth())
                                Spacer(modifier = Modifier.height(6.dp))
                                OutlinedTextField(value = adjPhone, onValueChange = { adjPhone = it }, label = { Text("Phone") }, modifier = Modifier.fillMaxWidth())
                                Spacer(modifier = Modifier.height(6.dp))
                                OutlinedTextField(value = adjAmount, onValueChange = { adjAmount = it.filter { ch -> ch.isDigit() } }, label = { Text("Coins Amount") }, modifier = Modifier.fillMaxWidth())
                                Spacer(modifier = Modifier.height(10.dp))
                                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                                    Button(
                                        onClick = {
                                            val amt = adjAmount.toLongOrNull() ?: 0
                                            viewModel.adminCredit(adjUser, adjPhone, amt) {}
                                        },
                                        colors = ButtonDefaults.buttonColors(containerColor = GreenBadge),
                                        shape = RoundedCornerShape(18.dp)
                                    ) {
                                        Text("Add Coins", fontWeight = FontWeight.Bold)
                                    }
                                    Button(
                                        onClick = {
                                            val amt = adjAmount.toLongOrNull() ?: 0
                                            viewModel.adminDebit(adjUser, adjPhone, amt) {}
                                        },
                                        colors = ButtonDefaults.buttonColors(containerColor = RedDeep),
                                        shape = RoundedCornerShape(18.dp)
                                    ) {
                                        Text("Debit Coins", fontWeight = FontWeight.Bold)
                                    }
                                }
                            }
                        }
                    }
                }

                "declare_result" -> {
                    item {
                        Surface(
                            modifier = Modifier.fillMaxWidth(),
                            color = PanelAlt,
                            shape = RoundedCornerShape(14.dp),
                            border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder)
                        ) {
                            Column(modifier = Modifier.padding(16.dp)) {
                                Text(text = "Declare Game Result", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Ink)
                                Spacer(modifier = Modifier.height(8.dp))
                                OutlinedTextField(value = decRoundId, onValueChange = { decRoundId = it.filter { ch -> ch.isDigit() } }, label = { Text("Round ID") }, modifier = Modifier.fillMaxWidth())
                                Spacer(modifier = Modifier.height(6.dp))
                                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                    Button(
                                        onClick = { decSession = "open" },
                                        colors = ButtonDefaults.buttonColors(containerColor = if (decSession == "open") RedPrimary else PanelCard)
                                    ) {
                                        Text("Open", color = if (decSession == "open") Color.White else Ink)
                                    }
                                    Button(
                                        onClick = { decSession = "close" },
                                        colors = ButtonDefaults.buttonColors(containerColor = if (decSession == "close") RedPrimary else PanelCard)
                                    ) {
                                        Text("Close", color = if (decSession == "close") Color.White else Ink)
                                    }
                                }
                                Spacer(modifier = Modifier.height(6.dp))
                                OutlinedTextField(value = decPanna, onValueChange = { decPanna = it.filter { ch -> ch.isDigit() }.take(3) }, label = { Text("3-Digit Panna") }, modifier = Modifier.fillMaxWidth())
                                Spacer(modifier = Modifier.height(10.dp))
                                Button(
                                    onClick = {
                                        val rid = decRoundId.toIntOrNull() ?: 0
                                        viewModel.declareRoundResult(rid, decSession, decPanna) {}
                                    },
                                    colors = ButtonDefaults.buttonColors(containerColor = RedPrimary),
                                    shape = RoundedCornerShape(20.dp)
                                ) {
                                    Text("Declare Result", fontWeight = FontWeight.Bold)
                                }
                            }
                        }
                    }
                }

                "market_schedule" -> {
                    item {
                        Surface(
                            modifier = Modifier.fillMaxWidth(),
                            color = PanelAlt,
                            shape = RoundedCornerShape(14.dp),
                            border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder)
                        ) {
                            Column(modifier = Modifier.padding(16.dp)) {
                                Text(text = "Market Schedule", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Ink)
                                Spacer(modifier = Modifier.height(8.dp))
                                OutlinedTextField(value = mktName, onValueChange = { mktName = it }, label = { Text("Market Name") }, modifier = Modifier.fillMaxWidth())
                                Spacer(modifier = Modifier.height(6.dp))
                                OutlinedTextField(value = mktOpen, onValueChange = { mktOpen = it }, label = { Text("Open Time (HH:MM)") }, modifier = Modifier.fillMaxWidth())
                                Spacer(modifier = Modifier.height(6.dp))
                                OutlinedTextField(value = mktClose, onValueChange = { mktClose = it }, label = { Text("Close Time (HH:MM)") }, modifier = Modifier.fillMaxWidth())
                                Spacer(modifier = Modifier.height(6.dp))
                                OutlinedTextField(value = mktDays, onValueChange = { mktDays = it }, label = { Text("Active Days (0,1,2,3,4,5,6)") }, modifier = Modifier.fillMaxWidth())
                                Spacer(modifier = Modifier.height(6.dp))
                                OutlinedTextField(value = mktCutoff, onValueChange = { mktCutoff = it.filter { ch -> ch.isDigit() } }, label = { Text("Cutoff Minutes") }, modifier = Modifier.fillMaxWidth())
                                Spacer(modifier = Modifier.height(10.dp))
                                Button(
                                    onClick = {
                                        val daysList = mktDays.split(",").mapNotNull { it.trim().toIntOrNull() }
                                        val cutoffInt = mktCutoff.toIntOrNull() ?: 10
                                        val sortInt = mktSort.toIntOrNull() ?: 0
                                        viewModel.saveMarket(null, mktName, mktOpen, mktClose, daysList, cutoffInt, mktPaused, sortInt) {}
                                    },
                                    colors = ButtonDefaults.buttonColors(containerColor = RedPrimary),
                                    shape = RoundedCornerShape(20.dp)
                                ) {
                                    Text("Create Market", fontWeight = FontWeight.Bold)
                                }
                            }
                        }
                    }
                }

                "win_rates" -> {
                    item {
                        Surface(
                            modifier = Modifier.fillMaxWidth(),
                            color = PanelAlt,
                            shape = RoundedCornerShape(14.dp),
                            border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder)
                        ) {
                            Column(modifier = Modifier.padding(16.dp)) {
                                Text(text = "Win Rates Configuration", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Ink)
                                Spacer(modifier = Modifier.height(8.dp))
                                OutlinedTextField(value = rateCode, onValueChange = { rateCode = it.uppercase() }, label = { Text("Game Code") }, modifier = Modifier.fillMaxWidth())
                                Spacer(modifier = Modifier.height(6.dp))
                                OutlinedTextField(value = rateWin, onValueChange = { rateWin = it.filter { ch -> ch.isDigit() } }, label = { Text("Win per 10 points") }, modifier = Modifier.fillMaxWidth())
                                Spacer(modifier = Modifier.height(6.dp))
                                OutlinedTextField(value = rateMin, onValueChange = { rateMin = it.filter { ch -> ch.isDigit() } }, label = { Text("Min points") }, modifier = Modifier.fillMaxWidth())
                                Spacer(modifier = Modifier.height(6.dp))
                                OutlinedTextField(value = rateMax, onValueChange = { rateMax = it.filter { ch -> ch.isDigit() } }, label = { Text("Max points") }, modifier = Modifier.fillMaxWidth())
                                Spacer(modifier = Modifier.height(10.dp))
                                Button(
                                    onClick = {
                                        val w = rateWin.toLongOrNull() ?: 95
                                        val minP = rateMin.toLongOrNull() ?: 10
                                        val maxP = rateMax.toLongOrNull() ?: 100000
                                        viewModel.saveBetType(rateCode, w, minP, maxP, rateEnabled) {}
                                    },
                                    colors = ButtonDefaults.buttonColors(containerColor = RedPrimary),
                                    shape = RoundedCornerShape(20.dp)
                                ) {
                                    Text("Save Win Rate", fontWeight = FontWeight.Bold)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

// -------------------------------------------------------------
// Global Components (Toast & Dialog)
// -------------------------------------------------------------
@Composable
fun GlobalToast(message: String?, onDismiss: () -> Unit) {
    AnimatedVisibility(visible = !message.isNullOrBlank(), enter = fadeIn(), exit = fadeOut()) {
        Box(
            modifier = Modifier.fillMaxSize().padding(bottom = 75.dp),
            contentAlignment = Alignment.BottomCenter
        ) {
            Surface(
                color = Ink,
                shape = RoundedCornerShape(12.dp),
                shadowElevation = 8.dp,
                modifier = Modifier.padding(horizontal = 24.dp).clickable { onDismiss() }
            ) {
                Text(
                    text = message.orEmpty(),
                    color = Color.White,
                    fontSize = 13.sp,
                    fontWeight = FontWeight.Medium,
                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp)
                )
            }
        }
    }
}

@Composable
fun RegistrationResultDialog(result: Pair<Boolean, String>?, onDismiss: (Boolean) -> Unit) {
    if (result == null) return
    val (success, detail) = result

    Dialog(onDismissRequest = { onDismiss(success) }) {
        Surface(
            shape = RoundedCornerShape(18.dp),
            color = PanelWhite,
            border = androidx.compose.foundation.BorderStroke(1.dp, LineBorder),
            shadowElevation = 12.dp,
            modifier = Modifier.fillMaxWidth().padding(16.dp)
        ) {
            Column(modifier = Modifier.padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    text = if (success) "Registration successful" else "Registration unsuccessful",
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold,
                    color = if (success) GreenBadge else RedDeep
                )
                Spacer(modifier = Modifier.height(12.dp))
                Text(text = detail, fontSize = 14.sp, color = MutedPurple, lineHeight = 20.sp)
                Spacer(modifier = Modifier.height(20.dp))
                Button(
                    onClick = { onDismiss(success) },
                    colors = ButtonDefaults.buttonColors(containerColor = RedPrimary),
                    shape = RoundedCornerShape(20.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(text = if (success) "Continue to login" else "Close", color = Color.White, fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}
