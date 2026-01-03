"""
Exercise 1 (Easy): Basic Coroutines

Your task is to implement the following coroutines.
Run the tests to verify your solutions:
    python -m pytest module_01_coroutines_eventloop/exercises/test_easy.py -v
"""

import asyncio


# =============================================================================
# Exercise 1.1: Simple Coroutine
# =============================================================================
# Create a coroutine called `say_hello` that:
# - Takes a name (str) as parameter
# - Returns the string "Hello, {name}!"
#
# Example: say_hello("Alice") should return "Hello, Alice!"
# =============================================================================


async def say_hello(name: str) -> str:
    print(f"Hello {name}")
    pass


# =============================================================================
# Exercise 1.2: Coroutine with Delay
# =============================================================================
# Create a coroutine called `delayed_message` that:
# - Takes a message (str) and delay (float) as parameters
# - Waits for `delay` seconds using asyncio.sleep()
# - Returns the message after the delay
#
# Example: delayed_message("Hi", 1.0) waits 1 second, then returns "Hi"
# =============================================================================


async def delayed_message(message: str, delay: float) -> str:
    await asyncio.sleep(1.0)
    await say_hello(message)


# =============================================================================
# Exercise 1.3: Sequential Coroutines
# =============================================================================
# Create a coroutine called `count_to_n` that:
# - Takes an integer n as parameter
# - Counts from 1 to n, waiting 0.1 seconds between each count
# - Returns a list of all numbers [1, 2, 3, ..., n]
#
# Example: count_to_n(3) returns [1, 2, 3] after ~0.3 seconds
# =============================================================================


async def count_to_n(n: int) -> list[int]:
    list_result = []
    for i in range(0, n):
        await asyncio.sleep(0.1)
        list_result.append(i)
    return list_result


# =============================================================================
# Exercise 1.4: Calling Coroutines from Coroutines
# =============================================================================
# Create a coroutine called `greet_twice` that:
# - Takes a name (str) as parameter
# - Calls say_hello() twice with the same name
# - Returns both greetings as a tuple
#
# Example: greet_twice("Bob") returns ("Hello, Bob!", "Hello, Bob!")
# =============================================================================


async def greet_twice(name: str) -> tuple[str, str]:
    return await say_hello(name), await say_hello(name)


# =============================================================================
# Exercise 1.5: Conditional Async
# =============================================================================
# Create a coroutine called `fetch_data` that:
# - Takes a data_id (int) as parameter
# - If data_id is positive, wait 0.1 seconds and return f"Data-{data_id}"
# - If data_id is zero or negative, return "Invalid ID" immediately (no wait)
#
# Example:
#   fetch_data(5)  -> waits 0.1s, returns "Data-5"
#   fetch_data(-1) -> returns "Invalid ID" immediately
# =============================================================================


async def fetch_data(data_id: int) -> str:
    if data_id > 0:
        await asyncio.sleep(0.1)
        return f"Data-{data_id}"
    else:
        return "Invalid ID"
