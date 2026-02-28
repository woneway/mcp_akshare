# MCP AKShare

## MCP 配置

```json
{
  "mcpServers": {
    "akshare": {
      "command": "python3",
      "args": ["/Users/lianwu/ai/mcp/mcp_akshare/run.py"]
    }
  }
}
```

## 使用方法

1. **搜索函数**: `ak_search(keyword="期货")`
2. **调用函数**: `ak_call(function="函数名", params='{}')`

## 示例

```
用户: 查询螺纹钢期货行情

AI:
1. ak_search("螺纹钢 期货")
2. ak_call(function="ak_general_futures_zh_daily_sina", params='{"symbol":"rb2405"}')
```
