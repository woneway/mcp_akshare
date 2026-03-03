"""
测试 formatters 模块
"""
import pytest
import pandas as pd
from datetime import date, datetime


class TestFormatResult:
    """测试 format_result 函数"""

    def test_format_none(self):
        """测试 None 输入"""
        from src.mcp_akshare.formatters import format_result
        result = format_result(None)
        assert result == {"message": "无数据"}

    def test_format_error_response(self):
        """测试错误响应"""
        from src.mcp_akshare.formatters import format_result
        result = format_result({"error": "some error"})
        assert result == {"error": "some error"}

    def test_format_dataframe(self):
        """测试 DataFrame 格式化"""
        from src.mcp_akshare.formatters import format_result
        df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
        result = format_result(df)
        assert "data" in result
        assert len(result["data"]) == 2

    def test_format_dataframe_truncated(self):
        """测试 DataFrame 截断"""
        from src.mcp_akshare.formatters import format_result
        df = pd.DataFrame({"value": range(150)})
        result = format_result(df, max_rows=100)
        assert "warning" in result
        assert result["total_rows"] == 150

    def test_format_series(self):
        """测试 Series 格式化"""
        from src.mcp_akshare.formatters import format_result
        series = pd.Series([1, 2, 3])
        result = format_result(series)
        assert result == {0: 1, 1: 2, 2: 3}

    def test_format_list(self):
        """测试列表格式化"""
        from src.mcp_akshare.formatters import format_result
        result = format_result([1, 2, 3])
        assert result == {"data": [1, 2, 3]}

    def test_format_list_with_dataframes(self):
        """测试包含 DataFrame 的列表"""
        from src.mcp_akshare.formatters import format_result
        df1 = pd.DataFrame({"a": [1]})
        df2 = pd.DataFrame({"a": [2]})
        result = format_result([df1, df2])
        assert "data" in result
        assert len(result["data"]) == 2

    def test_format_dict(self):
        """测试字典格式化"""
        from src.mcp_akshare.formatters import format_result
        result = format_result({"key": "value"})
        assert result == {"key": "value"}

    def test_format_primitive(self):
        """测试原始类型"""
        from src.mcp_akshare.formatters import format_result
        assert format_result("hello") == "hello"
        assert format_result(123) == 123
        assert format_result(True) is True


class TestFormatSearchResults:
    """测试 format_search_results 函数"""

    def test_empty_results(self):
        """测试空结果"""
        from src.mcp_akshare.formatters import format_search_results
        result = format_search_results([])
        assert "未找到" in result

    def test_single_result(self):
        """测试单条结果"""
        from src.mcp_akshare.formatters import format_search_results
        results = [{
            "name": "test_func",
            "description": "测试函数",
            "category": "test",
            "params": [{"name": "param1", "type": "str"}]
        }]
        result = format_search_results(results)
        assert "test_func" in result
        assert "测试函数" in result

    def test_multiple_results(self):
        """测试多条结果"""
        from src.mcp_akshare.formatters import format_search_results
        results = [
            {"name": "func1", "description": "函数1", "category": "cat1", "params": []},
            {"name": "func2", "description": "函数2", "category": "cat2", "params": []},
        ]
        result = format_search_results(results)
        assert "找到 2 个" in result
