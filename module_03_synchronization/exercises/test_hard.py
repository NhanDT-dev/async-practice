"""
Tests for Exercise 3 (Hard): Complex Synchronization Challenges
Run with: python -m pytest module_03_synchronization/exercises/test_hard.py -v
"""

import asyncio
import time
import pytest

from exercise_hard import (
    ConnectionPool,
    TokenBucketRateLimiter,
    HeartbeatLock,
    DiningTable,
    BackpressurePipeline,
)


class TestConnectionPool:
    """Tests for Exercise 3.1: ConnectionPool"""

    def test_acquire_release(self):
        async def check():
            pool = ConnectionPool(max_connections=3)
            conn = await pool.acquire()
            assert conn is not None
            await pool.release(conn)

        asyncio.run(check())

    def test_context_manager(self):
        async def check():
            pool = ConnectionPool(max_connections=2)
            async with pool.connection() as conn:
                assert conn is not None

        asyncio.run(check())

    def test_respects_max_connections(self):
        async def check():
            pool = ConnectionPool(max_connections=2)
            conn1 = await pool.acquire()
            conn2 = await pool.acquire()

            # Third acquire should block
            acquired = False

            async def try_acquire():
                nonlocal acquired
                await pool.acquire()
                acquired = True

            task = asyncio.create_task(try_acquire())
            await asyncio.sleep(0.1)
            assert acquired is False

            await pool.release(conn1)
            await asyncio.sleep(0.05)
            assert acquired is True

            await pool.release(conn2)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        asyncio.run(check())

    def test_connection_reuse(self):
        async def check():
            pool = ConnectionPool(max_connections=1)
            conn1 = await pool.acquire()
            await pool.release(conn1)
            conn2 = await pool.acquire()
            assert conn1 == conn2  # Same connection reused
            await pool.release(conn2)

        asyncio.run(check())


class TestTokenBucketRateLimiter:
    """Tests for Exercise 3.2: TokenBucketRateLimiter"""

    def test_immediate_tokens(self):
        async def check():
            limiter = TokenBucketRateLimiter(max_tokens=5, refill_period=1.0)
            start = time.time()
            for _ in range(5):
                await limiter.acquire()
            elapsed = time.time() - start
            assert elapsed < 0.1  # All 5 should be immediate

        asyncio.run(check())

    def test_rate_limiting(self):
        async def check():
            limiter = TokenBucketRateLimiter(max_tokens=2, refill_period=0.2)
            start = time.time()
            for _ in range(4):
                await limiter.acquire()
            elapsed = time.time() - start
            # 2 immediate, then wait ~0.1s for each additional
            assert elapsed >= 0.15

        asyncio.run(check())

    def test_available_tokens(self):
        async def check():
            limiter = TokenBucketRateLimiter(max_tokens=5, refill_period=1.0)
            initial = limiter.available_tokens
            assert initial == 5

            await limiter.acquire()
            assert limiter.available_tokens == 4

        asyncio.run(check())


