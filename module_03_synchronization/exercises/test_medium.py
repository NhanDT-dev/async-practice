"""
Tests for Exercise 2 (Medium): Advanced Synchronization Patterns
Run with: python -m pytest module_03_synchronization/exercises/test_medium.py -v
"""

import asyncio
import time
import pytest

from exercise_medium import (
    SimpleAsyncQueue,
    ReadWriteLock,
    ActionBarrier,
    TimeoutSemaphore,
    AsyncPubSub,
)


class TestSimpleAsyncQueue:
    """Tests for Exercise 2.1: SimpleAsyncQueue"""

    def test_put_get(self):
        async def check():
            queue = SimpleAsyncQueue(maxsize=3)
            await queue.put("a")
            item = await queue.get()
            assert item == "a"

        asyncio.run(check())

    def test_fifo_order(self):
        async def check():
            queue = SimpleAsyncQueue(maxsize=3)
            await queue.put("a")
            await queue.put("b")
            await queue.put("c")
            assert await queue.get() == "a"
            assert await queue.get() == "b"
            assert await queue.get() == "c"

        asyncio.run(check())

    def test_blocks_when_full(self):
        async def check():
            queue = SimpleAsyncQueue(maxsize=2)
            await queue.put("a")
            await queue.put("b")

            async def delayed_get():
                await asyncio.sleep(0.1)
                return await queue.get()

            start = time.time()
            await asyncio.gather(
                queue.put("c"),  # Blocks until get
                delayed_get()
            )
            elapsed = time.time() - start
            assert elapsed >= 0.1

        asyncio.run(check())

    def test_blocks_when_empty(self):
        async def check():
            queue = SimpleAsyncQueue(maxsize=2)

            async def delayed_put():
                await asyncio.sleep(0.1)
                await queue.put("item")

            start = time.time()
            await asyncio.gather(
                queue.get(),  # Blocks until put
                delayed_put()
            )
            elapsed = time.time() - start
            assert elapsed >= 0.1

        asyncio.run(check())

    def test_qsize_and_empty(self):
        async def check():
            queue = SimpleAsyncQueue(maxsize=3)
            assert queue.empty() is True
            assert queue.qsize() == 0

            await queue.put("a")
            assert queue.empty() is False
            assert queue.qsize() == 1

        asyncio.run(check())


class TestReadWriteLock:
    """Tests for Exercise 2.2: ReadWriteLock"""

    def test_multiple_readers(self):
        async def check():
            rwlock = ReadWriteLock()
            readers_inside = 0
            max_readers = 0

            async def reader():
                nonlocal readers_inside, max_readers
                async with rwlock.read_lock():
                    readers_inside += 1
                    max_readers = max(max_readers, readers_inside)
                    await asyncio.sleep(0.1)
                    readers_inside -= 1

            await asyncio.gather(*[reader() for _ in range(5)])
            assert max_readers > 1  # Multiple readers at same time

        asyncio.run(check())

    def test_writer_exclusive(self):
        async def check():
            rwlock = ReadWriteLock()
            writers_inside = 0
            max_writers = 0

            async def writer():
                nonlocal writers_inside, max_writers
                async with rwlock.write_lock():
                    writers_inside += 1
                    max_writers = max(max_writers, writers_inside)
                    await asyncio.sleep(0.05)
                    writers_inside -= 1

            await asyncio.gather(*[writer() for _ in range(3)])
            assert max_writers == 1  # Only one writer at a time

        asyncio.run(check())

    def test_writer_blocks_readers(self):
        async def check():
            rwlock = ReadWriteLock()
            log = []

            async def writer():
                async with rwlock.write_lock():
                    log.append("writer_start")
                    await asyncio.sleep(0.1)
                    log.append("writer_end")

            async def reader():
                await asyncio.sleep(0.02)  # Start after writer
                async with rwlock.read_lock():
                    log.append("reader")

            await asyncio.gather(writer(), reader())
            # Reader should come after writer ends
            assert log.index("reader") > log.index("writer_end")

        asyncio.run(check())


