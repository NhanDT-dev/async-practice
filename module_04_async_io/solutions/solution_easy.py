"""
Solutions for Exercise 1 (Easy): Basic Async I/O

Study these solutions AFTER attempting the exercises yourself!
"""

import asyncio
from typing import Any, Callable, Awaitable, TypeVar

T = TypeVar('T')
R = TypeVar('R')


# =============================================================================
# Solution 1.1: Simulated File Reader
# =============================================================================
async def read_file_async(filename: str, file_contents: dict[str, str]) -> str:
    await asyncio.sleep(0.1)  # Simulate I/O delay
    if filename not in file_contents:
        raise FileNotFoundError(f"File not found: {filename}")
    return file_contents[filename]


# =============================================================================
# Solution 1.2: Simulated HTTP Client
# =============================================================================
class MockHttpClient:
    def __init__(self, responses: dict[str, Any]):
        self._responses = responses

    async def get(self, url: str) -> dict:
        await asyncio.sleep(0.1)
        if url in self._responses:
            return self._responses[url]
        return {"error": "Not Found"}

    async def post(self, url: str, data: Any) -> dict:
        await asyncio.sleep(0.1)
        return {"status": "created", "data": data}


# =============================================================================
# Solution 1.3: Parallel File Reader
# =============================================================================
async def read_files_parallel(
    filenames: list[str],
    file_contents: dict[str, str]
) -> dict[str, str]:
    async def safe_read(filename: str):
        try:
            content = await read_file_async(filename, file_contents)
            return (filename, content)
        except FileNotFoundError:
            return None

    results = await asyncio.gather(*[safe_read(f) for f in filenames])
    return {name: content for result in results if result for name, content in [result]}


# =============================================================================
# Solution 1.4: API Fetcher with Retry
# =============================================================================
async def fetch_with_retry(
    client: MockHttpClient,
    url: str,
    max_retries: int
) -> dict:
    for attempt in range(max_retries):
        result = await client.get(url)
        if "error" not in result:
            return result
        if attempt < max_retries - 1:
            await asyncio.sleep(0.05)
    return result


# =============================================================================
# Solution 1.5: Batch Processor
# =============================================================================
async def process_batch(
    items: list[T],
    processor: Callable[[T], Awaitable[R]]
) -> list[R]:
    results = await asyncio.gather(*[processor(item) for item in items])
    return list(results)


# =============================================================================
# Test runner
# =============================================================================
if __name__ == "__main__":
    async def main():
        print("Testing read_file_async:")
        files = {"a.txt": "Hello", "b.txt": "World"}
        content = await read_file_async("a.txt", files)
        print(f"Read: {content}")

        print("\nTesting MockHttpClient:")
        client = MockHttpClient({"http://api": {"data": [1, 2, 3]}})
        result = await client.get("http://api")
        print(f"GET: {result}")
        result = await client.post("http://api", {"name": "test"})
        print(f"POST: {result}")

        print("\nTesting read_files_parallel:")
        result = await read_files_parallel(["a.txt", "c.txt"], files)
        print(f"Parallel read: {result}")

        print("\nTesting fetch_with_retry:")
        result = await fetch_with_retry(client, "http://api", 3)
        print(f"Fetch: {result}")

        print("\nTesting process_batch:")

        async def double(x):
            await asyncio.sleep(0.01)
            return x * 2

        result = await process_batch([1, 2, 3, 4, 5], double)
        print(f"Batch: {result}")

    asyncio.run(main())
