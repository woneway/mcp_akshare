"""
AKShare 函数注册表 - 基于文档文件解析
分类 = 文件名 (如 stock, futures, index 等)
"""

import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import akshare as ak


@dataclass
class FunctionInfo:
    """函数元信息"""
    name: str           # 函数名 (不含模块前缀)
    full_name: str      # 完整名称 (category_function)
    category: str       # 分类 = 文件名 (stock, futures, index 等)
    description: str   # 描述
    params: List[Dict] # 参数列表
    doc_path: str      # 文档路径

    def to_search_result(self) -> Dict:
        # 返回搜索结果
        # 去掉 ak_ 前缀
        display_name = self.full_name
        if display_name.startswith("ak_"):
            display_name = display_name[3:]
        return {
            "name": display_name,
            "description": self.description,
            "category": self.category,
            "params": self.params,
            "full_name": self.full_name,
        }


class DocRegistry:
    """基于文档的注册表"""

    def __init__(self, docs_dir: str):
        self.docs_dir = docs_dir
        self.functions: Dict[str, FunctionInfo] = {}
        self._index: Dict[str, List[str]] = {}
        self._initialized = False

    def initialize(self):
        """解析所有文档文件"""
        if self._initialized:
            return

        print(f"📄 解析 akshare 文档 from {self.docs_dir}...")
        self._parse_all_docs()
        self._build_index()
        print(f"✅ 已索引 {len(self.functions)} 个函数")
        self._initialized = True

    def _parse_all_docs(self):
        """解析所有文档目录下的 .md 文件"""
        if not os.path.isdir(self.docs_dir):
            print(f"⚠️ 文档目录不存在: {self.docs_dir}")
            return

        for filename in os.listdir(self.docs_dir):
            if not filename.endswith('.md'):
                continue

            category = filename[:-3]  # 去掉 .md 后缀
            filepath = os.path.join(self.docs_dir, filename)
            self._parse_doc_file(filepath, category)

    def _parse_doc_file(self, filepath: str, category: str):
        """解析单个文档文件"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析每个接口块
        # 格式: 接口: 函数名 ... (直到下一个接口: 或文件结束)
        interface_pattern = r'接口:\s*(\w+)\s*\n(.*?)(?=\n接口:\s*\w+\s*\n|\Z)'
        matches = re.findall(interface_pattern, content, re.DOTALL)

        for func_name, block in matches:
            # 解析描述
            description = ""
            desc_match = re.search(r'描述:\s*([^\n]+)', block)
            if desc_match:
                description = desc_match.group(1).strip()

            # 解析输入参数
            params = []
            # 更精确的匹配：从"输入参数"标题到表格结束（下一个空行或输出参数）
            input_match = re.search(r'输入参数\s*\n((?:\|[^\n]+\n)+)', block)
            if input_match:
                table_lines = input_match.group(1).strip().split('\n')
                for line in table_lines:
                    # 跳过表头
                    if '---' in line or '名称' in line or '类型' in line:
                        continue
                    # 匹配参数行: | name | type | ...
                    # 参数名只能是字母数字下划线
                    match = re.match(r'\|\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\|', line)
                    if match:
                        param_name = match.group(1)
                        # 提取类型（第二列）
                        type_match = re.search(r'\|[^\|]+\|([^\|]+)\|', line)
                        param_type = type_match.group(1).strip() if type_match else 'string'
                        params.append({
                            "name": param_name,
                            "type": param_type,
                        })

            # 生成完整名称，避免重复
            # 例如: category="futures", func_name="futures_inventory_em" -> "ak_futures_inventory_em"
            if func_name.startswith(f"{category}_"):
                full_name = f"ak_{func_name}"
            else:
                full_name = f"ak_{category}_{func_name}"

            info = FunctionInfo(
                name=func_name,
                full_name=full_name,
                category=category,
                description=description,
                params=params,
                doc_path=filepath,
            )

            self.functions[full_name] = info

    def _build_index(self):
        """构建搜索索引"""
        for full_name, info in self.functions.items():
            # 关键词: 分类, 函数名, 描述词
            keywords = [info.category, info.name]

            # 从描述提取关键词
            if info.description:
                words = re.findall(r"[\w]+", info.description)
                keywords.extend(words)

            # 从参数名提取关键词
            for p in info.params:
                keywords.append(p.get("name", ""))

            for kw in keywords:
                kw = kw.lower()
                if kw not in self._index:
                    self._index[kw] = []
                if full_name not in self._index[kw]:
                    self._index[kw].append(full_name)

    def search(self, keyword: str, limit: int = 20) -> List[Dict]:
        """搜索函数 - 支持分词搜索"""
        keyword = keyword.lower().strip()
        results = set()

        # 分词搜索：将关键词按空格分开，每个词都要匹配
        words = keyword.split()

        # 收集所有匹配的函数
        all_matches = {}
        for word in words:
            word_results = set()
            # 精确匹配
            if word in self._index:
                word_results.update(self._index[word])
            # 模糊匹配
            for kw, funcs in self._index.items():
                if word in kw or kw in word:
                    word_results.update(funcs)

            # 记录每个词的匹配结果
            for func in word_results:
                all_matches[func] = all_matches.get(func, 0) + 1

        # 只返回所有词都匹配的函数
        for func, match_count in all_matches.items():
            if match_count == len(words):
                results.add(func)

        # 转换为结果
        output = []
        for full_name in list(results)[:limit]:
            if full_name in self.functions:
                output.append(self.functions[full_name].to_search_result())

        return output

    def get_function(self, full_name: str) -> Optional[FunctionInfo]:
        """获取函数信息"""
        return self.functions.get(full_name)

    def call(self, func_name: str, params: Dict) -> Any:
        """调用函数 - 支持带或不带 ak_ 前缀"""
        # 尝试查找函数
        info = None
        # 1. 直接查找（不带前缀）
        if func_name in self.functions:
            info = self.functions[func_name]
        # 2. 查找带 ak_ 前缀的
        elif f"ak_{func_name}" in self.functions:
            info = self.functions[f"ak_{func_name}"]

        if info is None:
            raise ValueError(f"未找到函数: {func_name}")

        # 获取实际的 akshare 函数名
        actual_func_name = info.name

        try:
            # 直接从 akshare 主模块调用
            func = getattr(ak, actual_func_name, None)
            if func is None:
                raise ValueError(f"无法找到函数: {actual_func_name}")

            result = func(**params)
            return result

        except Exception as e:
            return {"error": str(e)}


def _get_default_docs_dir():
    """获取默认文档目录路径 - 直接使用绝对路径避免 __file__ 问题"""
    # 直接使用绝对路径
    abs_path = '/Users/lianwu/ai/mcp/mcp_akshare/akshare_docs'

    if os.path.exists(abs_path):
        return abs_path

    # 回退：相对于本文件的路径
    base_dir = os.path.dirname(__file__)
    relative_path = os.path.join(base_dir, 'akshare_docs')

    if os.path.exists(relative_path):
        return relative_path

    return abs_path


# 默认注册表实例
registry = DocRegistry(_get_default_docs_dir())
