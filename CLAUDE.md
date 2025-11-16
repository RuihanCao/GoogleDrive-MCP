# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server implementation that creates a bidirectional communication bridge between AI models and external tools. The system uses WebSocket connections to pipe MCP stdio messages between local MCP servers and a remote endpoint.

## Architecture

The project has two main components:

1. **mcp_pipe.py** - The core communication bridge that:
   - Connects to a WebSocket endpoint (via `MCP_ENDPOINT` environment variable)
   - Manages subprocess lifecycle for MCP servers (stdio/sse/http transports)
   - Implements automatic reconnection with exponential backoff
   - Pipes bidirectional communication: WebSocket ↔ subprocess stdin/stdout
   - Supports config-driven multi-server mode or single-script mode

2. **calculator.py** - Example MCP tool implementation using FastMCP that exposes a `calculator` tool for evaluating Python math expressions

## Configuration

**mcp_config.json** defines available MCP servers:
- `type: stdio` - Direct subprocess execution
- `type: sse` or `type: http` - Proxied via `mcp-proxy` module
- Each server can have `disabled: true` to skip it
- Servers can specify `env` variables and custom `headers` (for SSE/HTTP)

Config discovery: `$MCP_CONFIG` environment variable, or `./mcp_config.json` by default.

## Running the Project

### Environment Setup
```bash
# Required: Set the WebSocket endpoint
export MCP_ENDPOINT="wss://your-endpoint-url"

# Windows (PowerShell):
$env:MCP_ENDPOINT = "wss://your-endpoint-url"

# Optional: Custom config path
export MCP_CONFIG="/path/to/config.json"
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run All Configured Servers
```bash
python mcp_pipe.py
```
Starts all enabled servers from `mcp_config.json` concurrently (skips `disabled: true` entries).

### Run Single Local Script (Back-compat)
```bash
python mcp_pipe.py calculator.py
```
Runs a single local Python script as an MCP stdio server.

## Creating New MCP Tools

Use FastMCP to create new tools:

```python
from fastmcp import FastMCP

mcp = FastMCP("ToolName")

@mcp.tool()
def tool_name(param: str) -> dict:
    """Tool description for AI"""
    # Implementation
    return {"success": True, "result": result}

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

Add to `mcp_config.json`:
```json
{
  "mcpServers": {
    "your-tool": {
      "type": "stdio",
      "command": "python",
      "args": ["path/to/your_tool.py"]
    }
  }
}
```

## Important Implementation Details

- **Windows UTF-8 encoding**: `calculator.py` reconfigures stdout/stderr for Windows console UTF-8 support
- **Process management**: `mcp_pipe.py` ensures proper subprocess termination using SIGTERM with fallback to SIGKILL
- **Text mode**: All stdin/stdout/stderr uses `encoding='utf-8', text=True` for subprocess communication
- **Reconnection**: On connection loss, exponential backoff from 1s up to 600s (10 minutes)
- **Multi-server mode**: Each server gets its own WebSocket connection and subprocess, running concurrently via `asyncio.gather()`
- **Logging**: Uses Python logging with `[target]` prefixes to distinguish server outputs
