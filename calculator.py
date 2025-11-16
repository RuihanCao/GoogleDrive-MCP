# server.py
from fastmcp import FastMCP
import sys
import logging

logger = logging.getLogger('Calculator')

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

import math
import random

# Create an MCP server
mcp = FastMCP("Calculator")

# Add an addition tool
@mcp.tool()
def calculator(python_expression: str) -> dict:
    """Evaluate a Python math expression and return the result. The 'math' and 'random' modules are pre-imported and available. DO NOT use import statements. Examples: 'math.pi * 4**2', 'math.sqrt(16)', 'random.randint(1, 10)'."""
    result = eval(python_expression, {"math": math, "random": random})
    logger.info(f"Calculating formula: {python_expression}, result: {result}")
    return {"success": True, "result": result}

# Start the server
if __name__ == "__main__":
    mcp.run(transport="stdio")
