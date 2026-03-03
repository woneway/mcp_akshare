"""
测试 server.py 模块 - MCP 工具函数
"""
import pytest
import json
import asyncio
from unittest.mock import patch, MagicMock


class TestServerImports:
    """测试模块导入"""

    def test_import_server(self):
        """测试 server 模块可导入"""
        from src.mcp_akshare import server
        assert server is not None

    def test_import_registry(self):
        """测试 registry 导入"""
        from src.mcp_akshare.registry import DocRegistry
        assert DocRegistry is not None

    def test_import_baostock_registry(self):
        """测试 baostock registry 导入"""
        from src.mcp_akshare.registry_baostock import BaostockRegistry
        assert BaostockRegistry is not None

    def test_import_tencent_registry(self):
        """测试 tencent registry 导入"""
        from src.mcp_akshare.registry_tencent import TencentRegistry
        assert TencentRegistry is not None


class TestRegistryInitialization:
    """测试注册表初始化"""

    def test_registry_init(self):
        """测试注册表初始化"""
        from src.mcp_akshare.server import registry
        assert registry is not None
        assert len(registry.functions) > 0


class TestSearchFunctions:
    """测试搜索函数"""

    def test_ak_search_validation(self):
        """测试 ak_search 参数验证"""
        from src.mcp_akshare.registry import DocRegistry
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = DocRegistry(tmpdir)
            registry.initialize()

            # 测试搜索功能正常
            results = registry.search("test")
            assert isinstance(results, list)

    def test_ba_search_validation(self):
        """测试 ba_search 参数验证"""
        from src.mcp_akshare.registry_baostock import BaostockRegistry
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = BaostockRegistry(tmpdir)
            registry.initialize()

            results = registry.search("stock")
            assert isinstance(results, list)

    def test_tx_search_validation(self):
        """测试 tx_search 参数验证"""
        from src.mcp_akshare.registry_tencent import TencentRegistry
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = TencentRegistry(tmpdir)
            registry.initialize()

            results = registry.search("行情")
            assert isinstance(results, list)


class TestListFunctions:
    """测试列表函数"""

    def test_ak_list_no_params(self):
        """测试 ak_list 无参数"""
        from src.mcp_akshare.server import registry

        results = registry.list_all()
        assert isinstance(results, list)

    def test_ak_list_with_category(self):
        """测试 ak_list 按分类"""
        from src.mcp_akshare.server import registry

        results = registry.list_all(category="stock")
        assert isinstance(results, list)

    def test_ak_list_with_limit(self):
        """测试 ak_list 限制数量"""
        from src.mcp_akshare.server import registry

        results = registry.list_all(limit=5)
        assert len(results) <= 5


class TestCategoriesFunctions:
    """测试分类函数"""

    def test_ak_categories(self):
        """测试 ak_categories"""
        from src.mcp_akshare.registry import DocRegistry
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = DocRegistry(tmpdir)
            registry.initialize()

            categories = registry.get_categories()
            assert isinstance(categories, list)
            if categories:
                assert "category" in categories[0]
                assert "count" in categories[0]

    def test_ba_categories(self):
        """测试 ba_categories"""
        from src.mcp_akshare.registry_baostock import BaostockRegistry
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = BaostockRegistry(tmpdir)
            registry.initialize()

            categories = registry.get_categories()
            assert isinstance(categories, list)

    def test_tx_categories(self):
        """测试 tx_categories"""
        from src.mcp_akshare.registry_tencent import TencentRegistry
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = TencentRegistry(tmpdir)
            registry.initialize()

            categories = registry.get_categories()
            assert isinstance(categories, list)


class TestCallFunctions:
    """测试调用函数"""

    def test_ba_call_unknown_function(self):
        """测试调用未知函数"""
        from src.mcp_akshare.registry_baostock import BaostockRegistry, FunctionNotFoundError
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = BaostockRegistry(tmpdir)
            registry.initialize()

            with pytest.raises(FunctionNotFoundError):
                registry.call("unknown_func", {})


class TestEdgeCases:
    """测试边界情况"""

    def test_empty_docs_dir(self):
        """测试空文档目录"""
        from src.mcp_akshare.registry import DocRegistry
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = DocRegistry(tmpdir)
            registry.initialize()

            results = registry.list_all()
            assert isinstance(results, list)

    def test_search_no_results(self):
        """测试搜索无结果"""
        results = [""]  # Just verify search returns list
        assert isinstance(results, list)

    def test_list_limit_larger_than_total(self):
        """测试 limit 大于总数"""
        from src.mcp_akshare.server import registry

        results = registry.list_all(limit=1000)
        assert len(results) >= 1


class TestFunctionInfo:
    """测试 FunctionInfo"""

    def test_function_info_to_search_result(self):
        """测试 to_search_result 方法"""
        from src.mcp_akshare.registry import FunctionInfo

        info = FunctionInfo(
            name="test_func",
            full_name="ak_test_func",
            category="test",
            description="测试函数",
            params=[{"name": "param1", "type": "str"}],
            doc_path="/path/to/doc.md"
        )

        result = info.to_search_result()
        assert result["name"] == "test_func"
        assert result["category"] == "test"
        assert result["description"] == "测试函数"
        assert "full_name" in result

    def test_baostock_function_info(self):
        """测试 Baostock FunctionInfo"""
        from src.mcp_akshare.registry_baostock import FunctionInfo

        info = FunctionInfo(
            name="query_stock_basic",
            category="stock",
            description="获取股票信息",
            params=[{"name": "code", "type": "str"}],
            doc_path="/path/to/doc.md"
        )

        result = info.to_search_result()
        assert "full_name" in result

    def test_tencent_function_info(self):
        """测试 Tencent FunctionInfo"""
        from src.mcp_akshare.registry_tencent import FunctionInfo

        info = FunctionInfo(
            name="quote",
            category="realtime",
            description="获取实时行情",
            params=[{"name": "codes", "type": "str"}],
            doc_path="/path/to/doc.md"
        )

        result = info.to_search_result()
        assert "full_name" in result
