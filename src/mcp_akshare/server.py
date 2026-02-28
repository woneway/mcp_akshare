"""
MCP AKShare Server - 提供 akshare 函数搜索和调用能力
"""

import json
import os
from fastmcp import FastMCP

from .registry import DocRegistry
from .formatters import format_result, format_search_results

# 创建 MCP 服务
mcp = FastMCP("akshare")

# 初始化注册表 - 使用文档目录
# 直接使用绝对路径
docs_dir = '/Users/lianwu/ai/mcp/mcp_akshare/akshare_docs'
registry = DocRegistry(docs_dir)
registry.initialize()


@mcp.tool()
async def ak_search(keyword: str, limit: int = 20) -> str:
    """
    搜索 akshare 函数。

    根据关键词搜索可用函数，返回匹配的函数元数据。
    支持按函数名、描述、分类搜索。

    Args:
        keyword: 搜索关键词，如 "期货"、"股票"、"GDP" 等
        limit: 返回结果数量，默认 20

    Returns:
        匹配的函数列表，包含名称、描述、分类、参数等信息
    """
    results = registry.search(keyword, limit)

    if not results:
        return f"未找到包含 '{keyword}' 的函数，请尝试其他关键词"

    return format_search_results(results)


@mcp.tool()
async def ak_call(function: str, params: str = "{}") -> str:
    """
    调用 akshare 函数。

    通用函数调用器，可以调用任意 akshare 函数。
    先用 ak_search 找到函数名，然后用 ak_call 调用。

    Args:
        function: 函数全名，如 "ak_stock_zh_a_spot_em"
        params: JSON 格式参数字典，如 '{"symbol": "000001"}'

    Returns:
        函数执行结果
    """
    # 解析参数
    try:
        if isinstance(params, str):
            params_dict = json.loads(params)
        else:
            params_dict = params
    except json.JSONDecodeError as e:
        return f"参数解析错误: {e}"

    # 调用函数
    result = registry.call(function, params_dict)

    # 格式化输出
    formatted = format_result(result)

    # 转为 JSON 字符串返回
    return json.dumps(formatted, ensure_ascii=False, indent=2)


def main():
    """启动服务"""
    mcp.run()


if __name__ == "__main__":
    main()
