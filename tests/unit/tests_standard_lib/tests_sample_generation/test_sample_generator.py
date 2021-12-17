from unittest.mock import MagicMock, patch

from pytest_splunk_addon.standard_lib.sample_generation.sample_generator import (
    SampleGenerator,
)

MODULE_PATH = "pytest_splunk_addon.standard_lib.sample_generation.sample_generator"
ADDON_PATH = "/add/on/path"
CONFIG_PATH = "/config/path"


class TestSampleGenerator:
    def test_init(self):
        sg = SampleGenerator(ADDON_PATH, CONFIG_PATH)
        assert sg.addon_path == ADDON_PATH
        assert sg.config_path == CONFIG_PATH
        assert sg.process_count == 4
        sg = SampleGenerator(ADDON_PATH, CONFIG_PATH, 2)
        assert sg.addon_path == ADDON_PATH
        assert sg.config_path == CONFIG_PATH
        assert sg.process_count == 2

    def test_get_samples(self):
        tks_1 = "tokenized_sample_1"
        tks_2 = "tokenized_sample_2"
        sample_mock = MagicMock()
        sample_mock.get_tokenized_events.return_value = [tks_1, tks_2]
        psa_data_mock = MagicMock()
        psa_data_mock.get_sample_stanzas = MagicMock(
            return_value=[sample_mock, sample_mock]
        )
        with patch(
            f"{MODULE_PATH}.PytestSplunkAddonDataParser",
            MagicMock(return_value=psa_data_mock),
        ), patch(f"{MODULE_PATH}.SampleStanza", MagicMock()) as sample_stanza_mock:
            sample_stanza_mock.get_raw_events = ["event_1", "event_2"]
            sample_stanza_mock.tokenize = lambda x, y: (x, y)
            psa_data_mock.conf_name = CONFIG_PATH
            sg = SampleGenerator(ADDON_PATH)
            assert list(sg.get_samples()) == [tks_1, tks_2, tks_1, tks_2]

    def test_clean_samples(self):
        SampleGenerator.sample_stanzas = [10]
        SampleGenerator.conf_name = "conf_name"
        SampleGenerator.clean_samples()
        assert SampleGenerator.sample_stanzas == []
        assert SampleGenerator.conf_name == ""
