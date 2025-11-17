# MCP Sample Project | MCP 示例项目

A powerful interface for extending AI capabilities through remote control, calculations, email operations, knowledge search, and more.

一个强大的接口，用于通过远程控制、计算、邮件操作、知识搜索等方式扩展AI能力。

## Overview | 概述

MCP (Model Context Protocol) is a protocol that allows servers to expose tools that can be invoked by language models. Tools enable models to interact with external systems, such as querying databases, calling APIs, or performing computations. Each tool is uniquely identified by a name and includes metadata describing its schema.

MCP（模型上下文协议）是一个允许服务器向语言模型暴露可调用工具的协议。这些工具使模型能够与外部系统交互，例如查询数据库、调用API或执行计算。每个工具都由一个唯一的名称标识，并包含描述其模式的元数据。

## Features | 特性

- 🔌 Bidirectional communication between AI and external tools | AI与外部工具之间的双向通信
- 🔄 Automatic reconnection with exponential backoff | 具有指数退避的自动重连机制
- 📊 Real-time data streaming | 实时数据流传输
- 🛠️ Easy-to-use tool creation interface | 简单易用的工具创建接口
- 🔒 Secure WebSocket communication | 安全的WebSocket通信
- ⚙️ Multiple transport types support (stdio/sse/http) | 支持多种传输类型（stdio/sse/http）

## Quick Start | 快速开始

1. Install dependencies | 安装依赖:
```bash
pip install -r requirements.txt
```

2. Set up your MCP endpoint (replace with your own endpoint and token) | 设置 MCP 端点（替换为你自己的端点与 token）:
```bash
export MCP_ENDPOINT="wss://<your-endpoint>/?token=<your-token>"
# Windows PowerShell
$env:MCP_ENDPOINT = "wss://<your-endpoint>/?token=<your-token>"
```

3. Provide Google credentials for Sheets/Docs access | 提供用于表格/文档的 Google 凭据:
```bash
# Provide raw JSON
export GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "service_account", ...}'
# Or point to a JSON file
export GOOGLE_SERVICE_ACCOUNT_FILE=/path/to/service_account.json
```

4. Start the Google Drive MCP server locally via stdio | 通过 stdio 本地启动 Google Drive MCP 服务:
```bash
python mcp_pipe.py google_drive.py
```

5. Or launch all servers defined in `mcp_config.json` (override with `MCP_CONFIG` if needed) | 或启动 `mcp_config.json` 中定义的所有服务（需要时可用 `MCP_CONFIG` 覆盖）:
```bash
python mcp_pipe.py
```

`mcp_pipe.py` will use stdio by default; you can also configure SSE/HTTP proxy transports through `mcp_config.json`. | `mcp_pipe.py` 默认使用 stdio；也可以通过 `mcp_config.json` 配置 SSE/HTTP 代理传输。

## Google Drive (Sheets + Docs) Tools | Google Drive（表格与文档）工具

`google_drive.py` provides both spreadsheet and document tools in a single server（没有单独的 `google_sheet.py` 文件）。

1. Required scopes | 需要的作用域：
   - Sheets: `https://www.googleapis.com/auth/spreadsheets`
   - Docs: `https://www.googleapis.com/auth/documents`

2. Configure credentials | 配置凭据：
   - `GOOGLE_SERVICE_ACCOUNT_JSON`: 服务账号原始 JSON（推荐）
   - 或 `GOOGLE_SERVICE_ACCOUNT_FILE`: 指向 JSON 凭据文件的路径

3. Available tools | 可用工具：
   - `update_sheet_values`: 覆盖指定的 Sheet 区域
   - `append_sheet_rows`: 向 Sheet 区域追加行
   - `append_document_text`: 向 Google 文档插入文本（默认末尾）
   - `replace_document_text`: 在 Google 文档中查找并替换文本
   - `set_document_text`: 用新文本覆盖整个 Google 文档

4. Example requests | 示例请求：
```jsonc
// Append text to the end of a doc
{
  "tool": "append_document_text",
  "arguments": {"document_id": "<doc-id>", "text": "Hello world"}
}

// Replace occurrences of "old" with "new"
{
  "tool": "replace_document_text",
  "arguments": {"document_id": "<doc-id>", "old_text": "old", "new_text": "new"}
}

// Replace the entire doc body
{
  "tool": "set_document_text",
  "arguments": {"document_id": "<doc-id>", "text": "All new content"}
}
```

## Project Structure | 项目结构

- `mcp_pipe.py`: 处理WebSocket连接和进程管理的主通信管道
- `mcp_config.json`: 服务器列表与传输配置
- `google_drive.py`: 提供 Google 表格与文档工具的 MCP 服务器
- `requirements.txt`: 项目依赖

## Config-driven Servers | 通过配置驱动的服务

编辑 `mcp_config.json` 文件来配置服务器列表（也可设置 `MCP_CONFIG` 环境变量指向其他配置文件）。

配置说明：
- 无参数时启动所有配置的服务（自动跳过 `disabled: true` 的条目）
- 有参数时运行单个本地脚本文件
- `type=stdio` 直接启动；`type=sse/http` 通过 `python -m mcp_proxy` 代理

## Creating Your Own MCP Tools | 创建自己的MCP工具

Here's a simple example of creating an MCP tool | 以下是一个创建MCP工具的简单示例:

```python
from fastmcp import FastMCP

mcp = FastMCP("YourToolName")

@mcp.tool()
def your_tool(parameter: str) -> dict:
    """Tool description here"""
    # Your implementation
    return {"success": True, "result": result}

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

## Use Cases | 使用场景

- 更新或追加 Google 表格数据
- 插入、替换或覆盖 Google 文档内容
- 自定义工具集成（基于 MCP 协议）

## Requirements | 环境要求

- Python 3.7+
- websockets>=11.0.3
- python-dotenv>=1.0.0
- mcp>=1.8.1
- pydantic>=2.11.4
- mcp-proxy>=0.8.2
- google-api-python-client>=2.149.0
- google-auth>=2.34.0
- google-auth-httplib2>=0.2.0

## Contributing | 贡献指南

Contributions are welcome! Please feel free to submit a Pull Request.

欢迎贡献代码！请随时提交PullRequest。

## License | 许可证

This project is licensed under the MIT License - see the LICENSE file for details.

本项目采用MIT许可证 - 详情请查看LICENSE文件。

## Acknowledgments | 致谢

- Thanks to all contributors who have helped shape this project | 感谢所有帮助塑造这个项目的贡献者
- Inspired by the need for extensible AI capabilities | 灵感来源于对可扩展AI能力的需求
