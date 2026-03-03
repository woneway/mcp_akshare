"""
Tencent 股票数据注册表 - 基于 HTTP API
"""

import os
import re
import logging
import requests
import pandas as pd
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# 腾讯行情API基础URL
TX_BASE_URL = "http://qt.gtimg.cn/q="

# 预编译正则表达式
_INTERFACE_PATTERN = re.compile(r'接口:\s*(\w+)\s*\n(.*?)(?=\n接口:\s*\w+\s*\n|\Z)', re.DOTALL)
_DESC_PATTERN = re.compile(r'描述:\s*([^\n]+)')
_INPUT_PARAMS_PATTERN = re.compile(r'输入参数\s*\n((?:\|[^\n]+\n)+)')
_PARAM_ROW_PATTERN = re.compile(r'\|\s*(\w+)\s*\|')


class RegistryError(Exception):
    """注册表基础异常"""
    pass


class FunctionNotFoundError(RegistryError):
    """函数未找到"""
    def __init__(self, func_name: str):
        self.func_name = func_name
        super().__init__(f"未找到函数: {func_name}")


class ParameterError(RegistryError):
    """参数错误"""
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"参数错误: {'; '.join(errors)}")


class TencentError(RegistryError):
    """Tencent API 执行错误"""
    def __init__(self, message: str, func_name: str = None):
        self.message = message
        self.func_name = func_name
        super().__init__(f"Tencent API 错误: {message}")


@dataclass
class FunctionInfo:
    """函数元信息"""
    name: str           # 函数名
    category: str       # 分类
    description: str    # 描述
    params: List[Dict] # 参数列表
    doc_path: str      # 文档路径

    def to_search_result(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "params": self.params,
            "full_name": f"tx_{self.name}",
        }


