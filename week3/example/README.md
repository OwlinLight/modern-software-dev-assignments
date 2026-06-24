# A Simple MCP Weather Server written in Python

See the [Build an MCP server](https://modelcontextprotocol.io/docs/develop/build-server) tutorial for more information.

## Verify with the chatbot client

Run the server through the local MCP client:

```bash
uv run weather-client
```

Then try:

```text
alerts CA
forecast 37.7749 -122.4194
tools
quit
```

For a quick smoke test:

```bash
uv run weather-client --demo
```
