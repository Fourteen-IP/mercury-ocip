# Async Client 

The `AsyncClient` class provides an asynchronous interface for interacting with BroadWorks servers. It is designed for high-performance applications that require non-blocking I/O operations and can handle multiple concurrent requests efficiently.

!!! warning "Advanced Usage"
    Please note that the AsyncClient is intended for advanced usage where performance and concurrent requests are needed. Normal users trying to automate small tasks are advised to use Client.

## Key Features

**Asynchronous Operations**: All methods are asynchronous and return awaitable objects. This enables concurrent execution and improved performance in I/O-bound applications.

**Manual Authentication**: Unlike the synchronous `Client`, authentication must be explicitly called using `await client.authenticate()` before executing commands.

**Context Manager Support**: Implements async context manager protocol for automatic resource cleanup and connection management.

**Concurrent Request Handling**: Designed to work with asyncio event loops, enabling multiple simultaneous requests to BroadWorks servers.

---

## Quick Start

The most basic example - connect, authenticate, run a command, clean up:

```python
import asyncio
from mercury_ocip.client import AsyncClient
from mercury_ocip.commands.commands import UserGetListInSystemRequest

async def get_users():
    client = AsyncClient(
        host="https://your-broadworks.com",
        port=2209,
        username="admin",
        password="secret123",
        conn_type="SOAP"  # or "TCP"
    )
    
    try:
        await client.authenticate()  # Manual authentication required
        response = await client.command(UserGetListInSystemRequest())
        return response.user_table  # Access the actual data
    finally:
        await client.disconnect()  # Clean up and disconnect

# Run the async function
users = asyncio.run(get_users())
print(f"Found {len(users)} users")
```

## Context Manager Usage (Recommended)

Using async context managers for automatic resource management:

```python
async def get_users_with_context():
    async with AsyncClient(
        host="https://your-broadworks.com",
        username="admin",
        password="secret123",
        conn_type="SOAP"
    ) as client:
        await client.authenticate()
        response = await client.command(UserGetListInSystemRequest())
        return response.user_table
        # Automatic cleanup when exiting context

users = asyncio.run(get_users_with_context())
```

## Connection Types

**SOAP** (recommended for most cases):
```python
client = AsyncClient(
    host="https://your-server.com",  # No /wsdl suffix needed
    username="your_user",
    password="your_pass",
    conn_type="SOAP"
)
```

**TCP** (for legacy systems or specific requirements):
```python
client = AsyncClient(
    host="broadworks.company.com",
    port=2209,  # Usually 2209/2208 for TCP
    username="admin",
    password="password",
    conn_type="TCP",
    tls=True  # Set False for unencrypted (not recommended)
)
```

## Running Commands

**Using command classes** (type-safe, autocompletion-friendly):
```python
from mercury_ocip.commands.commands import GroupHuntGroupGetInstanceRequest20

async def get_hunt_group():
    async with AsyncClient(...) as client:
        await client.authenticate()
        
        response = await client.command(
            GroupHuntGroupGetInstanceRequest20(
                group_id="MyGroup",
                service_provider_id="MyProvider"
            )
        )
        print(f"Hunt Group: {response}")
```

**Using raw commands** (when you know the exact command name):
```python
# Equivalent to the above, but as a string
response = await client.raw_command(
    "GroupHuntGroupGetInstanceRequest20",
    group_id="MyGroup",
    service_provider_id="MyProvider"
)
```

## Practical Examples

