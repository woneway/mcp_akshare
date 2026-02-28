#!/bin/bash

# AKShare 数据字典下载脚本

# 所有数据分类
CATEGORIES=(
    "stock/stock"
    "futures/futures"
    "bond/bond"
    "option/option"
    "fx/fx"
    "currency/currency"
    "spot/spot"
    "interest_rate/interest_rate"
    "fund/fund_private"
    "fund/fund_public"
    "index/index"
    "macro/macro"
    "dc/dc"
    "bank/bank"
    "article/article"
    "energy/energy"
    "event/event"
    "hf/hf"
    "nlp/nlp"
    "qdii/qdii"
    "others/others"
    "qhkc/index"
    "tool/tool"
)

BASE_URL="https://akshare.akfamily.xyz/_sources/data"
OUTPUT_DIR="."

echo "开始下载 AKShare 数据字典..."
echo "================================"

for cat in "${CATEGORIES[@]}"; do
    # 提取分类名称用于文件名
    filename=$(basename "$cat")
    output_file="${OUTPUT_DIR}/${filename}.md"
    url="${BASE_URL}/${cat}.md.txt"

    echo "下载: ${filename}.md"
    curl -s "$url" -o "$output_file"

    if [ -s "$output_file" ]; then
        echo "  -> 成功保存到 ${output_file}"
    else
        echo "  -> 失败或文件为空!"
        rm -f "$output_file"
    fi
done

echo "================================"
echo "下载完成!"
ls -la *.md
