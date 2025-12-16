"""
Solutions for Exercise 1 (Easy): Basic Synchronization Primitives

Study these solutions AFTER attempting the exercises yourself!
"""

import asyncio
import time


# =============================================================================
# Solution 1.1: Safe Counter with Lock
# =============================================================================
class SafeCounter:
    def __init__(self):
        self._value = 0
        self._lock = asyncio.Lock()

    @property
    def value(self) -> int:
        return self._value

    async def increment(self):
        async with self._lock:
            current = self._value
            await asyncio.sleep(0.001)  # Simulate async work
            self._value = current + 1


# =============================================================================
# Solution 1.2: Event-based Start Signal
# =============================================================================
async def run_with_start_signal(
    worker_names: list[str],
    start_event: asyncio.Event
) -> dict[str, float]:
    results = {}

    async def worker(name: str):
        await start_event.wait()
        await asyncio.sleep(0.1)  # Work
        results[name] = time.time()

    await asyncio.gather(*[worker(name) for name in worker_names])
    return results


# =============================================================================
# Solution 1.3: Limited Concurrent Access
# =============================================================================
async def rate_limited_fetch(urls: list[str], max_concurrent: int) -> list[str]:
    semaphore = asyncio.Semaphore(max_concurrent)
    results = []

    async def fetch(url: str) -> str:
        async with semaphore:
            await asyncio.sleep(0.1)
            return f"Fetched: {url}"

    results = await asyncio.gather(*[fetch(url) for url in urls])
    return list(results)


# =============================================================================
# Solution 1.4: Event Toggle
# =============================================================================
class AsyncToggle:
    def __init__(self):
        self._event = asyncio.Event()

    @property
    def is_on(self) -> bool:
        return self._event.is_set()

    def turn_on(self):
        self._event.set()

    def turn_off(self):
        self._event.clear()

    async def wait_for_on(self):
        await self._event.wait()


# =============================================================================
# Solution 1.5: Mutex-protected Resource
# =============================================================================
class SharedResource:
    def __init__(self):
        self.data = []
        self._lock = asyncio.Lock()

    async def add(self, item):
        async with self._lock:
            await asyncio.sleep(0.05)
            self.data.append(item)

    async def get_all(self) -> list:
        async with self._lock:
            return self.data.copy()


# =============================================================================
# Test runner
# =============================================================================
if __name__ == "__main__":
    async def main():
        print("Testing SafeCounter:")
        counter = SafeCounter()
        await asyncio.gather(*[counter.increment() for _ in range(100)])
        print(f"Counter value: {counter.value}")

        print("\nTesting run_with_start_signal:")
        event = asyncio.Event()

        async def delayed_set():
            await asyncio.sleep(0.2)
            print("Setting event!")
            event.set()

        results, _ = await asyncio.gather(
            run_with_start_signal(["A", "B", "C"], event),
            delayed_set()
        )
        print(f"Workers completed: {list(results.keys())}")

        print("\nTesting rate_limited_fetch:")
        start = time.time()
        results = await rate_limited_fetch(["a", "b", "c", "d"], 2)
        print(f"Results: {results}")
        print(f"Time: {time.time() - start:.2f}s")

        print("\nTesting AsyncToggle:")
        toggle = AsyncToggle()
        print(f"Initial state: {toggle.is_on}")
        toggle.turn_on()
        print(f"After turn_on: {toggle.is_on}")

        print("\nTesting SharedResource:")
        resource = SharedResource()
        await asyncio.gather(*[resource.add(i) for i in range(10)])
        data = await resource.get_all()
        print(f"Data: {sorted(data)}")

    asyncio.run(main())
