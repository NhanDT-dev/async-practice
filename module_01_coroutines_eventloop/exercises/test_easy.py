"""
Tests for Exercise 1 (Easy): Basic Coroutines
Run with: python -m pytest module_01_coroutines_eventloop/exercises/test_easy.py -v
"""

import asyncio
import time
import pytest

from exercise_easy import (
    say_hello,
    delayed_message,
    count_to_n,
    greet_twice,
    fetch_data,
)


class TestSayHello:
    """Tests for Exercise 1.1: say_hello"""

    def test_basic_greeting(self):
        result = asyncio.run(say_hello("Alice"))
        assert result == "Hello, Alice!"

    def test_different_name(self):
        result = asyncio.run(say_hello("Bob"))
        assert result == "Hello, Bob!"

    def test_empty_name(self):
        result = asyncio.run(say_hello(""))
        assert result == "Hello, !"

    def test_name_with_spaces(self):
        result = asyncio.run(say_hello("John Doe"))
        assert result == "Hello, John Doe!"


class TestDelayedMessage:
    """Tests for Exercise 1.2: delayed_message"""

    def test_returns_message(self):
        result = asyncio.run(delayed_message("Hello", 0.1))
        assert result == "Hello"

    def test_delay_timing(self):
        start = time.time()
        asyncio.run(delayed_message("Test", 0.2))
        elapsed = time.time() - start
        assert 0.15 < elapsed < 0.35, f"Expected ~0.2s delay, got {elapsed}s"

    def test_zero_delay(self):
        start = time.time()
        result = asyncio.run(delayed_message("Quick", 0))
        elapsed = time.time() - start
        assert result == "Quick"
        assert elapsed < 0.1


class TestCountToN:
    """Tests for Exercise 1.3: count_to_n"""

    def test_count_to_three(self):
        result = asyncio.run(count_to_n(3))
        assert result == [1, 2, 3]

    def test_count_to_one(self):
        result = asyncio.run(count_to_n(1))
        assert result == [1]

    def test_count_to_five(self):
        result = asyncio.run(count_to_n(5))
        assert result == [1, 2, 3, 4, 5]

    def test_timing(self):
        start = time.time()
        asyncio.run(count_to_n(3))
        elapsed = time.time() - start
        # Should take ~0.3s (3 * 0.1s delays)
        assert 0.25 < elapsed < 0.5, f"Expected ~0.3s, got {elapsed}s"

    def test_count_to_zero(self):
        result = asyncio.run(count_to_n(0))
        assert result == []


class TestGreetTwice:
    """Tests for Exercise 1.4: greet_twice"""

    def test_basic_greet_twice(self):
        result = asyncio.run(greet_twice("Charlie"))
        assert result == ("Hello, Charlie!", "Hello, Charlie!")

    def test_returns_tuple(self):
        result = asyncio.run(greet_twice("Test"))
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestFetchData:
    """Tests for Exercise 1.5: fetch_data"""

    def test_positive_id(self):
        result = asyncio.run(fetch_data(5))
        assert result == "Data-5"

    def test_positive_id_timing(self):
        start = time.time()
        asyncio.run(fetch_data(10))
        elapsed = time.time() - start
        assert elapsed >= 0.1, "Positive ID should have delay"

    def test_zero_id(self):
        result = asyncio.run(fetch_data(0))
        assert result == "Invalid ID"

    def test_negative_id(self):
        result = asyncio.run(fetch_data(-3))
        assert result == "Invalid ID"

    def test_invalid_id_no_delay(self):
        start = time.time()
        asyncio.run(fetch_data(-1))
        elapsed = time.time() - start
        assert elapsed < 0.05, "Invalid ID should return immediately"
