#!/usr/bin/env python3
"""MCP AKShare 功能验收测试"""
import sys
sys.path.insert(0, 'src')

from mcp_akshare.registry import DocRegistry
from mcp_akshare.formatters import format_search_results, format_result
import json

# 使用正确的文档目录创建注册表
registry = DocRegistry('/Users/lianwu/ai/mcp/mcp_akshare/akshare_docs')
registry.initialize()

print("=" * 60)
print("验收测试 1: 搜索期货库存接口")
print("=" * 60)
results = registry.search('期货 库存', limit=5)
print(format_search_results(results))
assert len(results) > 0, "应该找到期货库存相关函数"
assert any('inventory' in r['name'].lower() for r in results), "应该包含 inventory 函数"

print("\n" + "=" * 60)
print("验收测试 2: 调用期货库存接口")
print("=" * 60)
result = registry.call('ak_futures_inventory_em', {'symbol': '螺纹钢'})
# DataFrame 有 len 属性
if hasattr(result, '__len__'):
    print(f"✅ 返回 {len(result)} 条数据")
else:
    print(f"✅ 返回结果: {result}")

print("\n" + "=" * 60)
print("验收测试 3: 搜索 A股实时行情接口")
print("=" * 60)
results = registry.search('A股 实时行情', limit=5)
print(format_search_results(results))
assert len(results) > 0, "应该找到 A股实时行情相关函数"

print("\n" + "=" * 60)
print("验收测试 4: 搜索 index 指数接口")
print("=" * 60)
results = registry.search('指数', limit=5)
print(format_search_results(results))

print("\n" + "=" * 60)
print("验收测试 5: 函数信息完整性")
print("=" * 60)
info = registry.get_function('ak_futures_inventory_em')
print(f"名称: {info.name}")
print(f"分类: {info.category}")
print(f"描述: {info.description}")
print(f"参数: {info.params}")
assert info.category == "futures", "分类应该是 futures"
assert info.name == "futures_inventory_em", "名称应该正确"

print("\n" + "=" * 60)
print("✅ 所有验收测试通过!")
print("=" * 60)
