"""
Solutions for Exercise 3 (Hard): Production-Ready Async Patterns

Study these solutions AFTER attempting the exercises yourself!
"""

import asyncio
import time
from typing import Any, Callable, Awaitable, Optional
from dataclasses import dataclass
from contextlib import asynccontextmanager


# =============================================================================
# Solution 3.1: Async Actor System
# =============================================================================
@dataclass
class Message:
    type: str
    payload: Any
    reply_to: Optional[asyncio.Queue] = None


class Actor:
    def __init__(self):
        self._mailbox = asyncio.Queue()
        self._running = False
        self._task = None

    async def start(self):
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self):
        self._running = False
        await self._mailbox.put(None)  # Sentinel
        if self._task:
            await self._task

    async def send(self, message: Message):
        await self._mailbox.put(message)

    async def _run(self):
        while self._running:
            message = await self._mailbox.get()
            if message is None:
                break
            await self.receive(message)

    async def receive(self, message: Message):
        pass  # Override in subclass


class EchoActor(Actor):
    async def receive(self, message: Message):
        if message.reply_to:
            await message.reply_to.put(message.payload)


# =============================================================================
# Solution 3.2: Async State Machine
# =============================================================================
class AsyncStateMachine:
    def __init__(self, initial: str):
        self._current_state = initial
        self._transitions = {}

    @property
    def current_state(self) -> str:
        return self._current_state

    def add_transition(
        self,
        from_state: str,
        event: str,
        to_state: str,
        guard: Callable[[], Awaitable[bool]] = None,
        action: Callable[[], Awaitable[None]] = None
    ):
        key = (from_state, event)
        self._transitions[key] = (to_state, guard, action)

    async def trigger(self, event: str) -> bool:
        key = (self._current_state, event)
        if key not in self._transitions:
            return False

        to_state, guard, action = self._transitions[key]

        if guard:
            if not await guard():
                return False

        if action:
            await action()

        self._current_state = to_state
        return True


# =============================================================================
# Solution 3.3: Async Object Pool with Health Checks
# =============================================================================
class HealthyPool:
    def __init__(
        self,
        factory: Callable[[], Awaitable[Any]],
        health_check: Callable[[Any], Awaitable[bool]],
        min_size: int,
        check_interval: float
    ):
        self.factory = factory
        self.health_check = health_check
        self.min_size = min_size
        self.check_interval = check_interval
        self._pool = asyncio.Queue()
        self._all_objects = []
        self._running = False
        self._check_task = None

    async def start(self):
        self._running = True
        await self._ensure_min_size()
        self._check_task = asyncio.create_task(self._health_check_loop())

    async def stop(self):
        self._running = False
        if self._check_task:
            self._check_task.cancel()
            try:
                await self._check_task
            except asyncio.CancelledError:
                pass

    async def _ensure_min_size(self):
        while len(self._all_objects) < self.min_size:
            obj = await self.factory()
            self._all_objects.append(obj)
            await self._pool.put(obj)

    async def _health_check_loop(self):
        while self._running:
            await asyncio.sleep(self.check_interval)
            # Check and remove unhealthy objects
            healthy = []
            for obj in self._all_objects:
                if await self.health_check(obj):
                    healthy.append(obj)
            self._all_objects = healthy
            await self._ensure_min_size()

    @asynccontextmanager
    async def acquire(self):
        obj = await self._pool.get()
        try:
            yield obj
        finally:
            if obj in self._all_objects:
                await self._pool.put(obj)


