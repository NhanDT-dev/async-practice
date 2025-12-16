"""
Tests for Exercise 1 (Easy): Basic Async I/O
Run with: python -m pytest module_04_async_io/exercises/test_easy.py -v
"""

import asyncio
import time
import pytest

from exercise_easy import (
    read_file_async,
    MockHttpClient,
    read_files_parallel,
    fetch_with_retry,
    process_batch,
)


class TestReadFileAsync:
    """Tests for Exercise 1.1: read_file_async"""

    def test_reads_existing_file(self):
        async def check():
            files = {"test.txt": "Hello World"}
            content = await read_file_async("test.txt", files)
            assert content == "Hello World"

        asyncio.run(check())

    def test_raises_for_missing_file(self):
        async def check():
            files = {"test.txt": "Hello"}
            with pytest.raises(FileNotFoundError):
                await read_file_async("missing.txt", files)

        asyncio.run(check())

    def test_has_delay(self):
        async def check():
            files = {"test.txt": "Content"}
            start = time.time()
            await read_file_async("test.txt", files)
            elapsed = time.time() - start
            assert elapsed >= 0.1

        asyncio.run(check())


class TestMockHttpClient:
    """Tests for Exercise 1.2: MockHttpClient"""

    def test_get_existing_url(self):
        async def check():
            responses = {"http://api/data": {"result": 42}}
            client = MockHttpClient(responses)
            result = await client.get("http://api/data")
            assert result == {"result": 42}

        asyncio.run(check())

    def test_get_missing_url(self):
        async def check():
            client = MockHttpClient({})
            result = await client.get("http://unknown")
            assert result == {"error": "Not Found"}

        asyncio.run(check())

    def test_post(self):
        async def check():
            client = MockHttpClient({})
            result = await client.post("http://api/create", {"name": "test"})
            assert result["status"] == "created"
            assert result["data"] == {"name": "test"}

        asyncio.run(check())

    def test_has_delay(self):
        async def check():
            client = MockHttpClient({"url": "data"})
            start = time.time()
            await client.get("url")
            elapsed = time.time() - start
            assert elapsed >= 0.1

        asyncio.run(check())


class TestReadFilesParallel:
    """Tests for Exercise 1.3: read_files_parallel"""

    def test_reads_multiple_files(self):
        async def check():
            files = {"a.txt": "A", "b.txt": "B", "c.txt": "C"}
            result = await read_files_parallel(["a.txt", "b.txt"], files)
            assert result == {"a.txt": "A", "b.txt": "B"}

        asyncio.run(check())

    def test_skips_missing(self):
        async def check():
            files = {"a.txt": "A"}
            result = await read_files_parallel(["a.txt", "missing.txt"], files)
            assert result == {"a.txt": "A"}

        asyncio.run(check())

    def test_concurrent_execution(self):
        async def check():
            files = {f"{i}.txt": str(i) for i in range(5)}
            start = time.time()
            await read_files_parallel(list(files.keys()), files)
            elapsed = time.time() - start
            # 5 files at 0.1s each = 0.5s sequential, should be ~0.1s concurrent
            assert elapsed < 0.2

        asyncio.run(check())


class TestFetchWithRetry:
    """Tests for Exercise 1.4: fetch_with_retry"""

    def test_success_first_try(self):
        async def check():
            responses = {"url": {"data": "ok"}}
            client = MockHttpClient(responses)
            result = await fetch_with_retry(client, "url", max_retries=3)
            assert result == {"data": "ok"}

        asyncio.run(check())

    def test_retries_on_error(self):
        async def check():
            # Use a client that tracks attempts
            attempts = [0]
            responses = {"url": {"error": "fail"}}

            class RetryClient(MockHttpClient):
                async def get(self, url):
                    attempts[0] += 1
                    if attempts[0] < 3:
                        return {"error": "temporary"}
                    return {"data": "success"}

            client = RetryClient(responses)
            result = await fetch_with_retry(client, "url", max_retries=5)
            assert result == {"data": "success"}
            assert attempts[0] == 3

        asyncio.run(check())

    def test_returns_error_after_max_retries(self):
        async def check():
            client = MockHttpClient({})  # All URLs return error
            result = await fetch_with_retry(client, "url", max_retries=2)
            assert "error" in result

        asyncio.run(check())


class TestProcessBatch:
    """Tests for Exercise 1.5: process_batch"""

    def test_processes_all(self):
        async def double(x):
            return x * 2

        async def check():
            results = await process_batch([1, 2, 3], double)
            assert results == [2, 4, 6]

        asyncio.run(check())

    def test_preserves_order(self):
        async def identity(x):
            await asyncio.sleep(0.1 - x * 0.02)  # Different delays
            return x

        async def check():
            results = await process_batch([1, 2, 3, 4], identity)
            assert results == [1, 2, 3, 4]

        asyncio.run(check())

    def test_concurrent_execution(self):
        async def slow_process(x):
            await asyncio.sleep(0.1)
            return x

        async def check():
            start = time.time()
            await process_batch([1, 2, 3, 4, 5], slow_process)
            elapsed = time.time() - start
            # Should be ~0.1s concurrent, not 0.5s sequential
            assert elapsed < 0.2

        asyncio.run(check())

    def test_empty_list(self):
        async def process(x):
            return x

        async def check():
            results = await process_batch([], process)
            assert results == []

        asyncio.run(check())
