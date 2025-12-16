# Module 04: Async I/O & Networking

## Prerequisites
Complete Modules 01, 02, and 03 before starting this module.

---

## 1. Why Async I/O?

### 1.1 The I/O Bottleneck

Most programs spend time waiting for:
- Network requests (HTTP, database queries)
- File system operations
- User input

```
┌──────────────────────────────────────────────┐
│  Synchronous Request (time →)                │
├──────────────────────────────────────────────┤
│  [Send]▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓[Wait]▓▓▓▓▓▓▓▓[Recv]   │
│         ↑ CPU idle during wait ↑             │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│  Async Requests (time →)                     │
├──────────────────────────────────────────────┤
│  Req1: [Send]          [Recv]                │
│  Req2:    [Send]          [Recv]             │
│  Req3:       [Send]          [Recv]          │
│         ↑ All waiting concurrently ↑         │
└──────────────────────────────────────────────┘
```

### 1.2 Blocking vs Non-blocking

```python
# BLOCKING - program waits
import requests
response = requests.get("https://api.example.com")  # Blocks here

# NON-BLOCKING - program continues
import aiohttp
async with aiohttp.ClientSession() as session:
    async with session.get("https://api.example.com") as response:
        data = await response.text()  # Yields control while waiting
```

---

## 2. Async File I/O with aiofiles

### 2.1 Installation

```bash
pip install aiofiles
```

### 2.2 Basic File Operations

```python
import aiofiles
import asyncio

async def read_file(path):
    async with aiofiles.open(path, 'r') as f:
        content = await f.read()
    return content

async def write_file(path, content):
    async with aiofiles.open(path, 'w') as f:
        await f.write(content)

async def main():
    await write_file('test.txt', 'Hello, Async World!')
    content = await read_file('test.txt')
    print(content)

asyncio.run(main())
```

### 2.3 Line-by-Line Reading

```python
async def read_lines(path):
    async with aiofiles.open(path, 'r') as f:
        async for line in f:
            print(line.strip())

async def process_large_file(path):
    """Process file without loading entirely into memory"""
    line_count = 0
    async with aiofiles.open(path, 'r') as f:
        async for line in f:
            line_count += 1
            # Process each line
    return line_count
```

### 2.4 Concurrent File Operations

```python
import aiofiles
import asyncio

async def read_many_files(paths):
    """Read multiple files concurrently"""
    async def read_one(path):
        async with aiofiles.open(path, 'r') as f:
            return await f.read()

    contents = await asyncio.gather(*[read_one(p) for p in paths])
    return dict(zip(paths, contents))
```

---

## 3. HTTP Client with aiohttp

### 3.1 Installation

```bash
pip install aiohttp
```

### 3.2 Basic Requests

```python
import aiohttp
import asyncio

async def fetch_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def main():
    html = await fetch_url("https://example.com")
    print(len(html))

asyncio.run(main())
```

### 3.3 Session Management

```python
# WRONG - creates new session for each request
async def bad_fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

# RIGHT - reuse session for multiple requests
async def fetch_many(urls):
    async with aiohttp.ClientSession() as session:
        async def fetch_one(url):
            async with session.get(url) as response:
                return await response.text()

        results = await asyncio.gather(*[fetch_one(url) for url in urls])
        return results
```

### 3.4 HTTP Methods

```python
async def http_examples(session):
    # GET
    async with session.get('https://api.example.com/users') as resp:
        users = await resp.json()

    # POST with JSON
    async with session.post(
        'https://api.example.com/users',
        json={'name': 'John', 'email': 'john@example.com'}
    ) as resp:
        new_user = await resp.json()

    # PUT
    async with session.put(
        'https://api.example.com/users/1',
        json={'name': 'John Updated'}
    ) as resp:
        updated = await resp.json()

    # DELETE
    async with session.delete('https://api.example.com/users/1') as resp:
        status = resp.status
```

### 3.5 Headers and Authentication

