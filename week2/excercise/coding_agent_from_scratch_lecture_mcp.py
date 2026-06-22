import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import Client
from google import genai
from typing import Any, Dict, List, Tuple

try:
    from simple_mcp import mcp
except ImportError:
    from week2.excercise.simple_mcp import mcp

load_dotenv()

SYSTEM_PROMPT = """
You are a coding assistant whose goal it is to help us solve coding tasks. 
You have access to a series of MCP tools you can execute. Here are the tools you can execute:

{tool_list_repr}

When you want to use a tool, reply with exactly one line in the format: 'tool: TOOL_NAME({{JSON_ARGS}})' and nothing else.
Use compact single-line JSON with double quotes. After receiving a tool_result(...) message, continue the task.
If no tool is needed, respond normally.
"""


YOU_COLOR = "\u001b[94m"
ASSISTANT_COLOR = "\u001b[93m"
RESET_COLOR = "\u001b[0m"


def get_gemini_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY or GOOGLE_API_KEY before running the agent.")
    return genai.Client(api_key=api_key)


def get_tool_str_representation(tool: Any) -> str:
    input_schema = json.dumps(tool.inputSchema, indent=2)
    return f"""
    Name: {tool.name}
    Description: {tool.description}
    Input JSON schema: {input_schema}
    """


async def get_full_system_prompt(client: Client) -> str:
    tool_str_repr = ""
    for tool in await client.list_tools():
        tool_str_repr += "TOOL\n===" + get_tool_str_representation(tool)
        tool_str_repr += f"\n{"="*15}\n"
    return SYSTEM_PROMPT.format(tool_list_repr=tool_str_repr)

def extract_tool_invocations(text: str) -> List[Tuple[str, Dict[str, Any]]]:
    """
    Return list of (tool_name, args) requested in 'tool: name({...})' lines.
    The parser expects single-line, compact JSON in parentheses.
    """
    invocations = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("tool:"):
            continue
        try:
            after = line[len("tool:"):].strip()
            name, rest = after.split("(", 1)
            name = name.strip()
            if not rest.endswith(")"):
                continue
            json_str = rest[:-1].strip()
            args = json.loads(json_str)
            invocations.append((name, args))
        except Exception:
            continue
    return invocations

def execute_llm_call(conversation: List[Dict[str, str]]):
    prompt = "\n\n".join(
        f"{message['role'].upper()}: {message['content']}" for message in conversation
    )
    response = get_gemini_client().models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
    )
    return response.text


async def call_mcp_tool(client: Client, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        result = await client.call_tool(name, args, timeout=10)
        return result.structured_content
    except Exception as exc:
        return {
            "tool": name,
            "args": args,
            "error": str(exc),
        }


async def run_coding_agent_loop():
    async with Client(mcp) as client:
        system_prompt = await get_full_system_prompt(client)
        print(system_prompt)
        conversation = [{
            "role": "system",
            "content": system_prompt
        }]
        while True:
            try:
                user_input = input(f"{YOU_COLOR}You:{RESET_COLOR}:")
            except (KeyboardInterrupt, EOFError):
                break
            conversation.append({
                "role": "user",
                "content": user_input.strip()
            })
            while True:
                assistant_response = execute_llm_call(conversation)
                tool_invocations = extract_tool_invocations(assistant_response)
                if not tool_invocations:
                    print(f"{ASSISTANT_COLOR}Assistant:{RESET_COLOR}: {assistant_response}")
                    conversation.append({
                        "role": "assistant",
                        "content": assistant_response
                    })
                    break
                for name, args in tool_invocations:
                    print(name, args)
                    resp = await call_mcp_tool(client, name, args)
                    conversation.append({
                        "role": "user",
                        "content": f"tool_result({json.dumps(resp)})"
                    })


async def run_mcp_smoke_test():
    async with Client(mcp) as client:
        system_prompt = await get_full_system_prompt(client)
        print("Prompt has read_file_tool:", "read_file_tool" in system_prompt, flush=True)
        print("Prompt has list_files_tool:", "list_files_tool" in system_prompt, flush=True)
        print("Prompt has edit_file_tool:", "edit_file_tool" in system_prompt, flush=True)

        print("Calling list_files_tool...", flush=True)
        listed = await call_mcp_tool(client, "list_files_tool", {"path": "week2/excercise"})
        file_names = {item["filename"] for item in listed["files"]}
        print("Listed simple_mcp.py:", "simple_mcp.py" in file_names, flush=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            demo_file = Path(temp_dir) / "agent_mcp_demo.txt"

            print("Calling edit_file_tool to create file...", flush=True)
            created = await call_mcp_tool(
                client,
                "edit_file_tool",
                {
                    "path": str(demo_file),
                    "old_str": "",
                    "new_str": "hello MCP agent",
                },
            )
            print("Create action:", created["action"], flush=True)

            print("Calling read_file_tool...", flush=True)
            read_initial = await call_mcp_tool(
                client,
                "read_file_tool",
                {"filename": str(demo_file)},
            )
            print("Read content:", read_initial["content"], flush=True)

            print("Calling edit_file_tool to update file...", flush=True)
            edited = await call_mcp_tool(
                client,
                "edit_file_tool",
                {
                    "path": str(demo_file),
                    "old_str": "hello",
                    "new_str": "goodbye",
                },
            )
            print("Edit action:", edited["action"], flush=True)

            print("Calling read_file_tool again...", flush=True)
            read_updated = await call_mcp_tool(
                client,
                "read_file_tool",
                {"filename": str(demo_file)},
            )
            print("Updated content:", read_updated["content"], flush=True)


if __name__ == "__main__":
    if "--mcp-smoke-test" in sys.argv:
        asyncio.run(run_mcp_smoke_test())
    else:
        asyncio.run(run_coding_agent_loop())