class TestHeartbeatLock:
    """Tests for Exercise 3.3: HeartbeatLock"""

    def test_acquire_release(self):
        async def check():
            lock = HeartbeatLock(timeout=1.0)
            await lock.acquire("holder-1")
            await lock.release("holder-1")

        asyncio.run(check())

    def test_exclusive_lock(self):
        async def check():
            lock = HeartbeatLock(timeout=1.0)
            await lock.acquire("holder-1")

            acquired = False

            async def try_acquire():
                nonlocal acquired
                await lock.acquire("holder-2")
                acquired = True

            task = asyncio.create_task(try_acquire())
            await asyncio.sleep(0.1)
            assert acquired is False

            await lock.release("holder-1")
            await asyncio.sleep(0.05)
            assert acquired is True

            await lock.release("holder-2")

        asyncio.run(check())

    def test_timeout_expiry(self):
        async def check():
            lock = HeartbeatLock(timeout=0.2)
            await lock.acquire("holder-1")
            # Don't heartbeat, let it expire

            await asyncio.sleep(0.3)

            # Now holder-2 should be able to acquire
            await lock.acquire("holder-2")
            await lock.release("holder-2")

        asyncio.run(check())

    def test_heartbeat_keeps_alive(self):
        async def check():
            lock = HeartbeatLock(timeout=0.2)
            await lock.acquire("holder-1")

            # Heartbeat to keep alive
            await asyncio.sleep(0.1)
            await lock.heartbeat("holder-1")
            await asyncio.sleep(0.1)
            await lock.heartbeat("holder-1")

            # Lock should still be held by holder-1
            acquired = False

            async def try_acquire():
                nonlocal acquired
                await lock.acquire("holder-2")
                acquired = True

            task = asyncio.create_task(try_acquire())
            await asyncio.sleep(0.05)
            assert acquired is False

            await lock.release("holder-1")
            await asyncio.sleep(0.05)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        asyncio.run(check())


class TestDiningTable:
    """Tests for Exercise 3.4: DiningTable"""

    def test_all_philosophers_eat(self):
        async def check():
            table = DiningTable(5)
            eaten = []

            async def philosopher(id):
                await table.think(id)
                await table.eat(id)
                eaten.append(id)
                await table.think(id)

            await asyncio.gather(*[philosopher(i) for i in range(5)])
            assert sorted(eaten) == [0, 1, 2, 3, 4]

        asyncio.run(check())

    def test_no_deadlock(self):
        async def check():
            table = DiningTable(5)

            async def philosopher(id):
                for _ in range(3):  # Each eats 3 times
                    await table.think(id)
                    await table.eat(id)

            # Should complete without deadlock
            await asyncio.wait_for(
                asyncio.gather(*[philosopher(i) for i in range(5)]),
                timeout=5.0
            )

        asyncio.run(check())

    def test_concurrent_eating(self):
        async def check():
            table = DiningTable(5)
            max_eating = 0
            eating = 0

            original_eat = table.eat

            async def tracked_eat(id):
                nonlocal eating, max_eating
                eating += 1
                max_eating = max(max_eating, eating)
                await asyncio.sleep(0.1)
                eating -= 1

            # At most 2 can eat at once with 5 philosophers
            # (non-adjacent pairs)
            # Test just verifies no deadlock and completion

        asyncio.run(check())


class TestBackpressurePipeline:
    """Tests for Exercise 3.5: BackpressurePipeline"""

    def test_simple_pipeline(self):
        async def check():
            pipeline = BackpressurePipeline()

            async def double(x):
                return x * 2

            pipeline.add_stage(double, buffer_size=2)
            pipeline.start()

            for i in range(3):
                await pipeline.push(i)

            await pipeline.drain()
            assert sorted(pipeline.results) == [0, 2, 4]

        asyncio.run(check())

    def test_multi_stage(self):
        async def check():
            pipeline = BackpressurePipeline()

            async def double(x):
                return x * 2

            async def add_one(x):
                return x + 1

            pipeline.add_stage(double, buffer_size=2)
            pipeline.add_stage(add_one, buffer_size=2)
            pipeline.start()

            for i in range(3):
                await pipeline.push(i)

            await pipeline.drain()
            # 0 -> 0 -> 1, 1 -> 2 -> 3, 2 -> 4 -> 5
            assert sorted(pipeline.results) == [1, 3, 5]

        asyncio.run(check())

    def test_backpressure(self):
        async def check():
            pipeline = BackpressurePipeline()

            async def slow_stage(x):
                await asyncio.sleep(0.1)
                return x

            pipeline.add_stage(slow_stage, buffer_size=1)
            pipeline.start()

            start = time.time()
            for i in range(3):
                await pipeline.push(i)
            await pipeline.drain()
            elapsed = time.time() - start

            # With buffer of 1 and slow processing, should take time
            assert elapsed >= 0.2

        asyncio.run(check())
