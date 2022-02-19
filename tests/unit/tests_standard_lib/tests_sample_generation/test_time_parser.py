from datetime import datetime

import pytest
from freezegun import freeze_time

from pytest_splunk_addon.standard_lib.sample_generation.time_parser import time_parse


@pytest.fixture(scope="session")
def tp():
    return time_parse()


def generate_parameters():
    result = []
    for s in ("s", "sec", "secs", "second", "seconds"):
        result.append(("-", "60", s, datetime(2020, 9, 1, 8, 15, 13)))
    for m in ("m", "min", "minute", "minutes"):
        result.append(("-", "60", m, datetime(2020, 9, 1, 7, 16, 13)))
    for h in ("h", "hr", "hrs", "hour", "hours"):
        result.append(("-", "60", h, datetime(2020, 8, 29, 20, 16, 13)))
    for d in ("d", "day", "days"):
        result.append(("-", "1", d, datetime(2020, 8, 31, 8, 16, 13)))
    for w in ("w", "week", "weeks"):
        result.append(("-", "2", w, datetime(2020, 8, 18, 8, 16, 13)))
    for m in ("mon", "month", "months"):
        result.append(("-", "2", m, datetime(2020, 7, 1, 8, 16, 13)))
    for q in ("q", "qtr", "qtrs", "quarter", "quarters"):
        result.append(("-", "2", q, datetime(2020, 3, 1, 8, 16, 13)))
    for y in ("y", "yr", "yrs", "year", "years"):
        result.append(("-", "2", y, datetime(2018, 9, 1, 8, 16, 13)))
    result.extend(
        [
            ("+", "5", "months", datetime(2021, 2, 1, 8, 16, 13)),
            ("+", "3", "months", datetime(2020, 12, 1, 8, 16, 13)),
            ("-", "11", "months", datetime(2019, 10, 1, 8, 16, 13)),
            ("smth", "15", "minutes", datetime(2020, 9, 1, 8, 31, 13)),
        ]
    )
    return result


class Testtime_parse:
    @freeze_time("2020-09-01T04:16:13-04:00")
    @pytest.mark.parametrize("sign, num, unit, expected", generate_parameters())
    def test_convert_to_time(self, tp, sign, num, unit, expected):
        assert tp.convert_to_time(sign, num, unit) == expected

    @pytest.mark.parametrize(
        "timezone_time, expected",
        [
            ("+1122", datetime(2020, 9, 1, 19, 37, 13)),
            ("+0022", datetime(2020, 9, 1, 8, 15, 13)),
            ("+2322", datetime(2020, 9, 1, 8, 15, 13)),
            ("+1200", datetime(2020, 9, 1, 8, 15, 13)),
            ("+0559", datetime(2020, 9, 1, 8, 15, 13)),
            ("-1122", datetime(2020, 8, 31, 20, 53, 13)),
        ],
    )
    def test_get_timezone_time(self, tp, timezone_time, expected):
        assert (
            tp.get_timezone_time(datetime(2020, 9, 1, 8, 15, 13), timezone_time)
            == expected
        )
