from itertools import combinations


PAYOUTS_PER_10 = {
    "SINGLE_DIGIT": 95,
    "JODI": 900,
    "SINGLE_PANNA": 1400,
    "DOUBLE_PANNA": 2800,
    "TRIPLE_PANNA": 7000,
}


def panna_rows() -> list[tuple[str, str, int]]:
    order = "1234567890"
    rank = {digit: index for index, digit in enumerate(order)}
    rows = []
    for digits in combinations(order, 3):
        panna = "".join(sorted(digits, key=rank.__getitem__))
        rows.append((panna, "single", calculate_digit(panna)))
    for repeated in order:
        for other in order:
            if other == repeated:
                continue
            panna = "".join(sorted((repeated, repeated, other), key=rank.__getitem__))
            rows.append((panna, "double", calculate_digit(panna)))
    for digit in order:
        panna = digit * 3
        rows.append((panna, "triple", calculate_digit(panna)))
    return rows


def calculate_digit(panna: str) -> int:
    if len(panna) != 3 or not panna.isdigit():
        raise ValueError("A panna must contain exactly three digits.")
    return sum(int(digit) for digit in panna) % 10


def calculate_payout(points: int, win_per_10: int) -> int:
    return points * win_per_10 // 10


def panna_matches(selection: str, kind: str) -> bool:
    digits = list(selection)
    if len(digits) != 3 or not selection.isdigit():
        return False
    order = "1234567890"
    rank = {digit: index for index, digit in enumerate(order)}
    if digits != sorted(digits, key=rank.__getitem__):
        return False
    counts = {digit: digits.count(digit) for digit in set(digits)}
    if kind == "single":
        return len(counts) == 3
    if kind == "double":
        return sorted(counts.values()) == [1, 2]
    if kind == "triple":
        return len(counts) == 1
    return False


def bet_matches(
    *,
    code: str,
    selection: str,
    session: str,
    open_panna: str | None,
    open_digit: int | None,
    close_panna: str | None,
    close_digit: int | None,
) -> bool:
    if code == "JODI":
        return (
            open_digit is not None
            and close_digit is not None
            and selection == f"{open_digit}{close_digit}"
        )
    if session == "open":
        actual = open_panna if code.endswith("_PANNA") else open_digit
    else:
        actual = close_panna if code.endswith("_PANNA") else close_digit
    return actual is not None and selection == str(actual)
