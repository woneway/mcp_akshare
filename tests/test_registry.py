"""
测试 registry 模块
"""
import pytest
import os
import tempfile
import pandas as pd


class TestDocRegistry:
    """测试 DocRegistry 类"""

    @pytest.fixture
    def temp_docs(self):
        """创建临时文档目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建测试文档
            doc_content = """
## 测试分类

接口: test_func

描述: 测试函数

输入参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| param1 | str | 参数1 |

输出参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| result | str | 结果 |
"""
            doc_path = os.path.join(tmpdir, "test.md")
            with open(doc_path, "w") as f:
                f.write(doc_content)
            yield tmpdir

    def test_initialize(self, temp_docs):
        """测试初始化"""
        from src.mcp_akshare.registry import DocRegistry
        registry = DocRegistry(temp_docs)
        registry.initialize()
        assert len(registry.functions) > 0

    def test_search(self, temp_docs):
        """测试搜索功能"""
        from src.mcp_akshare.registry import DocRegistry
        registry = DocRegistry(temp_docs)
        registry.initialize()
        results = registry.search("测试")
        assert len(results) > 0

    def test_list_all(self, temp_docs):
        """测试列出所有函数"""
        from src.mcp_akshare.registry import DocRegistry
        registry = DocRegistry(temp_docs)
        registry.initialize()
        results = registry.list_all()
        assert len(results) > 0

    def test_get_categories(self, temp_docs):
        """测试获取分类"""
        from src.mcp_akshare.registry import DocRegistry
        registry = DocRegistry(temp_docs)
        registry.initialize()
        categories = registry.get_categories()
        assert len(categories) > 0
        assert "category" in categories[0]
        assert "count" in categories[0]


class TestExceptions:
    """测试异常类"""

    def test_function_not_found_error(self):
        """测试函数未找到异常"""
        from src.mcp_akshare.registry import FunctionNotFoundError
        error = FunctionNotFoundError("test_func")
        assert "test_func" in str(error)
        assert error.func_name == "test_func"

    def test_parameter_error(self):
        """测试参数错误异常"""
        from src.mcp_akshare.registry import ParameterError
        errors = ["param1 is required", "param2 must be int"]
        error = ParameterError(errors)
        assert error.errors == errors
        assert "param1 is required" in str(error)

    def test_akshare_error(self):
        """测试 Akshare 错误"""
        from src.mcp_akshare.registry import AkshareError
        error = AkshareError("Network error", "test_func")
        assert error.message == "Network error"
        assert error.func_name == "test_func"
