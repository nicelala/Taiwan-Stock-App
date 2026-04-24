from decimal import Decimal
from datetime import date

from app.core.utils import parse_decimal, parse_date, get_first, fix_mojibake


def test_parse_decimal_basic():
    assert parse_decimal("1,234.56") == Decimal("1234.56")
    assert parse_decimal("10") == Decimal("10")
    assert parse_decimal("-") is None
    assert parse_decimal(None) is None


def test_parse_date_gregorian():
    assert parse_date("2026/03/31") == date(2026, 3, 31)
    assert parse_date("20260331") == date(2026, 3, 31)


def test_parse_date_roc():
    assert parse_date("115/03/31") == date(2026, 3, 31)
    assert parse_date("1150331") == date(2026, 3, 31)


def test_get_first():
    raw = {
        "A": "",
        "B": "-",
        "C": "value-c",
    }
    assert get_first(raw, "A", "B", "C") == "value-c"
    assert get_first(raw, "X", "Y") is None


def test_fix_mojibake_keeps_normal_chinese():
    assert fix_mojibake("台積電") == "台積電"


def test_fix_mojibake_repairs_common_utf8_latin1_case():
    # 這是台積電常見的 mojibake 範例
    broken = "å°ç©é»"
    assert fix_mojibake(broken) == "台積電"