# =============================================================================
# Solution 3.4: Async Job Scheduler
# =============================================================================
class AsyncScheduler:
    def __init__(self):
        self._jobs = {}
        self._next_id = 0
        self._running = False
        self._tasks = []

    async def start(self):
        self._running = True

    async def stop(self):
        self._running = False
        for task in self._tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    def schedule_once(
        self,
        delay: float,
        job: Callable[[], Awaitable[None]]
    ) -> int:
        job_id = self._next_id
        self._next_id += 1

        async def run_once():
            await asyncio.sleep(delay)
            if job_id in self._jobs:
                await job()
                del self._jobs[job_id]

        self._jobs[job_id] = True
        task = asyncio.create_task(run_once())
        self._tasks.append(task)
        return job_id

    def schedule_interval(
        self,
        interval: float,
        job: Callable[[], Awaitable[None]]
    ) -> int:
        job_id = self._next_id
        self._next_id += 1

        async def run_interval():
            while job_id in self._jobs:
                await asyncio.sleep(interval)
                if job_id in self._jobs:
                    await job()

        self._jobs[job_id] = True
        task = asyncio.create_task(run_interval())
        self._tasks.append(task)
        return job_id

    def cancel(self, job_id: int):
        if job_id in self._jobs:
            del self._jobs[job_id]


# =============================================================================
# Solution 3.5: Async Distributed Lock
# =============================================================================
class DistributedLock:
    def __init__(self):
        self._holder = None
        self._expiry = 0
        self._lock = asyncio.Lock()

    async def acquire(self, holder_id: str, ttl: float) -> bool:
        async with self._lock:
            now = time.monotonic()
            if self._holder is None or now > self._expiry:
                self._holder = holder_id
                self._expiry = now + ttl
                return True
            return False

    async def release(self, holder_id: str):
        async with self._lock:
            if self._holder == holder_id:
                self._holder = None
                self._expiry = 0

    async def extend(self, holder_id: str, ttl: float) -> bool:
        async with self._lock:
            if self._holder == holder_id:
                self._expiry = time.monotonic() + ttl
                return True
            return False


# =============================================================================
# Test runner
# =============================================================================
if __name__ == "__main__":
    async def main():
        print("=" * 60)
        print("Testing Actor System:")
        print("=" * 60)
        echo = EchoActor()
        await echo.start()

        reply = asyncio.Queue()
        await echo.send(Message("echo", "Hello, Actor!", reply))
        response = await reply.get()
        print(f"  Response: {response}")
        await echo.stop()

        print("\n" + "=" * 60)
        print("Testing AsyncStateMachine:")
        print("=" * 60)
        sm = AsyncStateMachine(initial="idle")

        async def on_start():
            print("  Starting!")

        sm.add_transition("idle", "start", "running", action=on_start)
        sm.add_transition("running", "stop", "idle")

        print(f"  State: {sm.current_state}")
        await sm.trigger("start")
        print(f"  State: {sm.current_state}")
        await sm.trigger("stop")
        print(f"  State: {sm.current_state}")

        print("\n" + "=" * 60)
        print("Testing HealthyPool:")
        print("=" * 60)

        async def create():
            return {"healthy": True, "id": time.time()}

        async def check(obj):
            return obj.get("healthy", False)

        pool = HealthyPool(create, check, min_size=2, check_interval=10)
        await pool.start()

        async with pool.acquire() as obj:
            print(f"  Got object: {obj}")

        await pool.stop()

        print("\n" + "=" * 60)
        print("Testing AsyncScheduler:")
        print("=" * 60)
        scheduler = AsyncScheduler()
        await scheduler.start()

        count = [0]

        async def job():
            count[0] += 1
            print(f"  Job executed (count={count[0]})")

        scheduler.schedule_once(0.1, job)
        interval_id = scheduler.schedule_interval(0.1, job)

        await asyncio.sleep(0.35)
        scheduler.cancel(interval_id)
        await scheduler.stop()

        print("\n" + "=" * 60)
        print("Testing DistributedLock:")
        print("=" * 60)
        lock = DistributedLock()

        acquired1 = await lock.acquire("worker-1", ttl=1.0)
        print(f"  Worker-1 acquired: {acquired1}")

        acquired2 = await lock.acquire("worker-2", ttl=1.0)
        print(f"  Worker-2 acquired: {acquired2}")

        await lock.release("worker-1")
        acquired2 = await lock.acquire("worker-2", ttl=1.0)
        print(f"  Worker-2 acquired after release: {acquired2}")

        await lock.release("worker-2")

    asyncio.run(main())
