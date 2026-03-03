"""
测试 registry_baostock 模块
"""
import pytest
import os
import tempfile


class TestBaostockRegistry:
    """测试 BaostockRegistry 类"""

    @pytest.fixture
    def temp_docs(self):
        """创建临时文档目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_content = """
## 股票

接口: query_stock_basic

描述: 获取股票基本信息

输入参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| code | str | 股票代码 |

输出参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| code | str | 股票代码 |
| name | str | 股票名称 |
"""
            doc_path = os.path.join(tmpdir, "stock.md")
            with open(doc_path, "w") as f:
                f.write(doc_content)
            yield tmpdir

    def test_initialize(self, temp_docs):
        """测试初始化"""
        from src.mcp_akshare.registry_baostock import BaostockRegistry
        registry = BaostockRegistry(temp_docs)
        registry.initialize()
        assert len(registry.functions) > 0

    def test_search(self, temp_docs):
        """测试搜索"""
        from src.mcp_akshare.registry_baostock import BaostockRegistry
        registry = BaostockRegistry(temp_docs)
        registry.initialize()
        results = registry.search("股票")
        assert len(results) > 0

    def test_list_all(self, temp_docs):
        """测试列出所有函数"""
        from src.mcp_akshare.registry_baostock import BaostockRegistry
        registry = BaostockRegistry(temp_docs)
        registry.initialize()
        results = registry.list_all()
        assert len(results) > 0

    def test_get_categories(self, temp_docs):
        """测试获取分类"""
        from src.mcp_akshare.registry_baostock import BaostockRegistry
        registry = BaostockRegistry(temp_docs)
        registry.initialize()
        categories = registry.get_categories()
        assert len(categories) > 0


class TestBaostockExceptions:
    """测试异常类"""

    def test_function_not_found_error(self):
        """测试函数未找到异常"""
        from src.mcp_akshare.registry_baostock import FunctionNotFoundError
        error = FunctionNotFoundError("test_func")
        assert "test_func" in str(error)
        assert error.func_name == "test_func"

    def test_parameter_error(self):
        """测试参数错误异常"""
        from src.mcp_akshare.registry_baostock import ParameterError
        errors = ["invalid param"]
        error = ParameterError(errors)
        assert error.errors == errors

    def test_baostock_error(self):
        """测试 Baostock 错误"""
        from src.mcp_akshare.registry_baostock import BaostockError
        error = BaostockError("API error", "test_func")
        assert error.message == "API error"
        assert error.func_name == "test_func"
