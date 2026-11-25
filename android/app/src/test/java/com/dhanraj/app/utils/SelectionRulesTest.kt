package com.dhanraj.app.utils

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class SelectionRulesTest {
    @Test
    fun acceptsCanonicalSinglePanna() {
        assertTrue(isValidPanna("123", "SINGLE_PANNA"))
        assertTrue(isValidPanna("120", "SINGLE_PANNA"))
    }

    @Test
    fun rejectsNonCanonicalOrRepeatedSinglePanna() {
        assertFalse(isValidPanna("102", "SINGLE_PANNA"))
        assertFalse(isValidPanna("112", "SINGLE_PANNA"))
        assertFalse(isValidPanna("12", "SINGLE_PANNA"))
    }

    @Test
    fun acceptsOnlyCanonicalDoublePanna() {
        assertTrue(isValidPanna("112", "DOUBLE_PANNA"))
        assertFalse(isValidPanna("121", "DOUBLE_PANNA"))
        assertFalse(isValidPanna("111", "DOUBLE_PANNA"))
    }

    @Test
    fun acceptsTriplePanna() {
        assertTrue(isValidPanna("000", "TRIPLE_PANNA"))
        assertFalse(isValidPanna("001", "TRIPLE_PANNA"))
    }
}