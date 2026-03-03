## [Baostock](https://github.com/wenjianyuan/Baostock) 股票数据

### 股票基础信息

接口: query_stock_basic

描述: 获取股票基本信息

输入参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| code | str | 股票代码，默认为空查询全部，如 "sh.600000" |
| code_name | str | 股票名称模糊查询，默认为空 |

输出参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| code | str | 股票代码 |
| code_name | str | 股票名称 |
| ipoDate | str | 上市日期 |
| outDate | str | 退市日期 |
| type | str | 股票类型 |
| status | str | 上市状态 |

---

接口: query_stock_industry

描述: 获取股票所属行业

输入参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| code | str | 股票代码，如 "sh.600000" |

输出参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| code | str | 股票代码 |
| code_name | str | 股票名称 |
| industry | str | 所属行业 |
| industry_category | str | 行业类别 |

---

### 行情数据

接口: query_history_k_data_plus

描述: 获取历史 K 线数据

输入参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| code | str | 股票代码，如 "sh.600000" |
| fields | str | 想要获取的字段，默认为全部 |
| start_date | str | 开始日期，格式 yyyy-MM-dd |
| end_date | str | 结束日期，格式 yyyy-MM-dd |
| frequency | str | 数据频率，d=日线，w=周线，m=月线 |
| adjustflag | str | 复权类型，1=后复权，2=前复权，3=不复权 |

输出参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| date | str | 日期 |
| code | str | 股票代码 |
| open | float | 开盘价 |
| high | float | 最高价 |
| low | float | 最低价 |
| close | float | 收盘价 |
| volume | float | 成交量 |
| amount | float | 成交额 |
| adjustflag | str | 复权类型 |

---

接口: query_trade_dates

描述: 获取交易日历

输入参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| start_date | str | 开始日期，格式 yyyy-MM-dd |
| end_date | str | 结束日期，格式 yyyy-MM-dd |

输出参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| calendar_date | str | 日期 |
| is_trading_day | str | 是否交易日 |

---

### 财务数据

接口: query_profit_data

描述: 获取利润表数据

输入参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| code | str | 股票代码，如 "sh.600000" |
| year | int | 报告年份，如 2024 |
| quarter | int | 报告季度，1-4 |

输出参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| code | str | 股票代码 |
| report_date | str | 报告期 |
| basic_eps | float | 每股收益 |
| diluted_eps | float | 每股收益(稀释) |
| net_profit | float | 净利润 |
| net_profit_attr | float | 归属净利润 |

---

接口: query_balance_data

描述: 获取资产负债表数据

输入参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| code | str | 股票代码，如 "sh.600000" |
| year | int | 报告年份，如 2024 |
| quarter | int | 报告季度，1-4 |

输出参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| code | str | 股票代码 |
| report_date | str | 报告期 |
| total_assets | float | 资产总计 |
| total_liab | float | 负债合计 |
| total_hldr_eqy | float | 股东权益合计 |

---

接口: query_cash_flow_data

描述: 获取现金流量表数据

输入参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| code | str | 股票代码，如 "sh.600000" |
| year | int | 报告年份，如 2024 |
| quarter | int | 报告季度，1-4 |

输出参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| code | str | 股票代码 |
| report_date | str | 报告期 |
| net_cash_flows_oper_act | float | 经营活动产生的现金流量净额 |
| net_cash_flows_inv_act | float | 投资活动产生的现金流量净额 |
| net_cash_flows_fin_act | float | 筹资活动产生的现金流量净额 |

---

### 指数成分

接口: query_hs300_stocks

描述: 获取沪深 300 成分股

输入参数

无

输出参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| seq | int | 序号 |
| code | str | 股票代码 |
| code_name | str | 股票名称 |
| date | str | 日期 |

---

接口: query_sz50_stocks

描述: 获取上证 50 成分股

输入参数

无

输出参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| seq | int | 序号 |
| code | str | 股票代码 |
| code_name | str | 股票名称 |
| date | str | 日期 |

---

接口: query_zz500_stocks

描述: 获取中证 500 成分股

输入参数

无

输出参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| seq | int | 序号 |
| code | str | 股票代码 |
| code_name | str | 股票名称 |
| date | str | 日期 |

---

### 宏观数据

接口: query_deposit_rate_data

描述: 存款利率数据

输入参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| start_date | str | 开始日期，格式 yyyy-MM-dd |
| end_date | str | 结束日期，格式 yyyy-MM-dd |

输出参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| date | str | 日期 |
| deposit_rate_type | str | 存款类型 |
| rate | float | 利率 |

---

接口: query_loan_rate_data

描述: 贷款利率数据

输入参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| start_date | str | 开始日期，格式 yyyy-MM-dd |
| end_date | str | 结束日期，格式 yyyy-MM-dd |

输出参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| date | str | 日期 |
| loan_rate_type | str | 贷款类型 |
| rate | float | 利率 |

---

接口: query_money_supply_data_month

描述: 货币供应量月度数据

输入参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| start_date | str | 开始日期，格式 yyyy-MM |
| end_date | str | 结束日期，格式 yyyy-MM |

输出参数

| 名称 | 类型 | 描述 |
|-----|-----|-----|
| month | str | 月份 |
| m0 | float | 流通中货币(M0) |
| m0_yoy | float | 同比增长 |
| m1 | float | 狭义货币(M1) |
| m1_yoy | float | 同比增长 |
| m2 | float | 广义货币(M2) |
| m2_yoy | float | 同比增长 |
