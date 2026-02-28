"""
响应格式化工具
"""

from typing import Any, Dict, List
import json
import pandas as pd
from datetime import date, datetime


def format_result(result: Any, max_rows: int = 100) -> Any:
    """格式化函数返回值"""
    if result is None:
        return {"message": "无数据"}

    # 错误响应
    if isinstance(result, dict) and "error" in result:
        return result

    # DataFrame 转换
    if isinstance(result, pd.DataFrame):
        return _format_dataframe(result, max_rows)

    # Series 转换
    if isinstance(result, pd.Series):
        return result.to_dict()

    # 列表包含 DataFrame
    if isinstance(result, list):
        return _format_list(result, max_rows)

    # 字典包含 DataFrame
    if isinstance(result, dict):
        return _format_dict(result, max_rows)

    # 原始类型直接返回
    return result


def _format_dataframe(df: pd.DataFrame, max_rows: int) -> Dict:
    """格式化 DataFrame"""
    # 限制行数
    if len(df) > max_rows:
        df = df.head(max_rows)
        truncated = True
    else:
        truncated = False

    # 转换日期类型
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == "object":
            # 尝试检测日期
            sample = df[col].dropna().iloc[:10] if len(df) > 0 else []
            if len(sample) > 0:
                try:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                except Exception:
                    pass

    # 转换为字典
    data = df.to_dict(orient="records")

    # 转换日期为字符串
    for record in data:
        for key, value in record.items():
            if isinstance(value, (pd.Timestamp, datetime, date)):
                record[key] = str(value)
            elif pd.isna(value):
                record[key] = None

    result = {"data": data}

    if truncated:
        result["warning"] = f"数据已截断，只显示前 {max_rows} 行"
        result["total_rows"] = len(df)

    return result


def _format_list(items: List, max_rows: int) -> Any:
    """格式化列表"""
    if not items:
        return {"data": []}

    # 列表中包含 DataFrame
    if len(items) > 0 and isinstance(items[0], pd.DataFrame):
        result = []
        for i, df in enumerate(items[:max_rows]):
            formatted = _format_dataframe(df, max_rows)
            result.append(formatted)

        if len(items) > max_rows:
            return {
                "data": result,
                "warning": f"只显示前 {max_rows} 个",
            }
        return {"data": result}

    # 普通列表
    return {"data": items}


def _format_dict(data: Dict, max_rows: int) -> Dict:
    """格式化字典"""
    result = {}
    for key, value in data.items():
        if isinstance(value, pd.DataFrame):
            result[key] = _format_dataframe(value, max_rows)
        elif isinstance(value, (list, dict)):
            result[key] = format_result(value, max_rows)
        else:
            result[key] = value
    return result


def format_search_results(results: List[Dict]) -> str:
    """格式化搜索结果为可读文本"""
    if not results:
        return "未找到匹配的函数"

    lines = [f"找到 {len(results)} 个匹配的函数:\n"]

    for i, r in enumerate(results, 1):
        params_str = ", ".join([p["name"] for p in r.get("params", [])])
        # 显示 full_name（带 ak_ 前缀的完整名称）
        full_name = r.get('full_name', r.get('name', ''))
        lines.append(f"{i}. **{full_name}**")
        lines.append(f"   描述: {r['description']}")
        lines.append(f"   分类: {r['category']}")
        if params_str:
            lines.append(f"   参数: {params_str}")
        lines.append("")

    return "\n".join(lines)
