"""
Tests for Exercise 1 (Easy): Basic Synchronization Primitives
Run with: python -m pytest module_03_synchronization/exercises/test_easy.py -v
"""

import asyncio
import time
import pytest

from exercise_easy import (
    SafeCounter,
    run_with_start_signal,
    rate_limited_fetch,
    AsyncToggle,
    SharedResource,
)


class TestSafeCounter:
    """Tests for Exercise 1.1: SafeCounter"""

    def test_initial_value(self):
        counter = SafeCounter()
        assert counter.value == 0

    def test_single_increment(self):
        async def check():
            counter = SafeCounter()
            await counter.increment()
            assert counter.value == 1

        asyncio.run(check())

    def test_concurrent_increments(self):
        async def check():
            counter = SafeCounter()
            await asyncio.gather(*[counter.increment() for _ in range(100)])
            assert counter.value == 100

        asyncio.run(check())

    def test_multiple_rounds(self):
        async def check():
            counter = SafeCounter()
            await asyncio.gather(*[counter.increment() for _ in range(50)])
            await asyncio.gather(*[counter.increment() for _ in range(50)])
            assert counter.value == 100

        asyncio.run(check())


class TestRunWithStartSignal:
    """Tests for Exercise 1.2: run_with_start_signal"""

    def test_returns_dict(self):
        async def check():
            event = asyncio.Event()
            event.set()  # Already set
            result = await run_with_start_signal(["A"], event)
            assert isinstance(result, dict)
            assert "A" in result

        asyncio.run(check())

    def test_waits_for_signal(self):
        async def check():
            event = asyncio.Event()
            start = time.time()

            async def delayed_set():
                await asyncio.sleep(0.2)
                event.set()

            await asyncio.gather(
                run_with_start_signal(["A", "B"], event),
                delayed_set()
            )

            elapsed = time.time() - start
            assert elapsed >= 0.2  # Waited for signal

        asyncio.run(check())

    def test_all_workers_complete(self):
        async def check():
            event = asyncio.Event()
            event.set()
            result = await run_with_start_signal(["A", "B", "C"], event)
            assert len(result) == 3

        asyncio.run(check())


class TestRateLimitedFetch:
    """Tests for Exercise 1.3: rate_limited_fetch"""

    def test_returns_all_results(self):
        async def check():
            results = await rate_limited_fetch(["a", "b", "c"], 2)
            assert len(results) == 3
            assert "Fetched: a" in results

        asyncio.run(check())

    def test_respects_limit(self):
        running = 0
        max_running = 0

        original_fetch = None

        async def check():
            nonlocal running, max_running

            # We'll verify by timing - if limit=2, 4 items take ~0.2s, not 0.1s
            start = time.time()
            await rate_limited_fetch(["a", "b", "c", "d"], 2)
            elapsed = time.time() - start

            # 4 URLs, limit 2 -> 2 batches of 0.1s = ~0.2s
            assert elapsed >= 0.15, f"Should take at least 0.15s, got {elapsed}s"

        asyncio.run(check())

    def test_empty_list(self):
        async def check():
            results = await rate_limited_fetch([], 2)
            assert results == []

        asyncio.run(check())


class TestAsyncToggle:
    """Tests for Exercise 1.4: AsyncToggle"""

    def test_initial_state(self):
        toggle = AsyncToggle()
        assert toggle.is_on is False

    def test_turn_on(self):
        toggle = AsyncToggle()
        toggle.turn_on()
        assert toggle.is_on is True

    def test_turn_off(self):
        toggle = AsyncToggle()
        toggle.turn_on()
        toggle.turn_off()
        assert toggle.is_on is False

    def test_wait_for_on(self):
        async def check():
            toggle = AsyncToggle()

            async def delayed_on():
                await asyncio.sleep(0.1)
                toggle.turn_on()

            start = time.time()
            await asyncio.gather(
                toggle.wait_for_on(),
                delayed_on()
            )
            elapsed = time.time() - start
            assert elapsed >= 0.1

        asyncio.run(check())

    def test_already_on(self):
        async def check():
            toggle = AsyncToggle()
            toggle.turn_on()
            # Should return immediately
            start = time.time()
            await toggle.wait_for_on()
            elapsed = time.time() - start
            assert elapsed < 0.05

        asyncio.run(check())


class TestSharedResource:
    """Tests for Exercise 1.5: SharedResource"""

    def test_initial_empty(self):
        async def check():
            resource = SharedResource()
            data = await resource.get_all()
            assert data == []

        asyncio.run(check())

    def test_add_single(self):
        async def check():
            resource = SharedResource()
            await resource.add("item")
            data = await resource.get_all()
            assert data == ["item"]

        asyncio.run(check())

    def test_concurrent_adds(self):
        async def check():
            resource = SharedResource()
            await asyncio.gather(*[resource.add(i) for i in range(20)])
            data = await resource.get_all()
            assert len(data) == 20
            assert sorted(data) == list(range(20))

        asyncio.run(check())

    def test_get_returns_copy(self):
        async def check():
            resource = SharedResource()
            await resource.add(1)
            data = await resource.get_all()
            data.append(2)
            original = await resource.get_all()
            assert original == [1]  # Not modified

        asyncio.run(check())