```python
async def authenticated_request():
    headers = {
        'Authorization': 'Bearer token123',
        'Content-Type': 'application/json'
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get('https://api.example.com/me') as resp:
            return await resp.json()

# Basic Auth
async def basic_auth_request():
    auth = aiohttp.BasicAuth('username', 'password')
    async with aiohttp.ClientSession(auth=auth) as session:
        async with session.get('https://api.example.com/protected') as resp:
            return await resp.json()
```

### 3.6 Timeouts

```python
import aiohttp
from aiohttp import ClientTimeout

async def request_with_timeout():
    # Total timeout for entire operation
    timeout = ClientTimeout(total=30)

    # Or granular timeouts
    timeout = ClientTimeout(
        total=30,        # Total timeout
        connect=10,      # Connection timeout
        sock_read=10     # Read timeout
    )

    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get('https://slow-api.com') as resp:
                return await resp.text()
        except asyncio.TimeoutError:
            print("Request timed out!")
```

### 3.7 Error Handling

```python
import aiohttp

async def safe_fetch(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()  # Raise for 4xx/5xx
            return await response.json()
    except aiohttp.ClientResponseError as e:
        print(f"HTTP Error {e.status}: {e.message}")
    except aiohttp.ClientConnectionError:
        print("Connection failed")
    except asyncio.TimeoutError:
        print("Request timed out")
    return None
```

---

## 4. TCP/UDP with asyncio

### 4.1 TCP Echo Server

```python
import asyncio

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Connection from {addr}")

    while True:
        data = await reader.read(1024)
        if not data:
            break

        message = data.decode()
        print(f"Received: {message}")

        writer.write(data)  # Echo back
        await writer.drain()

    print(f"Closing connection from {addr}")
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(
        handle_client, '127.0.0.1', 8888
    )

    addr = server.sockets[0].getsockname()
    print(f"Serving on {addr}")

    async with server:
        await server.serve_forever()

asyncio.run(main())
```

### 4.2 TCP Client

```python
import asyncio

async def tcp_client():
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888
    )

    writer.write(b'Hello, server!')
    await writer.drain()

    data = await reader.read(1024)
    print(f"Received: {data.decode()}")

    writer.close()
    await writer.wait_closed()

asyncio.run(tcp_client())
```

### 4.3 UDP Server/Client

```python
import asyncio

class EchoServerProtocol(asyncio.DatagramProtocol):
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        print(f"Received {message} from {addr}")
        self.transport.sendto(data, addr)  # Echo back

async def main():
    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: EchoServerProtocol(),
        local_addr=('127.0.0.1', 9999)
    )

    print("UDP server running")
    try:
        await asyncio.sleep(3600)  # Run for 1 hour
    finally:
        transport.close()

asyncio.run(main())
```

---

## 5. Subprocess Handling

### 5.1 Running Commands

```python
import asyncio

async def run_command(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()

    return {
        'returncode': proc.returncode,
        'stdout': stdout.decode(),
        'stderr': stderr.decode()
    }

async def main():
    result = await run_command('echo "Hello from subprocess"')
    print(result['stdout'])

asyncio.run(main())
```

### 5.2 Running Multiple Commands

```python
async def run_many_commands(commands):
    results = await asyncio.gather(*[
        run_command(cmd) for cmd in commands
    ])
    return results
```

### 5.3 Streaming Output

```python
async def stream_command_output(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE
    )

    async for line in proc.stdout:
        print(f"[OUTPUT] {line.decode().strip()}")

    await proc.wait()
```

---

## 6. Database with asyncpg/aiosqlite

### 6.1 SQLite with aiosqlite

```bash
pip install aiosqlite
```

```python
import aiosqlite
import asyncio

async def main():
    async with aiosqlite.connect('example.db') as db:
        # Create table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT
            )
        ''')

        # Insert
        await db.execute(
            'INSERT INTO users (name, email) VALUES (?, ?)',
            ('John', 'john@example.com')
        )
        await db.commit()

        # Query
        async with db.execute('SELECT * FROM users') as cursor:
            async for row in cursor:
                print(row)

asyncio.run(main())
```

