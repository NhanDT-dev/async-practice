"""
Solutions for Exercise 2 (Medium): Advanced Synchronization Patterns

Study these solutions AFTER attempting the exercises yourself!
"""

import asyncio
from typing import Any
from collections import deque, defaultdict
from contextlib import asynccontextmanager


# =============================================================================
# Solution 2.1: Async Queue Implementation
# =============================================================================
class SimpleAsyncQueue:
    def __init__(self, maxsize: int):
        self.maxsize = maxsize
        self._queue = deque()
        self._condition = asyncio.Condition()

    async def put(self, item):
        async with self._condition:
            while len(self._queue) >= self.maxsize:
                await self._condition.wait()
            self._queue.append(item)
            self._condition.notify()

    async def get(self):
        async with self._condition:
            while not self._queue:
                await self._condition.wait()
            item = self._queue.popleft()
            self._condition.notify()
            return item

    def qsize(self) -> int:
        return len(self._queue)

    def empty(self) -> bool:
        return len(self._queue) == 0


# =============================================================================
# Solution 2.2: Read-Write Lock
# =============================================================================
class ReadWriteLock:
    def __init__(self):
        self._readers = 0
        self._writer = False
        self._condition = asyncio.Condition()

    @asynccontextmanager
    async def read_lock(self):
        async with self._condition:
            while self._writer:
                await self._condition.wait()
            self._readers += 1

        try:
            yield
        finally:
            async with self._condition:
                self._readers -= 1
                if self._readers == 0:
                    self._condition.notify_all()

    @asynccontextmanager
    async def write_lock(self):
        async with self._condition:
            while self._writer or self._readers > 0:
                await self._condition.wait()
            self._writer = True

        try:
            yield
        finally:
            async with self._condition:
                self._writer = False
                self._condition.notify_all()


# =============================================================================
# Solution 2.3: Async Barrier with Action
# =============================================================================
class ActionBarrier:
    def __init__(self, parties: int, action):
        self._parties = parties
        self._action = action
        self._count = 0
        self._generation = 0
        self._condition = asyncio.Condition()

    async def wait(self):
        async with self._condition:
            generation = self._generation
            self._count += 1

            if self._count == self._parties:
                # Last one to arrive
                self._action()
                self._count = 0
                self._generation += 1
                self._condition.notify_all()
            else:
                # Wait for others
                while generation == self._generation:
                    await self._condition.wait()


# =============================================================================
# Solution 2.4: Semaphore with Timeout
# =============================================================================
class TimeoutSemaphore:
    def __init__(self, value: int, default_timeout: float):
        self._semaphore = asyncio.Semaphore(value)
        self._default_timeout = default_timeout

    async def acquire(self, timeout: float = None) -> bool:
        if timeout is None:
            timeout = self._default_timeout

        try:
            await asyncio.wait_for(
                self._semaphore.acquire(),
                timeout=timeout
            )
            return True
        except asyncio.TimeoutError:
            return False

    def release(self):
        self._semaphore.release()

    async def __aenter__(self):
        acquired = await self.acquire()
        if not acquired:
            raise asyncio.TimeoutError("Could not acquire semaphore")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False


# =============================================================================
# Solution 2.5: Event-based Pub/Sub
# =============================================================================
class AsyncPubSub:
    def __init__(self):
        self._subscribers: dict[str, list[asyncio.Queue]] = defaultdict(list)

    async def subscribe(self, topic: str):
        queue = asyncio.Queue()
        self._subscribers[topic].append(queue)
        try:
            while True:
                message = await queue.get()
                yield message
        finally:
            self._subscribers[topic].remove(queue)

    async def publish(self, topic: str, message: Any):
        for queue in self._subscribers.get(topic, []):
            await queue.put(message)


# =============================================================================
# Test runner
# =============================================================================
if __name__ == "__main__":
    async def main():
        print("Testing SimpleAsyncQueue:")
        queue = SimpleAsyncQueue(maxsize=3)
        await queue.put("a")
        await queue.put("b")
        print(f"Size: {queue.qsize()}, Empty: {queue.empty()}")
        print(f"Get: {await queue.get()}")

        print("\nTesting ReadWriteLock:")
        rwlock = ReadWriteLock()

        async def reader(name):
            async with rwlock.read_lock():
                print(f"  {name} reading")
                await asyncio.sleep(0.1)

        async def writer(name):
            async with rwlock.write_lock():
                print(f"  {name} writing")
                await asyncio.sleep(0.1)

        await asyncio.gather(
            reader("R1"), reader("R2"), writer("W1")
        )

        print("\nTesting ActionBarrier:")
        log = []

        def action():
            log.append("SYNC")

        barrier = ActionBarrier(3, action)

        async def worker(name):
            log.append(f"{name}-before")
            await barrier.wait()
            log.append(f"{name}-after")

        await asyncio.gather(worker("A"), worker("B"), worker("C"))
        print(f"Log: {log}")

        print("\nTesting TimeoutSemaphore:")
        sem = TimeoutSemaphore(1, default_timeout=1.0)
        print(f"Acquire 1: {await sem.acquire(0.5)}")
        print(f"Acquire 2 (should timeout): {await sem.acquire(0.1)}")
        sem.release()

        print("\nTesting AsyncPubSub:")
        pubsub = AsyncPubSub()
        received = []

        async def subscriber():
            async for msg in pubsub.subscribe("test"):
                received.append(msg)
                if msg == "stop":
                    break

        async def publisher():
            await asyncio.sleep(0.05)
            await pubsub.publish("test", "hello")
            await pubsub.publish("test", "stop")

        await asyncio.gather(subscriber(), publisher())
        print(f"Received: {received}")

    asyncio.run(main())
