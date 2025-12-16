"""
Tests for Exercise 3 (Hard): Production-Ready Async Patterns
Run with: python -m pytest module_05_advanced_patterns/exercises/test_hard.py -v
"""

import asyncio
import time
import pytest

from exercise_hard import (
    Message,
    Actor,
    EchoActor,
    AsyncStateMachine,
    HealthyPool,
    AsyncScheduler,
    DistributedLock,
)


class TestActorSystem:
    """Tests for Exercise 3.1: Actor System"""

    def test_echo_actor(self):
        async def check():
            echo = EchoActor()
            await echo.start()

            reply_queue = asyncio.Queue()
            await echo.send(Message("echo", "hello", reply_queue))
            response = await asyncio.wait_for(reply_queue.get(), timeout=1.0)

            assert response == "hello"
            await echo.stop()

        asyncio.run(check())

    def test_multiple_messages(self):
        async def check():
            echo = EchoActor()
            await echo.start()

            reply1 = asyncio.Queue()
            reply2 = asyncio.Queue()

            await echo.send(Message("echo", "first", reply1))
            await echo.send(Message("echo", "second", reply2))

            r1 = await asyncio.wait_for(reply1.get(), timeout=1.0)
            r2 = await asyncio.wait_for(reply2.get(), timeout=1.0)

            assert r1 == "first"
            assert r2 == "second"
            await echo.stop()

        asyncio.run(check())


class TestAsyncStateMachine:
    """Tests for Exercise 3.2: AsyncStateMachine"""

    def test_simple_transition(self):
        async def check():
            sm = AsyncStateMachine(initial="idle")
            sm.add_transition("idle", "start", "running")

            assert sm.current_state == "idle"
            await sm.trigger("start")
            assert sm.current_state == "running"

        asyncio.run(check())

    def test_guard_blocks_transition(self):
        async def check():
            sm = AsyncStateMachine(initial="idle")

            async def always_false():
                return False

            sm.add_transition("idle", "start", "running", guard=always_false)

            await sm.trigger("start")
            assert sm.current_state == "idle"  # Didn't transition

        asyncio.run(check())

    def test_action_executed(self):
        async def check():
            log = []

            async def on_transition():
                log.append("transitioned")

            sm = AsyncStateMachine(initial="idle")
            sm.add_transition("idle", "go", "done", action=on_transition)

            await sm.trigger("go")
            assert "transitioned" in log

        asyncio.run(check())


class TestHealthyPool:
    """Tests for Exercise 3.3: HealthyPool"""

    def test_acquire_release(self):
        async def check():
            async def factory():
                return {"healthy": True}

            async def health_check(obj):
                return obj.get("healthy", False)

            pool = HealthyPool(
                factory=factory,
                health_check=health_check,
                min_size=2,
                check_interval=10.0
            )
            await pool.start()

            async with pool.acquire() as obj:
                assert obj is not None

            await pool.stop()

        asyncio.run(check())

    def test_maintains_min_size(self):
        async def check():
            created = [0]

            async def factory():
                created[0] += 1
                return {"id": created[0]}

            async def health_check(obj):
                return True

            pool = HealthyPool(
                factory=factory,
                health_check=health_check,
                min_size=3,
                check_interval=10.0
            )
            await pool.start()
            await asyncio.sleep(0.1)

            assert created[0] >= 3

            await pool.stop()

        asyncio.run(check())


class TestAsyncScheduler:
    """Tests for Exercise 3.4: AsyncScheduler"""

    def test_schedule_once(self):
        async def check():
            scheduler = AsyncScheduler()
            await scheduler.start()

            executed = []

            async def job():
                executed.append(time.time())

            scheduler.schedule_once(0.1, job)
            await asyncio.sleep(0.2)

            assert len(executed) == 1
            await scheduler.stop()

        asyncio.run(check())

    def test_schedule_interval(self):
        async def check():
            scheduler = AsyncScheduler()
            await scheduler.start()

            count = [0]

            async def job():
                count[0] += 1

            job_id = scheduler.schedule_interval(0.1, job)
            await asyncio.sleep(0.35)
            scheduler.cancel(job_id)

            assert count[0] >= 3
            await scheduler.stop()

        asyncio.run(check())

    def test_cancel(self):
        async def check():
            scheduler = AsyncScheduler()
            await scheduler.start()

            executed = []

            async def job():
                executed.append(True)

            job_id = scheduler.schedule_once(0.2, job)
            scheduler.cancel(job_id)
            await asyncio.sleep(0.3)

            assert len(executed) == 0
            await scheduler.stop()

        asyncio.run(check())


class TestDistributedLock:
    """Tests for Exercise 3.5: DistributedLock"""

    def test_acquire_release(self):
        async def check():
            lock = DistributedLock()
            acquired = await lock.acquire("holder-1", ttl=1.0)
            assert acquired is True
            await lock.release("holder-1")

        asyncio.run(check())

    def test_exclusive(self):
        async def check():
            lock = DistributedLock()
            await lock.acquire("holder-1", ttl=1.0)
            acquired = await lock.acquire("holder-2", ttl=1.0)
            assert acquired is False
            await lock.release("holder-1")

        asyncio.run(check())

    def test_ttl_expiry(self):
        async def check():
            lock = DistributedLock()
            await lock.acquire("holder-1", ttl=0.1)
            await asyncio.sleep(0.15)

            # Lock should have expired
            acquired = await lock.acquire("holder-2", ttl=1.0)
            assert acquired is True
            await lock.release("holder-2")

        asyncio.run(check())

    def test_extend(self):
        async def check():
            lock = DistributedLock()
            await lock.acquire("holder-1", ttl=0.1)
            await lock.extend("holder-1", ttl=0.5)
            await asyncio.sleep(0.15)

            # Lock should still be held (extended)
            acquired = await lock.acquire("holder-2", ttl=1.0)
            assert acquired is False

            await lock.release("holder-1")

        asyncio.run(check())

    def test_wrong_holder_release(self):
        async def check():
            lock = DistributedLock()
            await lock.acquire("holder-1", ttl=1.0)

            # Wrong holder can't release
            await lock.release("holder-2")

            # Lock should still be held
            acquired = await lock.acquire("holder-2", ttl=1.0)
            assert acquired is False

            await lock.release("holder-1")

        asyncio.run(check())
