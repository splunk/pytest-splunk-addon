from datetime import datetime
from unittest.mock import MagicMock, patch
from freezegun import freeze_time

from pytest_splunk_addon.standard_lib.sample_generation.time_parser import (
    time_parse,
)


class Testtime_parse:
    @freeze_time("2020-11-01T04:16:13-04:00")
    def test_convert_to_time(self):
        tp = time_parse()
        assert tp.convert_to_time("-", "60", "seconds") == datetime(
            2020, 11, 1, 8, 15, 13
        )
