package com.dhanraj.app.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color

val Ink = Color(0xFF351538)
val Wine = Color(0xFF60132F)
val WineDeep = Color(0xFF350D26)
val RedPrimary = Color(0xFFE73550)
val RedDeep = Color(0xFFBD203F)
val Lavender = Color(0xFFE8C9FF)
val LavenderLight = Color(0xFFF3E5FF)
val LavenderBgStart = Color(0xFFD9B5F0)
val LavenderBgMiddle = Color(0xFFF1E2FC)
val LavenderBgEnd = Color(0xFFD1A9EA)
val PanelWhite = Color(0xFFF8F2FF)
val PanelAlt = Color(0xFFF5E8FF)
val PanelCard = Color(0xFFFFF8FF)
val CardBorder = Color(0xFFCBA4E6)
val LineBorder = Color(0xFFD3B3E8)
val MutedPurple = Color(0xFF806B8E)
val TextDark = Color(0xFF1F2937)
val LogoRed = Color(0xFFDC2626)

val GreenBadge = Color(0xFF27984E)
val GreenBadgeBg = Color(0xFFDCF4E3)
val ClosedBadgeBg = Color(0xFFD7D4DA)
val ClosedBadgeText = Color(0xFF626068)

val WebsiteBackgroundBrush = Brush.linearGradient(
    colors = listOf(LavenderBgStart, LavenderBgMiddle, LavenderBgEnd)
)

val CtaButtonBrush = Brush.linearGradient(
    colors = listOf(Color(0xFFD43D5D), Color(0xFFE73550), Color(0xFFA51A39))
)

private val LightColorScheme = lightColorScheme(
    primary = RedPrimary,
    onPrimary = Color.White,
    primaryContainer = LavenderLight,
    onPrimaryContainer = Ink,
    secondary = Wine,
    onSecondary = Color.White,
    secondaryContainer = Lavender,
    onSecondaryContainer = WineDeep,
    background = LavenderBgMiddle,
    onBackground = Ink,
    surface = PanelWhite,
    onSurface = Ink,
    surfaceVariant = PanelAlt,
    onSurfaceVariant = MutedPurple,
    outline = LineBorder,
    error = RedDeep,
    onError = Color.White
)

@Composable
fun DhanRajTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = LightColorScheme,
        content = content
    )
}
