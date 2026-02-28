#!/usr/bin/env python3
"""测试 MCP AKShare 功能"""

import sys

sys.path.insert(0, "src")

from mcp_akshare.registry import registry
from mcp_akshare.formatters import format_result, format_search_results


def test_search():
    """测试搜索功能"""
    print("=" * 50)
    print("测试搜索功能")
    print("=" * 50)

    # 测试关键词搜索
    keywords = ["期货", "股票", "GDP", "ETF"]
    for kw in keywords:
        results = registry.search(kw, limit=5)
        print(f"\n搜索 '{kw}': 找到 {len(results)} 个")
        for r in results[:3]:
            print(f"  - {r['name']}: {r['description'][:40]}...")


def test_function_info():
    """测试获取函数信息"""
    print("\n" + "=" * 50)
    print("测试函数信息")
    print("=" * 50)

    # 获取一个函数的信息
    info = registry.get_function("ak_general_stock_zh_a_spot_em")
    if info:
        print(f"函数名: {info.name}")
        print(f"完整名: {info.full_name}")
        print(f"分类: {info.category}")
        print(f"描述: {info.description}")
        print(f"参数: {info.params}")


def test_tools_list():
    """测试工具列表"""
    print("\n" + "=" * 50)
    print("测试工具列表")
    print("=" * 50)

    # 模拟 MCP tools 列表
    tools = [
        {
            "name": "ak_search",
            "description": "搜索 akshare 函数",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "搜索关键词"},
                    "limit": {"type": "integer", "description": "返回数量"},
                },
            },
        },
        {
            "name": "ak_call",
            "description": "调用 akshare 函数",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "function": {
                        "type": "string",
                        "description": "函数名 (从搜索结果获取 full_name)",
                    },
                    "params": {
                        "type": "string",
                        "description": "JSON 格式参数",
                    },
                },
            },
        },
    ]

    for tool in tools:
        print(f"\n工具: {tool['name']}")
        print(f"描述: {tool['description']}")
        print(f"参数: {tool['inputSchema']['properties'].keys()}")


def main():
    print("🔍 初始化注册表...")
    registry.initialize()

    test_search()
    test_function_info()
    test_tools_list()

    print("\n" + "=" * 50)
    print("✅ 所有测试完成!")
    print("=" * 50)


if __name__ == "__main__":
    main()
