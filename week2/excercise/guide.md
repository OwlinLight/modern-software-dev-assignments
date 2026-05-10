# Fill-in-the-Blank Guide

This guide matches the scaffolded exercise files:

- [coding_agent_from_scratch_lecture_fill_in_the_blank.py](/home/charlie/codex/modern-software-dev-assignments/week2/excercise/coding_agent_from_scratch_lecture_fill_in_the_blank.py)
- [simple_mcp_fill_in_the_blank.py](/home/charlie/codex/modern-software-dev-assignments/week2/excercise/simple_mcp_fill_in_the_blank.py)

The original source files are still here for reference:

- [coding_agent_from_scratch_lecture.py](/home/charlie/codex/modern-software-dev-assignments/week2/excercise/coding_agent_from_scratch_lecture.py)
- [simple_mcp.py](/home/charlie/codex/modern-software-dev-assignments/week2/excercise/simple_mcp.py)

## How To Use This

1. Read the original file once so you understand the full flow.
2. Switch to the fill-in-the-blank version and complete the `TODO`s in order.
3. Run the file after every 1-2 TODOs so bugs stay small and obvious instead of becoming a semester-long emotional support problem.

## File 1: Coding Agent From Scratch

### What this file teaches

- How a tool-using coding agent stores conversation state
- How to describe tools to an LLM
- How to parse tool calls out of model output
- How to execute tool calls and feed results back into the loop

### TODO map

`TODO 1`
- Build the tool registry.
- The keys are tool names as strings.
- The values are the Python functions the agent is allowed to call.

`TODO 2`
- Format a readable description for one tool.
- Use `tool.__doc__` for the description.
- Use `inspect.signature(tool)` for the function signature.

`TODO 3`
- Concatenate all tool descriptions into one string.
- Insert that string into `SYSTEM_PROMPT.format(...)`.

`TODO 4`
- Ignore lines that are not tool requests.
- Only parse lines starting with `tool:`.

`TODO 5`
- Parse lines like:

```text
tool: read_file({"filename":"notes.txt"})
```

- Extract:
  - the tool name: `read_file`
  - the JSON arguments: `{"filename":"notes.txt"}`

`TODO 6`
- Call the OpenAI chat completions API.
- Return the text content from the first choice.

`TODO 7`
- Initialize the conversation with the system prompt.
- This gives the model its rules and available tools.

`TODO 8`
- If the assistant replies normally, print the reply and store it in the conversation.
- Then stop the inner loop and wait for the next user turn.

`TODO 9`
- Dispatch tool calls by name.
- Pull the needed values out of the parsed argument dictionary.

`TODO 10`
- Append tool results back into the conversation using:

```text
tool_result({...})
```

- This lets the model continue reasoning with the tool output.

### Suggested run command

```bash
python3 week2/excercise/coding_agent_from_scratch_lecture_fill_in_the_blank.py
```

### Things to watch for

- `json.loads(...)` expects valid JSON with double quotes.
- `conversation` must stay in chronological order.
- If you forget to append `tool_result(...)`, the agent will act like it has amnesia, which is very on-brand for badly wired loops.

## File 2: Simple MCP

### What this file teaches

- How to create a minimal MCP server
- How to expose Python functions as MCP tools
- How to share file system utilities through a server interface

### TODO map

`TODO 1`
- Create the `FastMCP` app instance.
- Give it the name `SimpleMCPTestServer`.

`TODO 2`
- Read a file and return:
  - absolute file path
  - file contents

`TODO 3`
- List directory contents.
- Each item should say whether it is a `file` or `dir`.

`TODO 4`
- Support both create/overwrite and replace-first-occurrence behavior.
- Keep the return format consistent with the original file.

`TODO 5`
- Run the MCP server in the `__main__` block.

### Suggested run command

```bash
python3 week2/excercise/simple_mcp_fill_in_the_blank.py
```

## Quick Self-Check

Before calling the exercise done, verify:

- Every `TODO` has been replaced or completed.
- Both files still import cleanly.
- The coding agent can parse at least one `tool: ...` line correctly.
- The MCP tools return dictionaries, not raw strings or `Path` objects.