### 6.2 PostgreSQL with asyncpg

```bash
pip install asyncpg
```

```python
import asyncpg
import asyncio

async def main():
    conn = await asyncpg.connect(
        'postgresql://user:password@localhost/database'
    )

    # Create table
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT,
            email TEXT
        )
    ''')

    # Insert
    await conn.execute(
        'INSERT INTO users (name, email) VALUES ($1, $2)',
        'John', 'john@example.com'
    )

    # Query
    rows = await conn.fetch('SELECT * FROM users')
    for row in rows:
        print(dict(row))

    await conn.close()

asyncio.run(main())
```

### 6.3 Connection Pool

```python
import asyncpg
import asyncio

async def main():
    # Create connection pool
    pool = await asyncpg.create_pool(
        'postgresql://user:password@localhost/database',
        min_size=5,
        max_size=20
    )

    async def fetch_user(user_id):
        async with pool.acquire() as conn:
            return await conn.fetchrow(
                'SELECT * FROM users WHERE id = $1', user_id
            )

    # Use pool for concurrent queries
    users = await asyncio.gather(*[
        fetch_user(i) for i in range(1, 11)
    ])

    await pool.close()

asyncio.run(main())
```

---

## 7. Practical Patterns

### 7.1 Rate-Limited API Client

```python
import aiohttp
import asyncio

class RateLimitedClient:
    def __init__(self, requests_per_second=10):
        self.semaphore = asyncio.Semaphore(requests_per_second)
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args):
        await self.session.close()

    async def get(self, url):
        async with self.semaphore:
            async with self.session.get(url) as response:
                result = await response.json()
            await asyncio.sleep(0.1)  # Rate limit
            return result

# Usage
async def main():
    async with RateLimitedClient(5) as client:
        urls = [f"https://api.example.com/item/{i}" for i in range(20)]
        results = await asyncio.gather(*[client.get(url) for url in urls])
```

### 7.2 Retry Logic

```python
import aiohttp
import asyncio

async def fetch_with_retry(session, url, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### 7.3 Concurrent with Progress

```python
import aiohttp
import asyncio

async def fetch_all_with_progress(urls):
    completed = 0
    total = len(urls)
    results = []

    async def fetch_one(session, url):
        nonlocal completed
        async with session.get(url) as response:
            result = await response.text()
        completed += 1
        print(f"Progress: {completed}/{total}")
        return result

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_one(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

    return results
```

---

## 8. Best Practices

### 8.1 Always Use Context Managers

```python
# GOOD
async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
        data = await response.text()

# BAD - resources may not be cleaned up
session = aiohttp.ClientSession()
response = await session.get(url)
```

### 8.2 Reuse Connections

```python
# Create session once
async def main():
    async with aiohttp.ClientSession() as session:
        # Reuse for all requests
        result1 = await fetch(session, url1)
        result2 = await fetch(session, url2)
        results = await asyncio.gather(*[
            fetch(session, url) for url in urls
        ])
```

### 8.3 Set Appropriate Timeouts

```python
timeout = aiohttp.ClientTimeout(total=30)
async with aiohttp.ClientSession(timeout=timeout) as session:
    # All requests will have 30s timeout
    pass
```

### 8.4 Handle Exceptions Gracefully

```python
async def safe_operation():
    try:
        result = await risky_io_operation()
        return result
    except aiohttp.ClientError as e:
        logger.error(f"HTTP error: {e}")
        return None
    except asyncio.TimeoutError:
        logger.error("Operation timed out")
        return None
```

---

## Summary

1. Use `aiofiles` for async file operations
2. Use `aiohttp` for HTTP client/server
3. Use `asyncio.start_server()` for TCP servers
4. Use `asyncio.create_subprocess_*` for running commands
5. Use `aiosqlite`/`asyncpg` for database access
6. Always use context managers
7. Reuse sessions and connections
8. Set timeouts and handle errors

---

## Next Steps

After completing the 3 exercises, move to **Module 05: Advanced Patterns** to learn real-world async architectures.
