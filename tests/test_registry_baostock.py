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


class TestBaostockCall:
    """测试 BaostockRegistry 调用功能"""

    @pytest.fixture
    def registry(self):
        """创建注册表实例"""
        from src.mcp_akshare.registry_baostock import BaostockRegistry
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            doc_content = """
## 股票

接口: query_stock_basic

描述: 获取股票基本信息

输入参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| code | str | 股票代码 |
"""
            doc_path = os.path.join(tmpdir, "stock.md")
            with open(doc_path, "w") as f:
                f.write(doc_content)

            reg = BaostockRegistry(tmpdir)
            reg.initialize()
            yield reg

    def test_call_with_prefix(self, registry):
        """测试带 ba_ 前缀调用"""
        # 函数已注册为 ba_query_stock_basic
        info = registry.get_function("ba_query_stock_basic")
        assert info is not None

    def test_call_with_wrong_params(self, registry):
        """测试错误参数"""
        from src.mcp_akshare.registry_baostock import ParameterError
        with pytest.raises(ParameterError):
            registry.call("query_stock_basic", {"wrong_param": "value"})

    def test_validate_params(self, registry):
        """测试参数验证"""
        info = registry.get_function("ba_query_stock_basic")
        errors = registry._validate_params(info, {"extra": "param"})
        assert len(errors) > 0


class TestBaostockSearch:
    """测试搜索功能"""

    @pytest.fixture
    def registry(self):
        """创建注册表实例"""
        from src.mcp_akshare.registry_baostock import BaostockRegistry
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            doc_content = """
## 股票

接口: query_stock_basic

描述: 获取股票基本信息

接口: query_stock_industry

描述: 获取股票所属行业

## 行情

接口: query_history_k_data

描述: 获取历史K线
"""
            doc_path = os.path.join(tmpdir, "stock.md")
            with open(doc_path, "w") as f:
                f.write(doc_content)

            reg = BaostockRegistry(tmpdir)
            reg.initialize()
            yield reg

    def test_search_single_word(self, registry):
        """测试单词搜索"""
        results = registry.search("股票")
        assert len(results) > 0

    def test_search_multiple_words(self, registry):
        """测试多词搜索"""
        results = registry.search("股票 基本")
        assert isinstance(results, list)

    def test_search_no_match(self, registry):
        """测试无匹配搜索"""
        results = registry.search("完全不存在的词xyz123")
        assert results == []

    def test_search_with_limit(self, registry):
        """测试搜索限制数量"""
        results = registry.search("股票", limit=1)
        assert len(results) <= 1


class TestBaostockList:
    """测试列表功能"""

    @pytest.fixture
    def registry(self):
        """创建注册表实例"""
        from src.mcp_akshare.registry_baostock import BaostockRegistry
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            doc_content = """
## 股票

接口: query_stock_basic

描述: 获取股票基本信息
"""
            doc_path = os.path.join(tmpdir, "stock.md")
            with open(doc_path, "w") as f:
                f.write(doc_content)

            reg = BaostockRegistry(tmpdir)
            reg.initialize()
            yield reg

    def test_list_all(self, registry):
        """测试列出所有"""
        results = registry.list_all()
        assert len(results) > 0

    def test_list_by_category(self, registry):
        """测试按分类列出"""
        results = registry.list_all(category="股票")
        assert isinstance(results, list)

    def test_list_with_limit(self, registry):
        """测试限制数量"""
        results = registry.list_all(limit=1)
        assert len(results) <= 1


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

    def test_registry_error(self):
        """测试注册表基础异常"""
        from src.mcp_akshare.registry_baostock import RegistryError
        error = RegistryError("Base error")
        assert "Base error" in str(error)