class TencentRegistry:
    """基于 HTTP API 的 Tencent 注册表"""

    def __init__(self, docs_dir: str):
        self.docs_dir = docs_dir
        self.functions: Dict[str, FunctionInfo] = {}
        self._index: Dict[str, List[str]] = {}
        self._initialized = False
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def initialize(self):
        """解析所有文档文件"""
        if self._initialized:
            return

        logger.info(f"解析 tencent 文档 from {self.docs_dir}...")
        self._parse_all_docs()
        self._build_index()
        logger.info(f"已索引 {len(self.functions)} 个 tencent 函数")
        self._initialized = True

    def _parse_all_docs(self):
        """解析所有文档目录下的 .md 文件"""
        if not os.path.isdir(self.docs_dir):
            logger.warning(f"文档目录不存在: {self.docs_dir}")
            return

        try:
            filenames = os.listdir(self.docs_dir)
        except OSError as e:
            logger.error(f"读取文档目录失败: {e}")
            return

        for filename in filenames:
            if not filename.endswith('.md'):
                continue

            category = filename[:-3]
            filepath = os.path.join(self.docs_dir, filename)
            self._parse_doc_file(filepath, category)

    def _parse_doc_file(self, filepath: str, category: str):
        """解析单个文档文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"读取文档失败 {filepath}: {e}")
            return

        matches = _INTERFACE_PATTERN.findall(content)

        for func_name, block in matches:
            # 解析描述
            description = ""
            desc_match = _DESC_PATTERN.search(block)
            if desc_match:
                description = desc_match.group(1).strip()

            # 解析输入参数
            params = []
            input_match = _INPUT_PARAMS_PATTERN.search(block)
            if input_match:
                table_lines = input_match.group(1).strip().split('\n')
                for line in table_lines:
                    if '---' in line or '名称' in line or '类型' in line:
                        continue
                    match = _PARAM_ROW_PATTERN.match(line)
                    if match:
                        param_name = match.group(1)
                        type_match = re.search(r'\|[^\|]+\|([^\|]+)\|', line)
                        param_type = type_match.group(1).strip() if type_match else 'string'
                        params.append({
                            "name": param_name,
                            "type": param_type,
                        })

            full_name = f"tx_{func_name}"
            info = FunctionInfo(
                name=func_name,
                category=category,
                description=description,
                params=params,
                doc_path=filepath,
            )

            self.functions[full_name] = info

    def _build_index(self):
        """构建搜索索引"""
        for full_name, info in self.functions.items():
            keywords = [info.category, info.name]

            if info.description:
                words = re.findall(r"[\w]+", info.description)
                keywords.extend(words)

            for p in info.params:
                keywords.append(p.get("name", ""))

            for kw in keywords:
                kw = kw.lower()
                if kw not in self._index:
                    self._index[kw] = []
                if full_name not in self._index[kw]:
                    self._index[kw].append(full_name)

    def search(self, keyword: str, limit: int = 20) -> List[Dict]:
        """搜索函数"""
        keyword = keyword.lower().strip()
        results = set()

        words = keyword.split()
        all_matches = {}

        for word in words:
            word_results = set()
            if word in self._index:
                word_results.update(self._index[word])
            for kw, funcs in self._index.items():
                if word in kw or kw in word:
                    word_results.update(funcs)

            for func in word_results:
                all_matches[func] = all_matches.get(func, 0) + 1

        for func, match_count in all_matches.items():
            if match_count == len(words):
                results.add(func)

        output = []
        for full_name in list(results)[:limit]:
            if full_name in self.functions:
                output.append(self.functions[full_name].to_search_result())

        return output

    def get_function(self, full_name: str) -> Optional[FunctionInfo]:
        """获取函数信息"""
        return self.functions.get(full_name)

    def list_all(self, category: str = None, limit: int = 100) -> List[Dict]:
        """列出所有函数"""
        funcs = list(self.functions.values())

        if category:
            funcs = [f for f in funcs if f.category == category]

        funcs.sort(key=lambda x: (x.category, x.name))
        funcs = funcs[:limit]

        return [f.to_search_result() for f in funcs]

    def get_categories(self) -> List[Dict]:
        """获取所有分类"""
        categories = {}
        for func in self.functions.values():
            cat = func.category
            if cat not in categories:
                categories[cat] = {"category": cat, "count": 0}
            categories[cat]["count"] += 1

        return sorted(categories.values(), key=lambda x: x["category"])

    def call(self, func_name: str, params: Dict) -> Any:
        """调用函数"""
        # 处理 tx_ 前缀
        if func_name.startswith("tx_"):
            func_name = func_name[3:]

        info = None
        if func_name in self.functions:
            info = self.functions[func_name]
        elif f"tx_{func_name}" in self.functions:
            info = self.functions[f"tx_{func_name}"]

        if info is None:
            raise FunctionNotFoundError(func_name)

        # 验证参数
        param_errors = self._validate_params(info, params)
        if param_errors:
            raise ParameterError(param_errors)

        # 根据函数名调用对应的处理方法
        try:
            if info.name == "quote":
                return self._call_quote(params)
            elif info.name == "realtime":
                return self._call_realtime(params)
            elif info.name == "industry":
                return self._call_industry(params)
            else:
                raise FunctionNotFoundError(info.name)
        except TencentError:
            raise
        except Exception as e:
            raise TencentError(str(e), info.name)

    def _validate_params(self, info: FunctionInfo, params: Dict) -> List[str]:
        """验证参数"""
        errors = []
        param_names = {p["name"] for p in info.params}

        for key in params:
            if key not in param_names:
                errors.append(f"未知参数: {key}，可用参数: {list(param_names)}")

        return errors

    def _call_quote(self, params: Dict) -> pd.DataFrame:
        """调用实时行情接口"""
        codes = params.get("codes", "")
        if not codes:
            raise ParameterError(["缺少必需参数: codes"])

        # 调用腾讯API
        url = f"{TX_BASE_URL}{codes}"
        try:
            response = self._session.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            raise TencentError(f"API请求失败: {e}")

        # 解析返回数据
        return self._parse_quote_response(response.text)

    def _call_realtime(self, params: Dict) -> pd.DataFrame:
        """调用单支股票实时行情"""
        code = params.get("code", "")
        if not code:
            raise ParameterError(["缺少必需参数: code"])

        # 调用腾讯API
        url = f"{TX_BASE_URL}{code}"
        try:
            response = self._session.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            raise TencentError(f"API请求失败: {e}")

        # 解析返回数据
        return self._parse_quote_response(response.text)

    def _call_industry(self, params: Dict) -> pd.DataFrame:
        """调用板块行情"""
        # 腾讯API不直接支持板块查询，返回提示信息
        raise TencentError("板块行情接口暂未实现，请使用 tx_quote 或 tx_realtime")

    def _parse_quote_response(self, text: str) -> pd.DataFrame:
        """解析腾讯API返回的数据"""
        # 腾讯返回格式: v_sh600000="数据"
        # 数据格式: 1~股票名称~代码~当前价~昨收~...等49个字段

        results = []
        # 使用换行符和分号分割
        lines = text.strip().replace('\n', '').split(';')

        for line in lines:
            if not line or '=' not in line:
                continue

            # 解析 v_code="..."
            match = re.match(r'v_([^=]+)="([^"]*)"', line)
            if not match:
                continue

            code = match.group(1)
            data_str = match.group(2)

            if not data_str or data_str == '""':
                continue

            # 解析数据字段 ~ 分隔
            fields = data_str.split('~')

            if len(fields) < 10:
                continue

            # 字段映射 (参考腾讯API文档)
            record = {
                'code': code,
                'name': fields[1] if len(fields) > 1 else '',  # 股票名称
                'price': self._safe_float(fields[3]),          # 当前价格
                'change': self._safe_float(fields[4]),          # 涨跌额
                'change_pct': self._safe_float(fields[5]),      # 涨跌幅
                'volume': self._safe_float(fields[6]),         # 成交量(手)
                'amount': self._safe_float(fields[7]),         # 成交额(元)
                'open': self._safe_float(fields[8]),           # 开盘价
                'high': self._safe_float(fields[9]),           # 最高价
                'low': self._safe_float(fields[10]),           # 最低价
                'close': self._safe_float(fields[2]),           # 昨收价
                'bid1': self._safe_float(fields[11]),          # 买一价
                'bid2': self._safe_float(fields[12]),          # 买二价
                'bid3': self._safe_float(fields[13]),          # 买三价
                'bid4': self._safe_float(fields[14]),           # 买四价
                'bid5': self._safe_float(fields[15]),          # 买五价
                'bid_vol1': self._safe_float(fields[16]),      # 买一量
                'bid_vol2': self._safe_float(fields[17]),      # 买二量
                'bid_vol3': self._safe_float(fields[18]),      # 买三量
                'bid_vol4': self._safe_float(fields[19]),      # 买四量
                'bid_vol5': self._safe_float(fields[20]),      # 买五量
                'ask1': self._safe_float(fields[21]),          # 卖一价
                'ask2': self._safe_float(fields[22]),          # 卖二价
                'ask3': self._safe_float(fields[23]),          # 卖三价
                'ask4': self._safe_float(fields[24]),          # 卖四价
                'ask5': self._safe_float(fields[25]),          # 卖五价
                'ask_vol1': self._safe_float(fields[26]),      # 卖一量
                'ask_vol2': self._safe_float(fields[27]),      # 卖二量
                'ask_vol3': self._safe_float(fields[28]),      # 卖三量
                'ask_vol4': self._safe_float(fields[29]),      # 卖四量
                'ask_vol5': self._safe_float(fields[30]),      # 卖五量
                'date': fields[31] if len(fields) > 31 else '', # 日期
                'time': fields[32] if len(fields) > 32 else '', # 时间
            }

            results.append(record)

        if not results:
            return pd.DataFrame()

        df = pd.DataFrame(results)

        # 预处理：替换空字符串和 NaN
        df = df.fillna('')
        for col in df.columns:
            df[col] = df[col].replace([None, 'None', ''], '')

        return df

    def _safe_float(self, value: str) -> Any:
        """安全转换为浮点数"""
        if not value or value == '-':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
