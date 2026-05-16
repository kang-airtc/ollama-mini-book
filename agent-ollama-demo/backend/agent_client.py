#!/usr/bin/env python3
"""
MCP Client - 调用 Agent Server 的 Tools
"""

import asyncio
import json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def call_agent_tool(tool_name: str, arguments: dict = None):
    """
    调用 Agent Server 的 Tool，返回结果字符串
    """
    if arguments is None:
        arguments = {}

    async with streamable_http_client(url="http://localhost:8001/mcp") as (
        read,
        write,
        _session_id_callback,
    ):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(tool_name, arguments)

            # 提取文本结果
            for content in result.content:
                if content.type == "text":
                    return content.text

            return json.dumps({"error": "No text content in result"})


async def call_search_tickets_semantic(query: str, n_results: int = 5):
    """
    调用语义搜索工具 - 使用向量相似度搜索工单

    Args:
        query: 自然语言查询
        n_results: 返回结果数量

    Returns:
        搜索结果 JSON 字符串
    """
    return await call_agent_tool(
        "search_tickets_semantic", {"query": query, "n_results": n_results}
    )


if __name__ == "__main__":
    # 简单测试
    async def test():
        print("测试语义搜索...")
        result = await call_search_tickets_semantic("退款问题", 3)
        print(result)

    asyncio.run(test())
