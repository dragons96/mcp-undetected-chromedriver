from . import server
import asyncio


def main():
    """Main entry point for the package."""
    asyncio.run(server.mcp.run_stdio_async())


__all__ = ["main", "server"]
