"""
MCP AKShare Server - 提供 akshare 函数搜索和调用能力
"""

import argparse
import asyncio
import json
import os
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler

import pandas as pd
from fastmcp import FastMCP

from .registry import DocRegistry, FunctionNotFoundError, ParameterError, AkshareError
from .formatters import format_result, format_search_results

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志目录 - 使用项目根目录下的 logs
LOG_DIR = os.environ.get('AKSHARE_LOG_DIR', os.path.join(PROJECT_ROOT, 'logs'))

# 配置日志 - 使用轮转
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, 'akshare.log')

# 轮转日志：单文件10MB，保留5个备份
rotating_handler = RotatingFileHandler(
    log_file,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)

# 配置日志 - 避免重复添加 handler
root_logger = logging.getLogger()
if not root_logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            rotating_handler,
            logging.StreamHandler()
        ]
    )
logger = logging.getLogger(__name__)

# 创建 MCP 服务
mcp = FastMCP("akshare")

# 初始化注册表 - 使用文档目录
docs_dir = os.environ.get('AKSHARE_DOCS_DIR', os.path.join(PROJECT_ROOT, 'akshare_docs'))
registry = DocRegistry(docs_dir)
registry.initialize()


@mcp.tool()
async def ak_search(keyword: str, limit: int = 20) -> str:
    """
    搜索 akshare 函数。

    根据关键词搜索可用函数，返回匹配的函数元数据。
    支持按函数名、描述、分类搜索。

    Args:
        keyword: 搜索关键词，如 "期货"、"股票"、"GDP" 等
        limit: 返回结果数量，默认 20

    Returns:
        匹配的函数列表，包含名称、描述、分类、参数等信息
    """
    start_time = datetime.now()
    try:
        results = registry.search(keyword, limit)
    except Exception as e:
        logger.error(f"搜索失败: {e}", exc_info=True)
        return f"搜索失败: {str(e)}"
    duration = (datetime.now() - start_time).total_seconds()

    # 记录搜索日志
    logger.info(json.dumps({
        "timestamp": start_time.isoformat(),
        "type": "search",
        "keyword": keyword,
        "limit": limit,
        "duration_seconds": duration,
        "result_count": len(results),
    }, ensure_ascii=False))

    if not results:
        return f"未找到包含 '{keyword}' 的函数，请尝试其他关键词"

    return format_search_results(results)


@mcp.tool()
async def ak_call(function: str, params: str = "{}") -> str:
    """
    调用 akshare 函数。

    通用函数调用器，可以调用任意 akshare 函数。
    先用 ak_search 找到函数名，然后用 ak_call 调用。

    Args:
        function: 函数全名，如 "stock_lhb_detail_daily_sina"
        params: JSON 格式参数字典，如 '{"date": "20260227"}'

    Returns:
        函数执行结果
    """
    # 解析参数
    params_dict = {}
    try:
        if isinstance(params, str):
            params_dict = json.loads(params) if params.strip() else {}
        else:
            params_dict = params
    except json.JSONDecodeError as e:
        log_call(function, params, False, f"参数解析错误: {e}")
        return f"参数解析错误: {e}"

    # 调用函数 - 使用线程池避免阻塞事件循环
    start_time = datetime.now()
    try:
        result = await asyncio.to_thread(registry.call, function, params_dict)
        success = True
        error_msg = None
    except FunctionNotFoundError as e:
        result = {"error": str(e), "type": "FunctionNotFound"}
        success = False
        error_msg = str(e)
    except ParameterError as e:
        result = {"error": str(e), "type": "ParameterError", "details": e.errors}
        success = False
        error_msg = str(e)
    except AkshareError as e:
        result = {"error": e.message, "type": "AkshareError", "function": e.func_name}
        success = False
        error_msg = str(e)
    except Exception as e:
        result = {"error": str(e), "type": "UnknownError"}
        success = False
        error_msg = str(e)

    # 记录日志
    duration = (datetime.now() - start_time).total_seconds()

    # 确定错误类型
    error_type = None
    if not success:
        if isinstance(result, dict):
            error_type = result.get("type", "UnknownError")
        else:
            error_type = "UnknownError"

    # 统计返回数据量
    result_rows = None
    if success and result is not None:
        if isinstance(result, pd.DataFrame):
            result_rows = len(result)
        elif isinstance(result, list):
            result_rows = len(result)
        elif isinstance(result, dict) and "data" in result:
            if isinstance(result["data"], list):
                result_rows = len(result["data"])

    log_entry = {
        "timestamp": start_time.isoformat(),
        "function": function,
        "params": params_dict,
        "duration_seconds": duration,
        "success": success,
        "error_type": error_type,
        "result_rows": result_rows,
    }
    if not success:
        log_entry["error"] = error_msg
    elif isinstance(result, dict) and "error" in result:
        # akshare 返回错误
        log_entry["success"] = False
        log_entry["error"] = result.get("error")
        log_entry["error_type"] = "AkshareReturnedError"

    logger.info(f"CALL: {json.dumps(log_entry, ensure_ascii=False)}")

    # 格式化输出
    formatted = format_result(result)

    # 转为 JSON 字符串返回
    return json.dumps(formatted, ensure_ascii=False, indent=2)


@mcp.tool()
async def ak_logs(limit: int = 50) -> str:
    """
    查看调用日志。

    Args:
        limit: 返回最近的记录数，默认 50

    Returns:
        调用日志列表
    """
    log_file = os.path.join(LOG_DIR, 'akshare.log')
    if not os.path.exists(log_file):
        return "暂无调用记录"

    # 使用 deque 高效获取最后 limit 行，避免加载整个文件
    from collections import deque
    last_lines = deque(open(log_file, 'r'), maxlen=limit)

    # 解析并返回最近的日志
    entries = []
    for line in last_lines:
        if 'CALL:' in line:
            try:
                entry = json.loads(line.split('CALL:')[1].strip())
                entries.append(entry)
            except:
                pass

    # 反转顺序，最新的在前
    entries.reverse()

    return json.dumps(entries, ensure_ascii=False, indent=2)


def main():
    """启动服务"""
    parser = argparse.ArgumentParser(description="MCP AKShare Server")
    parser.add_argument("--mode", default="stdio",
                        choices=["stdio", "http", "sse", "streamable-http"],
                        help="传输模式: stdio(默认), http, sse, streamable-http")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址")
    parser.add_argument("--port", type=int, default=8000, help="监听端口")
    args = parser.parse_args()

    logger.info(f"MCP AKShare 服务启动 (模式: {args.mode})")

    if args.mode == "stdio":
        mcp.run()
    else:
        mcp.run(transport=args.mode, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
