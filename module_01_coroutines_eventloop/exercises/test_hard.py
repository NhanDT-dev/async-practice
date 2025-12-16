"""
Tests for Exercise 3 (Hard): Advanced Coroutine Patterns
Run with: python -m pytest module_01_coroutines_eventloop/exercises/test_hard.py -v
"""

import asyncio
import time
import pytest

from exercise_hard import (
    retry_with_backoff,
    limited_gather,
    pipeline,
    first_successful,
    AsyncEventEmitter,
)


class TestRetryWithBackoff:
    """Tests for Exercise 3.1: retry_with_backoff"""

    def test_success_on_first_try(self):
        async def always_works():
            return "success"

        result = asyncio.run(retry_with_backoff(always_works, 3, 0.1))
        assert result == "success"

    def test_success_after_retries(self):
        attempt = 0

        async def works_on_third():
            nonlocal attempt
            attempt += 1
            if attempt < 3:
                raise ValueError("Not yet")
            return "finally!"

        result = asyncio.run(retry_with_backoff(works_on_third, 5, 0.05))
        assert result == "finally!"
        assert attempt == 3

    def test_all_retries_fail(self):
        async def always_fails():
            raise ValueError("Always fails")

        with pytest.raises(ValueError, match="Always fails"):
            asyncio.run(retry_with_backoff(always_fails, 3, 0.01))

    def test_exponential_backoff_timing(self):
        attempt = 0

        async def fails_twice():
            nonlocal attempt
            attempt += 1
            if attempt <= 2:
                raise ValueError("Fail")
            return "ok"

        start = time.time()
        asyncio.run(retry_with_backoff(fails_twice, 5, 0.1))
        elapsed = time.time() - start

        # Should wait 0.1s + 0.2s = 0.3s total
        assert 0.25 < elapsed < 0.45, f"Expected ~0.3s delay, got {elapsed}s"


class TestLimitedGather:
    """Tests for Exercise 3.2: limited_gather"""

    def test_all_complete(self):
        async def task(n):
            await asyncio.sleep(0.05)
            return n

        coros = [task(i) for i in range(5)]
        results = asyncio.run(limited_gather(coros, 2))
        assert results == [0, 1, 2, 3, 4]

    def test_respects_limit(self):
        running = 0
        max_running = 0

        async def track_task(n):
            nonlocal running, max_running
            running += 1
            max_running = max(max_running, running)
            await asyncio.sleep(0.1)
            running -= 1
            return n

        coros = [track_task(i) for i in range(6)]
        asyncio.run(limited_gather(coros, 2))
        assert max_running <= 2, f"Max concurrent was {max_running}, expected <= 2"

    def test_timing_with_limit(self):
        async def slow_task(n):
            await asyncio.sleep(0.1)
            return n

        start = time.time()
        coros = [slow_task(i) for i in range(4)]
        asyncio.run(limited_gather(coros, 2))
        elapsed = time.time() - start

        # 4 tasks, limit 2 -> 2 batches -> ~0.2s
        assert 0.15 < elapsed < 0.35, f"Expected ~0.2s, got {elapsed}s"

    def test_empty_list(self):
        results = asyncio.run(limited_gather([], 2))
        assert results == []


class TestPipeline:
    """Tests for Exercise 3.3: pipeline"""

    def test_simple_pipeline(self):
        async def add_one(x):
            return x + 1

        async def double(x):
            return x * 2

        result = asyncio.run(pipeline(5, [add_one, double]))
        assert result == 12  # (5 + 1) * 2

    def test_type_transformation(self):
        async def double(x):
            await asyncio.sleep(0.05)
            return x * 2

        async def to_string(x):
            await asyncio.sleep(0.05)
            return str(x)

        async def add_suffix(x):
            await asyncio.sleep(0.05)
            return x + "!"

        result = asyncio.run(pipeline(5, [double, to_string, add_suffix]))
        assert result == "10!"

    def test_empty_pipeline(self):
        result = asyncio.run(pipeline(42, []))
        assert result == 42

    def test_single_stage(self):
        async def negate(x):
            return -x

        result = asyncio.run(pipeline(10, [negate]))
        assert result == -10


