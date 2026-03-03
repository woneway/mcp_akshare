## 腾讯股票数据

### 实时行情

接口: quote

描述: 获取股票实时行情

输入参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| codes | str | 股票代码，多个用逗号分隔，如 "sh600000,sz000001" |

输出参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| code | str | 股票代码 |
| name | str | 股票名称 |
| price | float | 当前价格 |
| change | float | 涨跌额 |
| change_pct | float | 涨跌幅 |
| volume | float | 成交量(手) |
| amount | float | 成交额(元) |
| open | float | 开盘价 |
| high | float | 最高价 |
| low | float | 最低价 |
| close | float | 昨收价 |
| time | str | 更新时间 |

---

接口: realtime

描述: 获取单支股票实时行情(详细)

输入参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| code | str | 股票代码，如 "sh600000" |

输出参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| code | str | 股票代码 |
| name | str | 股票名称 |
| price | float | 当前价格 |
| change | float | 涨跌额 |
| change_pct | float | 涨跌幅 |
| volume | float | 成交量(手) |
| amount | float | 成交额(元) |
| open | float | 开盘价 |
| high | float | 最高价 |
| low | float | 最低价 |
| close | float | 昨收价 |
| bid1 | float | 买一价 |
| bid2 | float | 买二价 |
| bid3 | float | 买三价 |
| bid4 | float | 买四价 |
| bid5 | float | 买五价 |
| ask1 | float | 卖一价 |
| ask2 | float | 卖二价 |
| ask3 | float | 卖三价 |
| ask4 | float | 卖四价 |
| ask5 | float | 卖五价 |
| time | str | 更新时间 |

---

### 板块行情

接口: industry

描述: 获取板块行情

输入参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| industry | str | 板块名称，如 "银行" |

输出参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| code | str | 股票代码 |
| name | str | 股票名称 |
| price | float | 当前价格 |
| change_pct | float | 涨跌幅 |
| volume | float | 成交量 |
