"""
MCP AKShare Server - 提供 akshare 函数搜索和调用能力
"""

import asyncio
import json
import os
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
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


def log_call(func_name: str, params: dict, success: bool, error_msg: str = None):
    """记录调用日志"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "function": func_name,
        "params": params,
        "success": success,
    }
    if error_msg:
        log_entry["error"] = error_msg

    logger.info(f"CALL: {json.dumps(log_entry, ensure_ascii=False)}")


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
    results = registry.search(keyword, limit)

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
    log_entry = {
        "timestamp": start_time.isoformat(),
        "function": function,
        "params": params_dict,
        "duration_seconds": duration,
        "success": success,
    }
    if not success:
        log_entry["error"] = error_msg
    elif isinstance(result, dict) and "error" in result:
        # akshare 返回错误
        log_entry["success"] = False
        log_entry["error"] = result.get("error")

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

    with open(log_file, 'r') as f:
        lines = f.readlines()

    # 解析并返回最近的日志
    entries = []
    for line in lines[-limit:]:
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
    logger.info("MCP AKShare 服务启动")
    mcp.run()


if __name__ == "__main__":
    main()
