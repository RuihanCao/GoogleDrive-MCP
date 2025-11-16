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

2. Set up environment variables | 设置环境变量:
```bash
export MCP_ENDPOINT=<your_mcp_endpoint>
for windows:
$env:MCP_ENDPOINT=<your_mcp_endpoint>
```

3. Prepare Google Sheets credentials | 准备 Google Sheets 凭据：

   1. In the Google Cloud Console, create (or reuse) a project and enable the **Google Sheets API**.
   2. Create a **Service Account** under *IAM & Admin → Service Accounts*, then generate a key of type **JSON** and download the file (e.g., `service_account.json`).
   3. Share any target spreadsheets with the service account’s email (it looks like `name@project.iam.gserviceaccount.com`) and give it edit access.
   4. Export the credential path (or paste the JSON string directly) so the MCP server can authenticate:

```bash
export GOOGLE_SERVICE_ACCOUNT_JSON="<PATH_TO_JSON>"
for windows:
$env:GOOGLE_SERVICE_ACCOUNT_JSON = "<PATH_TO_JSON>"
```

4. Run the Google Sheets MCP server | 运行 Google Sheets MCP 服务:
```bash
python mcp_pipe.py google_sheets_mcp.py

Or run all configured servers | 或运行所有配置的服务:
```bash
python mcp_pipe.py
```

*Requires `mcp_config.json` configuration file with server definitions (supports stdio/sse/http transport types)*

*需要 `mcp_config.json` 配置文件定义服务器（支持 stdio/sse/http 传输类型）*

## How to test the Google Sheets MCP | 如何测试 Google 表格 MCP

1. **Create/share a test spreadsheet** | **创建/共享测试表格**  
   Create a Google Sheet, note its spreadsheet ID (the long value in the URL), and share it with the service account email from your JSON key, giving edit access. | 创建一个 Google 表格，记录其 ID（URL 中的长字符串），并将其共享给服务账号邮箱，授予编辑权限。

2. **Export credentials** | **导出凭据**  
   Make sure the environment variable still points to your JSON credentials file or raw JSON text: | 确保环境变量仍然指向您的 JSON 凭据文件或原始 JSON 文本：
   ```bash
   export GOOGLE_SERVICE_ACCOUNT_JSON=/path/to/service_account.json
   ```

3. **Run the server** | **运行服务**  
   ```bash
   python -m google_sheets_mcp
   ```
   Leave this process running so a client can connect. | 保持该进程运行，以便客户端连接。

4. **Interact with the MCP server** | **与 MCP 服务交互**  
   Use any MCP client (e.g., [Model Context Protocol Inspector](https://github.com/modelcontextprotocol/inspector)) to send tool requests. With the inspector installed (`npm install -g @modelcontextprotocol/inspector`), you can point it at the stdio server like this: | 使用任意 MCP 客户端（如 [Model Context Protocol Inspector](https://github.com/modelcontextprotocol/inspector)）发送工具请求。安装 inspector (`npm install -g @modelcontextprotocol/inspector`) 后，可通过以下方式连接 stdio 服务：
   ```bash
   mcp-inspector "python -m google_sheets_mcp"
   ```
   Then call the tools (e.g., `list_worksheets`, `append_rows`, `read_range`) with your spreadsheet ID and worksheet name to verify read/write access. | 然后调用工具（如 `list_worksheets`、`append_rows`、`read_range`），使用您的表格 ID 和工作表名称验证读写权限。

5. **Optional Python smoke test (no MCP client needed)** | **可选的 Python 冒烟测试（无需 MCP 客户端）**  
   If you only want to confirm credentials and sheet access, you can run a quick script that uses the same code paths as the tools: | 若仅想确认凭据和表格访问，可运行一个使用相同代码路径的简易脚本：
   ```bash
   python - <<'PY'
   from google_sheets_mcp import list_worksheets, append_rows, read_range, clear_range

   SPREADSHEET_ID = "your-spreadsheet-id"
   SHEET = "Sheet1"

   print("Listing worksheets...")
   print(list_worksheets(SPREADSHEET_ID))

   print("Appending a test row...")
   append_rows(SPREADSHEET_ID, SHEET, [["MCP Smoke Test", "OK"]])

   print("Reading the last rows...")
   print(read_range(SPREADSHEET_ID, SHEET, "A1:B10"))

   print("Clearing the test row...")
   print(clear_range(SPREADSHEET_ID, SHEET, "A1:B10"))
   PY
   ```
   Successful responses (and visible changes in the sheet) indicate the MCP server has working credentials and permissions. | 出现成功的响应（且表格中能看到对应变化）表示 MCP 服务的凭据和权限正常。

## Project Structure | 项目结构

- `mcp_pipe.py`: Main communication pipe that handles WebSocket connections and process management | 处理WebSocket连接和进程管理的主通信管道
- `google_sheets_mcp.py`: MCP tool implementation for reading/writing Google Sheets | 用于读取/写入 Google 表格的 MCP 工具
- `requirements.txt`: Project dependencies | 项目依赖

## Google Sheets tools | Google 表格工具

- `list_worksheets`: List all worksheet names in a spreadsheet | 列出表格中的所有工作表名称
- `read_range`: Read cell values from a range (e.g., `A1:C10`) | 从指定范围读取单元格数据
- `write_range`: Overwrite a block of cells starting at a top-left cell | 从指定起始单元格覆盖写入一块数据
- `append_rows`: Append rows to the end of a worksheet | 在工作表末尾追加行
- `clear_range`: Clear the contents of a range | 清除指定范围的内容

## Google Sheets tools | Google 表格工具

- `list_worksheets`: List all worksheet names in a spreadsheet | 列出表格中的所有工作表名称
- `read_range`: Read cell values from a range (e.g., `A1:C10`) | 从指定范围读取单元格数据
- `write_range`: Overwrite a block of cells starting at a top-left cell | 从指定起始单元格覆盖写入一块数据
- `append_rows`: Append rows to the end of a worksheet | 在工作表末尾追加行
- `clear_range`: Clear the contents of a range | 清除指定范围的内容
=======
- `calculator.py`: Example MCP tool implementation for mathematical calculations | 用于数学计算的MCP工具示例实现
- `requirements.txt`: Project dependencies | 项目依赖

## Google Sheets tools | Google 表格工具

- `list_worksheets`: List all worksheet names in a spreadsheet | 列出表格中的所有工作表名称
- `read_range`: Read cell values from a range (e.g., `A1:C10`) | 从指定范围读取单元格数据
- `write_range`: Overwrite a block of cells starting at a top-left cell | 从指定起始单元格覆盖写入一块数据
- `append_rows`: Append rows to the end of a worksheet | 在工作表末尾追加行
- `clear_range`: Clear the contents of a range | 清除指定范围的内容
>>>>>>> theirs

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

- Mathematical calculations | 数学计算
- Email operations | 邮件操作
- Knowledge base search | 知识库搜索
- Remote device control | 远程设备控制
- Data processing | 数据处理
- Custom tool integration | 自定义工具集成

## Requirements | 环境要求

- Python 3.7+
- websockets>=11.0.3
- python-dotenv>=1.0.0
- mcp>=1.8.1
- pydantic>=2.11.4
- mcp-proxy>=0.8.2

## Contributing | 贡献指南

Contributions are welcome! Please feel free to submit a Pull Request.

欢迎贡献代码！请随时提交Pull Request。

## License | 许可证

This project is licensed under the MIT License - see the LICENSE file for details.

本项目采用MIT许可证 - 详情请查看LICENSE文件。

## Acknowledgments | 致谢

- Thanks to all contributors who have helped shape this project | 感谢所有帮助塑造这个项目的贡献者
- Inspired by the need for extensible AI capabilities | 灵感来源于对可扩展AI能力的需求
