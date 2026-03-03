"""
测试 registry_tencent 模块
"""
import pytest
import os
import tempfile
import pandas as pd
from unittest.mock import patch, MagicMock


class TestTencentRegistry:
    """测试 TencentRegistry 类"""

    @pytest.fixture
    def temp_docs(self):
        """创建临时文档目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_content = """
## 实时行情

接口: quote

描述: 获取股票实时行情

输入参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| codes | str | 股票代码 |

输出参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| code | str | 股票代码 |
| name | str | 股票名称 |
"""
            doc_path = os.path.join(tmpdir, "tencent.md")
            with open(doc_path, "w") as f:
                f.write(doc_content)
            yield tmpdir

    def test_initialize(self, temp_docs):
        """测试初始化"""
        from src.mcp_akshare.registry_tencent import TencentRegistry
        registry = TencentRegistry(temp_docs)
        registry.initialize()
        assert len(registry.functions) > 0

    def test_search(self, temp_docs):
        """测试搜索"""
        from src.mcp_akshare.registry_tencent import TencentRegistry
        registry = TencentRegistry(temp_docs)
        registry.initialize()
        results = registry.search("行情")
        assert len(results) > 0

    def test_list_all(self, temp_docs):
        """测试列出所有函数"""
        from src.mcp_akshare.registry_tencent import TencentRegistry
        registry = TencentRegistry(temp_docs)
        registry.initialize()
        results = registry.list_all()
        assert len(results) > 0

    def test_get_categories(self, temp_docs):
        """测试获取分类"""
        from src.mcp_akshare.registry_tencent import TencentRegistry
        registry = TencentRegistry(temp_docs)
        registry.initialize()
        categories = registry.get_categories()
        assert len(categories) > 0


class TestTencentCall:
    """测试 TencentRegistry 调用功能"""

    @pytest.fixture
    def registry(self):
        """创建注册表实例"""
        from src.mcp_akshare.registry_tencent import TencentRegistry
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_content = """
## 实时行情

接口: quote

描述: 获取股票实时行情

输入参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| codes | str | 股票代码 |

接口: realtime

描述: 获取单支股票实时行情

输入参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| code | str | 股票代码 |
"""
            doc_path = os.path.join(tmpdir, "tencent.md")
            with open(doc_path, "w") as f:
                f.write(doc_content)

            reg = TencentRegistry(tmpdir)
            reg.initialize()
            yield reg

    @patch('src.mcp_akshare.registry_tencent.requests.Session.get')
    def test_call_quote_success(self, mock_get, registry):
        """测试成功调用 quote"""
        mock_response = MagicMock()
        mock_response.text = 'v_sh600000="1~浦发银行~600000~9.73~9.68~9.66~1129364~620566~508798~9.72~1943~9.71~3322~9.70~3037~9.69~7033~9.68~3896~9.73~1548~9.74~3709~9.75~2214~9.76~1110~9.77~1070~~20260303161410~0.05~0.52~9.82~9.61~9.73/1129364/1098196732~1129364~109820~0.34~6.48~~9.82~9.61~2.17~3240.66~3240.66~0.44~10.65~8.71~1.52~9580~9.72~6.48~6.48~~~0.56~109819.6732~0.0000~0~ ~GP-A~-21.78~-1.72~3.83~5.87~0.50~14.39~9.05~-4.42~-5.99~-16.27~33305838300~33305838300~33.17~-18.71~33305838300~~~-0.10~0.10~~CNY~0~___D__F__N~9.82~-12500~";'
        mock_get.return_value = mock_response

        result = registry.call('tx_quote', {'codes': 'sh600000'})
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]['code'] == 'sh600000'

    def test_call_function_not_found(self, registry):
        """测试函数未找到"""
        from src.mcp_akshare.registry_tencent import FunctionNotFoundError
        with pytest.raises(FunctionNotFoundError):
            registry.call('tx_nonexist', {})

    def test_call_missing_params(self, registry):
        """测试缺少参数"""
        from src.mcp_akshare.registry_tencent import ParameterError
        with pytest.raises(ParameterError):
            registry.call('tx_quote', {})


class TestTencentExceptions:
    """测试异常类"""

    def test_function_not_found_error(self):
        """测试函数未找到异常"""
        from src.mcp_akshare.registry_tencent import FunctionNotFoundError
        error = FunctionNotFoundError("test_func")
        assert "test_func" in str(error)

    def test_parameter_error(self):
        """测试参数错误异常"""
        from src.mcp_akshare.registry_tencent import ParameterError
        errors = ["invalid param"]
        error = ParameterError(errors)
        assert error.errors == errors

    def test_tencent_error(self):
        """测试 Tencent 错误"""
        from src.mcp_akshare.registry_tencent import TencentError
        error = TencentError("API error", "test_func")
        assert error.message == "API error"
        assert error.func_name == "test_func"