**Concurrent user operations**:
```python
import asyncio

async def process_user(client, user):
    """Process a single user"""
    user_detail = await client.command(
        UserGetRequest23V2(user_id=user.user_id)
    )
    
    if user_detail.department == "Sales":
        await client.command(
            UserModifyRequest22(
                user_id=user.user_id,
                department="Business Development"
            )
        )
        return f"Updated {user.user_id}"
    return f"Skipped {user.user_id}"

async def update_users_concurrently():
    async with AsyncClient(
        host="https://broadworks.example.com",
        username="admin",
        password="admin123",
        conn_type="SOAP"
    ) as client:
        await client.authenticate()
        
        # Get all users
        users_resp = await client.command(UserGetListInSystemRequest())
        
        # Process users concurrently (up to 10 at a time)
        semaphore = asyncio.Semaphore(10)
        
        async def process_with_limit(user):
            async with semaphore:
                return await process_user(client, user)
        
        tasks = [process_with_limit(user) for user in users_resp.user_table]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                print(f"Error: {result}")
            else:
                print(result)

# Run the concurrent operation
asyncio.run(update_users_concurrently())
```

**Configuration with custom settings**:
```python
import logging
import asyncio

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("my_async_broadworks_app")

async def main():
    client = AsyncClient(
        host="https://broadworks.example.com/webservice/services/ProvisioningService",
        username="service_account",
        password="complex_password_123",
        conn_type="SOAP",
        timeout=60,  # 60 seconds for slow operations
        user_agent="My Async Admin Tool v1.0",  # Shows up in logs
        logger=logger,  # Your custom logger
    )
    
    try:
        await client.authenticate()
        # Your async operations here
    finally:
        await client.disconnect()

# Enable debug logging to see exact commands
logging.basicConfig(level=logging.DEBUG)
asyncio.run(main())
```

## Error Handling Tips

Always wrap your async client operations:
```python
from mercury_ocip.exceptions import MError
import asyncio

async def safe_operation():
    try:
        async with AsyncClient(...) as client:
            await client.authenticate()
            response = await client.command(SomeCommand())
            # Process response...
    except MError as e:
        print(f"BroadWorks error: {e}")
        # Handle specific BroadWorks errors
    except Exception as e:
        print(f"Unexpected error: {e}")
        # Handle network issues, etc.

asyncio.run(safe_operation())
```

## Advanced Typing

Response classes can be used with proper typing:
```python
from mercury_ocip.commands import GroupHuntGroupGetInstanceRequest20, GroupHuntGroupGetInstanceResponse20
from mercury_ocip.commands.base_command import ErrorResponse

async def typed_request():
    async with AsyncClient(...) as client:
        await client.authenticate()
        
        response: GroupHuntGroupGetInstanceResponse20 | ErrorResponse = await client.command(
            GroupHuntGroupGetInstanceRequest20(
                group_id="MyGroup",
                service_provider_id="MyProvider"
            )
        )

        if isinstance(response, ErrorResponse):
            print(f"Request Failed: {response.errorCode}: {response.summary}")
        else:
            print(f"Hunt Group: {response}")
```

## Performance Patterns

**Batch processing with rate limiting**:
```python
import asyncio

async def batch_process_users(users, batch_size=50):
    async with AsyncClient(...) as client:
        await client.authenticate()
        
        for i in range(0, len(users), batch_size):
            batch = users[i:i + batch_size]
            
            tasks = [
                client.command(UserGetRequest23V2(user_id=user.user_id))
                for user in batch
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for user, result in zip(batch, results):
                if isinstance(result, Exception):
                    print(f"Error processing {user.user_id}: {result}")
                else:
                    print(f"Processed {user.user_id}")
            
            # Small delay between batches to avoid overwhelming server
            await asyncio.sleep(0.1)
```

## Pro Tips

**Manual authentication**: Unlike `Client`, you must call `await client.authenticate()` explicitly before making requests.

**Context managers**: Always use async context managers (`async with`) for automatic cleanup.

**Concurrency control**: Use `asyncio.Semaphore` to limit concurrent requests and avoid overwhelming the server.

**Error handling**: Use `asyncio.gather(..., return_exceptions=True)` to handle individual failures in concurrent operations.

**Resource cleanup**: Always ensure `await client.disconnect()` is called, either manually or through context managers.

**Performance**: AsyncClient shines when making many concurrent requests. For single requests, the synchronous Client may be simpler.

::: mercury_ocip.client.AsyncClient