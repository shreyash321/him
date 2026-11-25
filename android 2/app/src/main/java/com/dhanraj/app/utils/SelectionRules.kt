package com.dhanraj.app.utils

fun isValidPanna(value: String, code: String): Boolean {
    if (!value.matches(Regex("[0-9]{3}"))) return false
    val rank = "1234567890"
    val sorted = value.toList().sortedBy { rank.indexOf(it) }.joinToString("")
    val counts = value.groupingBy { it }.eachCount().values
    return when (code) {
        "SINGLE_PANNA" -> value == sorted && counts.size == 3
        "DOUBLE_PANNA" -> value == sorted && counts.sorted() == listOf(1, 2)
        "TRIPLE_PANNA" -> counts.size == 1
        else -> false
    }
}