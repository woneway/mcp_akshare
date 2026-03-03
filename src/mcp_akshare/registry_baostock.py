"""
Baostock 函数注册表 - 基于文档文件解析
"""

import os
import re
import logging
import baostock as bs
import pandas as pd
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# 预编译正则表达式
_INTERFACE_PATTERN = re.compile(r'接口:\s*(\w+)\s*\n(.*?)(?=\n接口:\s*\w+\s*\n|\Z)', re.DOTALL)
_DESC_PATTERN = re.compile(r'描述:\s*([^\n]+)')
_INPUT_PARAMS_PATTERN = re.compile(r'输入参数\s*\n((?:\|[^\n]+\n)+)')
_PARAM_ROW_PATTERN = re.compile(r'\|\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\|')


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


class BaostockError(RegistryError):
    """Baostock 执行错误"""
    def __init__(self, message: str, func_name: str = None):
        self.message = message
        self.func_name = func_name
        super().__init__(f"Baostock 执行错误: {message}")


@dataclass
class FunctionInfo:
    """函数元信息"""
    name: str           # 函数名
    category: str       # 分类
    description: str   # 描述
    params: List[Dict] # 参数列表
    doc_path: str      # 文档路径

    def to_search_result(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "params": self.params,
            "full_name": f"ba_{self.name}",
        }


class BaostockRegistry:
    """基于文档的 Baostock 注册表"""

    def __init__(self, docs_dir: str):
        self.docs_dir = docs_dir
        self.functions: Dict[str, FunctionInfo] = {}
        self._index: Dict[str, List[str]] = {}
        self._initialized = False
        self._logged_in = False

    def initialize(self):
        """解析所有文档文件"""
        if self._initialized:
            return

        logger.info(f"解析 baostock 文档 from {self.docs_dir}...")
        self._parse_all_docs()
        self._build_index()
        logger.info(f"已索引 {len(self.functions)} 个 baostock 函数")
        self._initialized = True

    def _login(self):
        """登录 baostock"""
        if not self._logged_in:
            lg = bs.login()
            if lg.error_code != '0':
                raise BaostockError(f"登录失败: {lg.error_msg}")
            self._logged_in = True

    def _logout(self):
        """登出 baostock"""
        if self._logged_in:
            bs.logout()
            self._logged_in = False

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
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

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

            full_name = f"ba_{func_name}"
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
        # 处理 ba_ 前缀
        if func_name.startswith("ba_"):
            func_name = func_name[3:]

        info = None
        if func_name in self.functions:
            info = self.functions[func_name]
        elif f"ba_{func_name}" in self.functions:
            info = self.functions[f"ba_{func_name}"]

        if info is None:
            raise FunctionNotFoundError(func_name)

        # 验证参数
        param_errors = self._validate_params(info, params)
        if param_errors:
            raise ParameterError(param_errors)

        # 登录
        self._login()

        # 调用 baostock 函数
        try:
            func = getattr(bs, info.name, None)
            if func is None:
                raise FunctionNotFoundError(info.name)

            # 处理参数 - baostock 有些参数是可选的
            call_params = {}
            for p in info.params:
                pname = p["name"]
                if pname in params and params[pname] is not None:
                    call_params[pname] = params[pname]

            result = func(**call_params)

            # 转换为 DataFrame
            if result:
                data_list = []
                while result.next():
                    data_list.append(result.get_row_data())
                if data_list:
                    df = pd.DataFrame(data_list, columns=result.fields)
                    # 预处理：替换空字符串和 NaN 为空字符串
                    df = df.fillna('')
                    for col in df.columns:
                        df[col] = df[col].replace([None, 'None', ''], '')
                        df[col] = df[col].astype(str)
                    return df

            return pd.DataFrame()

        except TypeError as e:
            raise ParameterError([str(e)])
        except Exception as e:
            raise BaostockError(str(e), info.name)
        finally:
            # 不登出，保持连接
            pass

    def _validate_params(self, info: FunctionInfo, params: Dict) -> List[str]:
        """验证参数"""
        errors = []
        param_names = {p["name"] for p in info.params}

        for key in params:
            if key not in param_names:
                errors.append(f"未知参数: {key}，可用参数: {list(param_names)}")

        return errors