class TestFirstSuccessful:
    """Tests for Exercise 3.4: first_successful"""

    def test_first_succeeds(self):
        async def success():
            await asyncio.sleep(0.1)
            return "ok"

        result = asyncio.run(first_successful([success]))
        assert result == "ok"

    def test_fast_fail_slow_success(self):
        async def fast_fail():
            await asyncio.sleep(0.05)
            raise ValueError("Fast fail")

        async def slow_success():
            await asyncio.sleep(0.2)
            return "Success!"

        result = asyncio.run(first_successful([fast_fail, slow_success]))
        assert result == "Success!"

    def test_multiple_successes_returns_first(self):
        async def slow_success():
            await asyncio.sleep(0.2)
            return "Slow"

        async def fast_success():
            await asyncio.sleep(0.05)
            return "Fast"

        result = asyncio.run(first_successful([slow_success, fast_success]))
        assert result == "Fast"

    def test_all_fail(self):
        async def fail1():
            raise ValueError("Fail 1")

        async def fail2():
            raise ValueError("Fail 2")

        with pytest.raises(Exception, match="All failed"):
            asyncio.run(first_successful([fail1, fail2]))

    def test_timing(self):
        async def fast_fail():
            await asyncio.sleep(0.05)
            raise ValueError()

        async def slow_success():
            await asyncio.sleep(0.15)
            return "ok"

        start = time.time()
        asyncio.run(first_successful([fast_fail, slow_success]))
        elapsed = time.time() - start

        # Should complete at ~0.15s when slow_success finishes
        assert elapsed < 0.25, f"Expected ~0.15s, got {elapsed}s"


class TestAsyncEventEmitter:
    """Tests for Exercise 3.5: AsyncEventEmitter"""

    def test_single_handler(self):
        async def handler(x):
            return x * 2

        emitter = AsyncEventEmitter()
        emitter.on("test", handler)
        results = asyncio.run(emitter.emit("test", 5))
        assert results == [10]

    def test_multiple_handlers(self):
        async def handler1(x):
            return f"h1:{x}"

        async def handler2(x):
            return f"h2:{x}"

        emitter = AsyncEventEmitter()
        emitter.on("event", handler1)
        emitter.on("event", handler2)
        results = asyncio.run(emitter.emit("event", "data"))
        assert "h1:data" in results
        assert "h2:data" in results
        assert len(results) == 2

    def test_different_events(self):
        async def handler_a(x):
            return f"A:{x}"

        async def handler_b(x):
            return f"B:{x}"

        emitter = AsyncEventEmitter()
        emitter.on("event_a", handler_a)
        emitter.on("event_b", handler_b)

        results_a = asyncio.run(emitter.emit("event_a", 1))
        results_b = asyncio.run(emitter.emit("event_b", 2))

        assert results_a == ["A:1"]
        assert results_b == ["B:2"]

    def test_no_handlers(self):
        emitter = AsyncEventEmitter()
        results = asyncio.run(emitter.emit("unknown_event", "data"))
        assert results == []

    def test_concurrent_handlers(self):
        async def slow_handler(x):
            await asyncio.sleep(0.1)
            return f"slow:{x}"

        async def fast_handler(x):
            await asyncio.sleep(0.1)
            return f"fast:{x}"

        emitter = AsyncEventEmitter()
        emitter.on("concurrent", slow_handler)
        emitter.on("concurrent", fast_handler)

        start = time.time()
        results = asyncio.run(emitter.emit("concurrent", "test"))
        elapsed = time.time() - start

        # Both handlers should run concurrently
        assert elapsed < 0.15, f"Expected concurrent execution, got {elapsed}s"
        assert len(results) == 2

    def test_multiple_args(self):
        async def handler(a, b, c):
            return a + b + c

        emitter = AsyncEventEmitter()
        emitter.on("sum", handler)
        results = asyncio.run(emitter.emit("sum", 1, 2, 3))
        assert results == [6]
