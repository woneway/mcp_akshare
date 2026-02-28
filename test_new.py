#!/usr/bin/env python3
"""测试 MCP AKShare 功能"""
import sys
sys.path.insert(0, 'src')

# 导入并初始化 - 使用正确的路径
from mcp_akshare.registry import DocRegistry
from mcp_akshare.formatters import format_search_results, format_result
import json

# 使用正确的文档目录创建注册表
registry = DocRegistry('/Users/lianwu/ai/mcp/mcp_akshare/akshare_docs')
registry.initialize()

print("=" * 60)
print("测试 1: 搜索 螺纹钢")
print("=" * 60)
results = registry.search('螺纹钢', limit=5)
print(format_search_results(results))

print("\n" + "=" * 60)
print("测试 2: 搜索 期货 库存")
print("=" * 60)
results = registry.search('期货 库存', limit=5)
print(format_search_results(results))

print("\n" + "=" * 60)
print("测试 3: 搜索 A股 实时行情")
print("=" * 60)
results = registry.search('A股 实时', limit=5)
print(format_search_results(results))

print("\n" + "=" * 60)
print("测试 4: 调用期货库存接口")
print("=" * 60)
result = registry.call('ak_futures_inventory_em', {'symbol': '螺纹钢'})
formatted = format_result(result)
print(json.dumps(formatted, ensure_ascii=False, indent=2)[:500])

print("\n" + "=" * 60)
print("测试 5: 调用 A股 实时行情接口")
print("=" * 60)
result = registry.call('ak_stock_zh_a_spot_em', {})
formatted = format_result(result)
print(json.dumps(formatted, ensure_ascii=False, indent=2)[:500])

print("\n" + "=" * 60)
print("✅ 所有测试完成!")
print("=" * 60)
