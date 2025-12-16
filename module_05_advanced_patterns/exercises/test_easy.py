"""
Tests for Exercise 1 (Easy): Async Patterns Basics
Run with: python -m pytest module_05_advanced_patterns/exercises/test_easy.py -v
"""

import asyncio
import time
import pytest

from exercise_easy import (
    AsyncTimer,
    AsyncCountdown,
    paginate,
    async_retry,
    managed_resource,
)


class TestAsyncTimer:
    """Tests for Exercise 1.1: AsyncTimer"""

    def test_measures_time(self):
        async def check():
            async with AsyncTimer() as timer:
                await asyncio.sleep(0.2)
            assert 0.2 <= timer.elapsed < 0.3

        asyncio.run(check())

    def test_short_duration(self):
        async def check():
            async with AsyncTimer() as timer:
                pass
            assert timer.elapsed < 0.1

        asyncio.run(check())


class TestAsyncCountdown:
    """Tests for Exercise 1.2: AsyncCountdown"""

    def test_countdown(self):
        async def check():
            numbers = []
            async for num in AsyncCountdown(3):
                numbers.append(num)
            assert numbers == [3, 2, 1]

        asyncio.run(check())

    def test_timing(self):
        async def check():
            start = time.time()
            async for _ in AsyncCountdown(3):
                pass
            elapsed = time.time() - start
            assert elapsed >= 0.3

        asyncio.run(check())

    def test_single(self):
        async def check():
            numbers = []
            async for num in AsyncCountdown(1):
                numbers.append(num)
            assert numbers == [1]

        asyncio.run(check())


class TestPaginate:
    """Tests for Exercise 1.3: paginate"""

    def test_exact_pages(self):
        async def check():
            pages = []
            async for page in paginate([1, 2, 3, 4], 2):
                pages.append(page)
            assert pages == [[1, 2], [3, 4]]

        asyncio.run(check())

    def test_partial_last_page(self):
        async def check():
            pages = []
            async for page in paginate([1, 2, 3, 4, 5], 2):
                pages.append(page)
            assert pages == [[1, 2], [3, 4], [5]]

        asyncio.run(check())

    def test_empty(self):
        async def check():
            pages = []
            async for page in paginate([], 2):
                pages.append(page)
            assert pages == []

        asyncio.run(check())

    def test_has_delay(self):
        async def check():
            start = time.time()
            async for _ in paginate([1, 2, 3], 2):
                pass
            elapsed = time.time() - start
            assert elapsed >= 0.2  # 2 pages * 0.1s

        asyncio.run(check())


class TestAsyncRetry:
    """Tests for Exercise 1.4: async_retry"""

    def test_success_first_try(self):
        @async_retry(max_retries=3)
        async def always_works():
            return "success"

        async def check():
            result = await always_works()
            assert result == "success"

        asyncio.run(check())

    def test_success_after_retry(self):
        attempts = [0]

        @async_retry(max_retries=3)
        async def works_second_try():
            attempts[0] += 1
            if attempts[0] < 2:
                raise ValueError("fail")
            return "success"

        async def check():
            result = await works_second_try()
            assert result == "success"
            assert attempts[0] == 2

        asyncio.run(check())

    def test_all_fail(self):
        @async_retry(max_retries=2)
        async def always_fails():
            raise ValueError("always fails")

        async def check():
            with pytest.raises(ValueError, match="always fails"):
                await always_fails()

        asyncio.run(check())


class TestManagedResource:
    """Tests for Exercise 1.5: managed_resource"""

    def test_acquires_and_releases(self):
        async def check():
            log = []
            async with managed_resource("test", log) as resource:
                assert resource == "test"
            assert "acquire:test" in log
            assert "release:test" in log

        asyncio.run(check())

    def test_order(self):
        async def check():
            log = []
            async with managed_resource("db", log):
                pass
            assert log.index("acquire:db") < log.index("release:db")

        asyncio.run(check())

    def test_releases_on_exception(self):
        async def check():
            log = []
            try:
                async with managed_resource("conn", log):
                    raise ValueError("error")
            except ValueError:
                pass
            assert "release:conn" in log

        asyncio.run(check())
