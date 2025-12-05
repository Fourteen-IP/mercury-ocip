import asyncio
from contextlib import contextmanager, asynccontextmanager
import time

from mercury_ocip.client import Client, AsyncClient


@contextmanager
def measure_time(operation_name: str):
    start_time = time.time()
    try:
        yield
    finally:
        elapsed_time = time.time() - start_time
        print(f"{operation_name} completed in {elapsed_time:.2f} seconds.")


@asynccontextmanager
async def measure_time_async(operation_name: str):
    start_time = time.time()
    try:
        yield
    finally:
        elapsed_time = time.time() - start_time
        print(f"{operation_name} completed in {elapsed_time:.2f} seconds.")


def main(client: Client) -> None:
    """
    Main function to run the benchmark script.

    Args:
        client (Client): An instance of the Client class to perform operations.
    """
    # Example operation: Authenticate the client

    try:
        with measure_time("Authentication"):
            client.authenticate()

        with measure_time("Dispatch Table Retrieval"):
            for command_name in client._dispatch_table:
                client._dispatch_table.get(command_name)  # type: ignore

        with measure_time("Command Creation"):
            command = client._dispatch_table.get("UserGetListInSystemRequest")()  # type: ignore

        with measure_time("Command Execution"):
            for _ in range(100):
                client.command(command=command)

        with measure_time("Command Parsing"):
            for _ in range(1000):
                command.to_dict()
                command.to_xml()

    except Exception as e:
        print(f"An error occurred: {e}")


async def main_async(client: AsyncClient):
    """
    Main function to run the benchmark script asynchronously.

    Args:
        client (Client): An instance of the Client class to perform operations.
    """
    try:
        async with measure_time_async("Authentication"):
            await client.authenticate()

        async with measure_time_async("Dispatch Table Retrieval"):
            for command_name in client._dispatch_table:
                client._dispatch_table.get(command_name)  # type: ignore

        async with measure_time_async("Command Creation"):
            command = client._dispatch_table.get("UserGetListInSystemRequest")()  # type: ignore

        async with measure_time_async("Command Execution"):
            tasks = [await client.command(command=command) for _ in range(100)]
            await asyncio.gather(*tasks)  # type: ignore

        async with measure_time_async("Command Parsing"):
            parser_tasks = [
                [await command.to_dict_async(), await command.to_xml_async()]
                for _ in range(1000)
            ]
            await asyncio.gather(*parser_tasks)  # type: ignore

    except Exception as e:
        print(f"An error occurred: {e}")
