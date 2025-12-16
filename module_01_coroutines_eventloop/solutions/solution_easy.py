"""
Solutions for Exercise 1 (Easy): Basic Coroutines

Study these solutions AFTER attempting the exercises yourself!
"""

import asyncio


# =============================================================================
# Solution 1.1: Simple Coroutine
# =============================================================================
async def say_hello(name: str) -> str:
    return f"Hello, {name}!"


# =============================================================================
# Solution 1.2: Coroutine with Delay
# =============================================================================
async def delayed_message(message: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return message


# =============================================================================
# Solution 1.3: Sequential Coroutines
# =============================================================================
async def count_to_n(n: int) -> list[int]:
    result = []
    for i in range(1, n + 1):
        await asyncio.sleep(0.1)
        result.append(i)
    return result


# =============================================================================
# Solution 1.4: Calling Coroutines from Coroutines
# =============================================================================
async def greet_twice(name: str) -> tuple[str, str]:
    first = await say_hello(name)
    second = await say_hello(name)
    return (first, second)


# =============================================================================
# Solution 1.5: Conditional Async
# =============================================================================
async def fetch_data(data_id: int) -> str:
    if data_id > 0:
        await asyncio.sleep(0.1)
        return f"Data-{data_id}"
    else:
        return "Invalid ID"


# =============================================================================
# Test runner
# =============================================================================
if __name__ == "__main__":
    # Test each solution
    print("Testing say_hello:")
    print(asyncio.run(say_hello("World")))

    print("\nTesting delayed_message:")
    print(asyncio.run(delayed_message("Hello!", 0.5)))

    print("\nTesting count_to_n:")
    print(asyncio.run(count_to_n(5)))

    print("\nTesting greet_twice:")
    print(asyncio.run(greet_twice("Python")))

    print("\nTesting fetch_data:")
    print(asyncio.run(fetch_data(42)))
    print(asyncio.run(fetch_data(-1)))
