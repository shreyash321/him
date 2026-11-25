from collections import Counter

from app.game_rules import (
    bet_matches,
    calculate_digit,
    calculate_payout,
    panna_matches,
    panna_rows,
)


def test_seeded_panna_table_has_correct_counts_and_derived_digits():
    rows = panna_rows()

    assert len(rows) == 220
    assert Counter(kind for _, kind, _ in rows) == {
        "single": 120,
        "double": 90,
        "triple": 10,
    }
    assert len({panna for panna, _, _ in rows}) == 220
    assert all(calculate_digit(panna) == digit for panna, _, digit in rows)


def test_digit_and_panna_order_validation():
    assert calculate_digit("677") == 0
    assert panna_matches("560", "single")
    assert panna_matches("112", "double")
    assert panna_matches("000", "triple")
    assert not panna_matches("056", "single")
    assert not panna_matches("821", "single")
    assert not panna_matches("111", "single")


def test_virtual_game_payout_and_matching_rules():
    assert calculate_payout(10, 95) == 95
    assert calculate_payout(13, 95) == 123
    assert bet_matches(
        code="JODI",
        selection="15",
        session="both",
        open_panna="128",
        open_digit=1,
        close_panna="456",
        close_digit=5,
    )
    assert bet_matches(
        code="SINGLE_PANNA",
        selection="128",
        session="open",
        open_panna="128",
        open_digit=1,
        close_panna="456",
        close_digit=5,
    )
    assert not bet_matches(
        code="SINGLE_DIGIT",
        selection="7",
        session="open",
        open_panna="128",
        open_digit=1,
        close_panna="456",
        close_digit=5,
    )
