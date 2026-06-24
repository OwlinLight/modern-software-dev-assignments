import argparse
import asyncio
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

SERVER_PATH = Path(__file__).with_name("tophub.py")


def text_from_result(result: object) -> str:
    """Extract readable text from an MCP tool result."""
    content = getattr(result, "content", [])
    parts = []
    for item in content:
        text = getattr(item, "text", None)
        if text is not None:
            parts.append(text)
    return "\n".join(parts).strip() or str(result)


def parse_message(message: str) -> tuple[str, dict[str, object]]:
    words = message.strip().split()
    if not words:
        raise ValueError("Try: tops 7, tools, or quit.")

    intent = words[0].lower()
    if intent in {"top", "tops", "repos", "repositories"}:
        if len(words) != 2:
            raise ValueError("Use the number of days to search, like: tops 7")
        try:
            days = int(words[1])
        except ValueError as exc:
            raise ValueError("Days must be a whole number.") from exc
        if days < 1:
            raise ValueError("Days must be at least 1.")
        return "get_tops", {"days": days}

    raise ValueError("Unknown command. Try: tops 7, tools, or quit.")


async def print_tools(session: ClientSession) -> None:
    response = await session.list_tools()
    print("\nAvailable MCP tools:")
    for tool in response.tools:
        description_lines = (tool.description or "").strip().splitlines()
        description = description_lines[0] if description_lines else "No description"
        print(f"- {tool.name}: {description}")


async def call_tophub_tool(session: ClientSession, message: str) -> None:
    tool_name, arguments = parse_message(message)
    result = await session.call_tool(tool_name, arguments)
    print(f"\ntophub> {text_from_result(result)}")


async def chat(demo: bool) -> None:
    server = StdioServerParameters(command=sys.executable, args=[str(SERVER_PATH)])
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            await print_tools(session)

            if demo:
                print("\nYou> tops 7")
                await call_tophub_tool(session, "tops 7")
                return

            print("\nType a request. Examples: tops 7 | tops 30 | tools | quit")
            while True:
                try:
                    message = input("\nYou> ").strip()
                except (EOFError, KeyboardInterrupt):
                    print()
                    return

                if message.lower() in {"q", "quit", "exit"}:
                    return
                if message.lower() in {"tool", "tools", "help", "?"}:
                    await print_tools(session)
                    continue

                try:
                    await call_tophub_tool(session, message)
                except ValueError as exc:
                    print(f"\nclient> {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Client for the tophub MCP server.")
    parser.add_argument("--demo", action="store_true", help="Run one sample request and exit.")
    args = parser.parse_args()
    asyncio.run(chat(args.demo))


if __name__ == "__main__":
    main()
