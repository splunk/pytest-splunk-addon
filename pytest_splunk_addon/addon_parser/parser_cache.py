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
Provides caching mechanism for parsed configuration files to avoid redundant
parsing when using pytest-xdist with multiple workers.

The cache stores parsed configuration data (props, transforms, tags, etc.) in a
temporary file that is shared across all xdist workers. This significantly reduces
test startup time when running with multiple workers.

Key features:
- Per-key locking to prevent deadlocks when nested cache lookups occur
- Atomic writes with integrity hash to prevent corruption
- Automatic cleanup on process exit
"""
import atexit
import hashlib
import logging
import os
import pickle
import re
import tempfile
from contextlib import nullcontext
from typing import Callable, Dict, Optional, TypeVar

from filelock import FileLock

from pytest_splunk_addon import utils

LOGGER = logging.getLogger("pytest-splunk-addon")

T = TypeVar("T")


class ParserCache:
    """
    Caches parsed configuration data to avoid redundant parsing in xdist workers.
    
    When running under pytest-xdist, this class creates a shared cache file in the
    system temp directory. The first worker to request a cache key will parse the
    data and save it; subsequent workers load from cache.
    
    Thread safety is ensured via FileLock with per-key locks to prevent deadlocks
    when nested cache lookups occur (e.g., props_fields -> props -> transforms).
    """

    def __init__(self):
        """Initialize the parser cache."""
        self._cache_file: Optional[str] = None
        self._cache_hash_file: Optional[str] = None
        self._cache_lock: Optional[FileLock] = None
        self._cache_dir: Optional[str] = None
        
        # Only enable caching when running under xdist
        if "PYTEST_XDIST_TESTRUNUID" in os.environ:
            self._init_cache_paths()

    def _init_cache_paths(self):
        """Initialize cache file paths for xdist runs."""
        testrunuid = os.environ.get("PYTEST_XDIST_TESTRUNUID", "")
        safe_testrunuid = re.sub(r"[^A-Za-z0-9_.-]", "_", testrunuid or "xdist")
        self._cache_dir = os.path.join(tempfile.gettempdir(), "pytest-splunk-addon")
        os.makedirs(self._cache_dir, exist_ok=True)
        
        self._cache_file = os.path.join(
            self._cache_dir, f"{safe_testrunuid}_parser_cache"
        )
        self._cache_hash_file = f"{self._cache_file}.sha256"
        self._cache_lock = FileLock(f"{self._cache_file}.lock")
        atexit.register(self._cleanup_cache)

    def _get_key_lock(self, cache_key: str) -> Optional[FileLock]:
        """
        Get a per-key lock to prevent deadlocks during nested cache lookups.
        
        Args:
            cache_key: The cache key to get a lock for
            
        Returns:
            FileLock for the key, or None if caching is disabled
        """
        if not self._cache_file:
            return None
        return FileLock(f"{self._cache_file}.{cache_key}.lock")

    def _is_cache_file_valid(self, path: str) -> bool:
        """
        Check if a cache file exists and is in the expected location.
        
        Args:
            path: Path to the cache file
            
        Returns:
            True if the file exists and is within the cache directory
        """
        if not path or not os.path.isfile(path):
            return False
        if self._cache_dir:
            cache_dir = os.path.abspath(self._cache_dir)
            target = os.path.abspath(path)
            if os.path.commonpath([cache_dir, target]) != cache_dir:
                LOGGER.warning("Cache file path is outside cache directory")
                return False
        return True

    def _write_atomic(self, path: str, data: bytes):
        """
        Write data to a file atomically using a temp file and rename.
        
        This prevents partial reads if another process reads during write.
        
        Args:
            path: Destination file path
            data: Bytes to write
        """
        if not self._cache_dir:
            raise ValueError("Cache directory not initialized")
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb", delete=False, dir=self._cache_dir
            ) as tmp:
                temp_file = tmp.name
                tmp.write(data)
                tmp.flush()
                os.fsync(tmp.fileno())
            os.chmod(temp_file, 0o600)
            os.replace(temp_file, path)
        finally:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass

    def get_cached_data(self) -> Optional[Dict]:
        """
        Load cached data from disk if available and valid.
        
        Validates that both the cache file and its hash file exist, then
        verifies the hash matches. If hash mismatch occurs (possibly due to
        concurrent write), retries once under lock.
        
        Returns:
            Cached data dictionary, or None if cache is missing/invalid
        """
        if not self._cache_file or not os.path.exists(self._cache_file):
            return None
        if not self._is_cache_file_valid(self._cache_file):
            return None
        if not self._cache_hash_file or not os.path.exists(self._cache_hash_file):
            LOGGER.warning("Cache hash file missing, ignoring cache")
            return None
        if not self._is_cache_file_valid(self._cache_hash_file):
            return None
        
        def _read_and_verify() -> Optional[Dict]:
            with open(self._cache_file, "rb") as f:
                cache_bytes = f.read()
            with open(self._cache_hash_file, "r", encoding="utf-8") as f:
                expected_hash = f.read().strip()
            actual_hash = hashlib.sha256(cache_bytes).hexdigest()
            if expected_hash != actual_hash:
                return None
            return pickle.loads(cache_bytes)

        try:
            cached_data = _read_and_verify()
            if cached_data is None:
                # Hash mismatch - likely read during concurrent write; retry under lock
                with self._cache_lock or nullcontext():
                    cached_data = _read_and_verify()
                if cached_data is None:
                    LOGGER.warning("Cache hash mismatch, ignoring cache")
                    return None
            LOGGER.info("Loaded parser cache from %s", self._cache_file)
            return cached_data
        except (IOError, pickle.PickleError) as e:
            LOGGER.warning("Failed to load parser cache: %s", str(e))
            return None

    def _save_cached_data(self, data: Dict):
        """
        Save data to cache file with integrity hash.
        
        Writes are atomic (temp file + rename) to prevent corruption.
        Must be called under appropriate lock.
        
        Args:
            data: Dictionary to cache
        """
        if not self._cache_file:
            return
        try:
            cache_bytes = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
            cache_hash = hashlib.sha256(cache_bytes).hexdigest().encode("utf-8")
            self._write_atomic(self._cache_file, cache_bytes)
            self._write_atomic(self._cache_hash_file, cache_hash)
            LOGGER.info("Saved parser cache to %s", self._cache_file)
        except IOError as e:
            LOGGER.warning("Failed to save parser cache: %s", str(e))

    def get_or_parse(self, parse_func: Callable[[], T], cache_key: str) -> T:
        """
        Get data from cache or parse it if not cached.
        
        Uses per-key FileLock to ensure only one worker parses each key,
        preventing deadlocks when nested cache lookups occur.
        
        Args:
            parse_func: Zero-argument function that returns the data to cache
            cache_key: Key to store/retrieve data under in the cache dict
            
        Returns:
            The cached or freshly parsed data
        """
        # Fast path: check cache without lock
        if self._cache_file and os.path.exists(self._cache_file):
            cached_data = self.get_cached_data()
            if cached_data and cache_key in cached_data:
                LOGGER.debug("Using cached %s", cache_key)
                return cached_data[cache_key]
        
        # Not in cache - acquire per-key lock and parse
        key_lock = self._get_key_lock(cache_key)
        with key_lock or nullcontext():
            # Double-check after acquiring lock
            if self._cache_file and os.path.exists(self._cache_file):
                cached_data = self.get_cached_data()
                if cached_data and cache_key in cached_data:
                    LOGGER.debug("Using cached %s (after lock)", cache_key)
                    return cached_data[cache_key]

            # Parse the data
            LOGGER.info("Parsing %s (cache miss)", cache_key)
            parsed_data = parse_func()

            # Save to cache under global lock for consistency
            if self._cache_lock:
                with self._cache_lock:
                    cached_data = self.get_cached_data() or {}
                    cached_data[cache_key] = parsed_data
                    self._save_cached_data(cached_data)

            return parsed_data

    def _cleanup_cache(self):
        """
        Remove cache files on process exit.
        
        Only the first worker (gw0) performs cleanup to avoid race conditions.
        Called automatically via atexit.
        """
        if not self._cache_file or not utils.check_first_worker():
            return
        try:
            with self._cache_lock or nullcontext():
                for path in [
                    self._cache_file,
                    self._cache_hash_file,
                    f"{self._cache_file}.lock",
                ]:
                    if path and os.path.exists(path):
                        os.remove(path)
        except OSError as e:
            LOGGER.warning("Failed to clean cache files: %s", str(e))

