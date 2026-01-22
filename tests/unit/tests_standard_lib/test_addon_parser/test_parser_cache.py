#
# Copyright 2025 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Unit tests for ParserCache.
"""
import os
import tempfile
from unittest.mock import patch

import pytest

from pytest_splunk_addon.addon_parser.parser_cache import ParserCache


class TestParserCacheNoXdist:
    """Tests for ParserCache when not running under xdist."""

    def test_init_no_xdist(self):
        """Cache should not be initialized when PYTEST_XDIST_TESTRUNUID is not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Ensure no xdist env var
            os.environ.pop("PYTEST_XDIST_TESTRUNUID", None)
            cache = ParserCache()
            assert cache._cache_file is None
            assert cache._cache_lock is None

    def test_get_or_parse_no_xdist(self):
        """Without xdist, get_or_parse should call parse_func directly."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("PYTEST_XDIST_TESTRUNUID", None)
            cache = ParserCache()
            
            call_count = 0
            def parse_func():
                nonlocal call_count
                call_count += 1
                return {"key": "value"}

            result = cache.get_or_parse(parse_func, "test_key")
            assert result == {"key": "value"}
            assert call_count == 1

            # Second call should also call parse_func (no caching without xdist)
            result = cache.get_or_parse(parse_func, "test_key")
            assert result == {"key": "value"}
            assert call_count == 2


class TestParserCacheWithXdist:
    """Tests for ParserCache when running under xdist."""

    @pytest.fixture
    def xdist_env(self):
        """Set up xdist environment variables."""
        with patch.dict(os.environ, {"PYTEST_XDIST_TESTRUNUID": "test_run_123"}):
            yield

    @pytest.fixture
    def cache(self, xdist_env):
        """Create a ParserCache with xdist enabled."""
        cache = ParserCache()
        yield cache
        # Cleanup
        if cache._cache_file and os.path.exists(cache._cache_file):
            os.remove(cache._cache_file)
        if cache._cache_hash_file and os.path.exists(cache._cache_hash_file):
            os.remove(cache._cache_hash_file)
        lock_file = f"{cache._cache_file}.lock" if cache._cache_file else None
        if lock_file and os.path.exists(lock_file):
            os.remove(lock_file)

    def test_init_with_xdist(self, xdist_env):
        """Cache should be initialized when PYTEST_XDIST_TESTRUNUID is set."""
        cache = ParserCache()
        assert cache._cache_file is not None
        assert cache._cache_lock is not None
        assert "test_run_123" in cache._cache_file

    def test_get_or_parse_caches_result(self, cache):
        """get_or_parse should cache the result and return it on subsequent calls."""
        call_count = 0
        def parse_func():
            nonlocal call_count
            call_count += 1
            return {"data": f"parsed_{call_count}"}

        # First call should parse
        result1 = cache.get_or_parse(parse_func, "my_key")
        assert result1 == {"data": "parsed_1"}
        assert call_count == 1

        # Second call should use cache
        result2 = cache.get_or_parse(parse_func, "my_key")
        assert result2 == {"data": "parsed_1"}  # Same data from cache
        assert call_count == 1  # parse_func not called again

    def test_get_or_parse_different_keys(self, cache):
        """Different keys should be cached separately."""
        def parse_a():
            return {"type": "a"}

        def parse_b():
            return {"type": "b"}

        result_a = cache.get_or_parse(parse_a, "key_a")
        result_b = cache.get_or_parse(parse_b, "key_b")

        assert result_a == {"type": "a"}
        assert result_b == {"type": "b"}

        # Verify both are cached
        result_a2 = cache.get_or_parse(lambda: {"type": "new"}, "key_a")
        result_b2 = cache.get_or_parse(lambda: {"type": "new"}, "key_b")

        assert result_a2 == {"type": "a"}  # From cache
        assert result_b2 == {"type": "b"}  # From cache

    def test_is_cache_file_valid_rejects_outside_dir(self, cache):
        """Cache file validation should reject files outside cache dir."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"test")
            tmp.flush()
            try:
                assert not cache._is_cache_file_valid(tmp.name)
            finally:
                os.remove(tmp.name)

    def test_is_cache_file_valid_accepts_inside_dir(self, cache):
        """Cache file validation should accept files inside cache dir."""
        # The cache file itself should be valid once created
        cache._save_cached_data({"test": "data"})
        assert cache._is_cache_file_valid(cache._cache_file)

    def test_get_cached_data_returns_none_for_missing_file(self, cache):
        """get_cached_data should return None if cache file doesn't exist."""
        assert cache.get_cached_data() is None

    def test_get_cached_data_returns_none_for_missing_hash(self, cache):
        """get_cached_data should return None if hash file is missing."""
        # Create cache file without hash file
        cache._write_atomic(cache._cache_file, b"test data")
        assert cache.get_cached_data() is None