class TestActionBarrier:
    """Tests for Exercise 2.3: ActionBarrier"""

    def test_all_arrive(self):
        async def check():
            action_called = []

            def action():
                action_called.append(True)

            barrier = ActionBarrier(3, action)

            async def worker():
                await barrier.wait()

            await asyncio.gather(*[worker() for _ in range(3)])
            assert len(action_called) == 1

        asyncio.run(check())

    def test_action_runs_once(self):
        async def check():
            count = [0]

            def action():
                count[0] += 1

            barrier = ActionBarrier(3, action)

            async def worker():
                await barrier.wait()

            await asyncio.gather(*[worker() for _ in range(3)])
            assert count[0] == 1

        asyncio.run(check())

    def test_order(self):
        async def check():
            log = []

            def action():
                log.append("SYNC")

            barrier = ActionBarrier(2, action)

            async def worker(name):
                log.append(f"{name}-before")
                await barrier.wait()
                log.append(f"{name}-after")

            await asyncio.gather(worker("A"), worker("B"))

            # All "before" should come before SYNC
            sync_idx = log.index("SYNC")
            before_indices = [log.index(x) for x in log if "before" in x]
            after_indices = [log.index(x) for x in log if "after" in x]

            assert all(i < sync_idx for i in before_indices)
            assert all(i > sync_idx for i in after_indices)

        asyncio.run(check())


class TestTimeoutSemaphore:
    """Tests for Exercise 2.4: TimeoutSemaphore"""

    def test_acquire_release(self):
        async def check():
            sem = TimeoutSemaphore(2, default_timeout=1.0)
            acquired = await sem.acquire(timeout=0.5)
            assert acquired is True
            sem.release()

        asyncio.run(check())

    def test_timeout_on_full(self):
        async def check():
            sem = TimeoutSemaphore(1, default_timeout=1.0)
            await sem.acquire(timeout=1.0)  # Take the only slot

            start = time.time()
            acquired = await sem.acquire(timeout=0.1)  # Should timeout
            elapsed = time.time() - start

            assert acquired is False
            assert elapsed >= 0.1
            assert elapsed < 0.2

        asyncio.run(check())

    def test_context_manager(self):
        async def check():
            sem = TimeoutSemaphore(1, default_timeout=1.0)

            async with sem:
                pass  # Should work

        asyncio.run(check())


class TestAsyncPubSub:
    """Tests for Exercise 2.5: AsyncPubSub"""

    def test_single_subscriber(self):
        async def check():
            pubsub = AsyncPubSub()
            received = []

            async def subscriber():
                async for msg in pubsub.subscribe("topic"):
                    received.append(msg)
                    if msg == "stop":
                        break

            async def publisher():
                await asyncio.sleep(0.05)
                await pubsub.publish("topic", "hello")
                await pubsub.publish("topic", "stop")

            await asyncio.gather(subscriber(), publisher())
            assert received == ["hello", "stop"]

        asyncio.run(check())

    def test_multiple_subscribers(self):
        async def check():
            pubsub = AsyncPubSub()
            received_a = []
            received_b = []

            async def subscriber(name, storage):
                async for msg in pubsub.subscribe("topic"):
                    storage.append(msg)
                    if msg == "stop":
                        break

            async def publisher():
                await asyncio.sleep(0.05)
                await pubsub.publish("topic", "msg")
                await pubsub.publish("topic", "stop")

            await asyncio.gather(
                subscriber("A", received_a),
                subscriber("B", received_b),
                publisher()
            )

            assert received_a == ["msg", "stop"]
            assert received_b == ["msg", "stop"]

        asyncio.run(check())

    def test_different_topics(self):
        async def check():
            pubsub = AsyncPubSub()
            received = []

            async def subscriber():
                async for msg in pubsub.subscribe("topic_a"):
                    received.append(msg)
                    if msg == "stop":
                        break

            async def publisher():
                await asyncio.sleep(0.05)
                await pubsub.publish("topic_b", "ignored")
                await pubsub.publish("topic_a", "received")
                await pubsub.publish("topic_a", "stop")

            await asyncio.gather(subscriber(), publisher())
            assert "ignored" not in received
            assert "received" in received

        asyncio.run(check())
