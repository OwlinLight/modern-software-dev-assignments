import argparse
import asyncio
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

SERVER_PATH = Path(__file__).with_name("weather.py")


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
        raise ValueError("Try: alerts CA, forecast 37.7749 -122.4194, tools, or quit.")

    intent = words[0].lower()
    if intent in {"alert", "alerts"}:
        if len(words) != 2 or len(words[1]) != 2:
            raise ValueError("Use a two-letter state code, like: alerts CA")
        return "get_alerts", {"state": words[1].upper()}

    if intent in {"forecast", "weather"}:
        if len(words) != 3:
            raise ValueError("Use latitude and longitude, like: forecast 37.7749 -122.4194")
        try:
            latitude = float(words[1])
            longitude = float(words[2])
        except ValueError as exc:
            raise ValueError("Latitude and longitude must be numbers.") from exc
        return "get_forecast", {"latitude": latitude, "longitude": longitude}

    raise ValueError("Unknown command. Try: alerts CA, forecast 37.7749 -122.4194, tools, or quit.")


async def print_tools(session: ClientSession) -> None:
    response = await session.list_tools()
    print("\nAvailable MCP tools:")
    for tool in response.tools:
        description = (tool.description or "").strip().splitlines()[0]
        print(f"- {tool.name}: {description}")


async def call_weather_tool(session: ClientSession, message: str) -> None:
    tool_name, arguments = parse_message(message)
    result = await session.call_tool(tool_name, arguments)
    print(f"\nweather> {text_from_result(result)}")


async def chat(demo: bool) -> None:
    server = StdioServerParameters(command=sys.executable, args=[str(SERVER_PATH)])
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            await print_tools(session)

            if demo:
                print("\nYou> alerts CA")
                await call_weather_tool(session, "alerts CA")
                return

            print("\nType a request. Examples: alerts CA | forecast 37.7749 -122.4194 | tools | quit")
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
                    await call_weather_tool(session, message)
                except ValueError as exc:
                    print(f"\nclient> {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Chatbot-style client for the weather MCP server.")
    parser.add_argument("--demo", action="store_true", help="Run one sample request and exit.")
    args = parser.parse_args()
    asyncio.run(chat(args.demo))


if __name__ == "__main__":
    main()
