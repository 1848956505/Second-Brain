# 安装的 Skills 汇总

> 自动维护：每次安装新 Skill 后更新并推送到仓库。
> 最后更新：2026-05-16（第二次更新）

---

## 1. x-tweet-fetcher

| 项目 | 内容 |
|------|------|
| **名称** | x-tweet-fetcher |
| **概述** | 无需登录或 API Key 即可抓取 X/Twitter 推文、回复、时间线、文章。支持中文平台（微博、B站、CSDN、微信公众号）和推文增长监控（X-Tracker）。零依赖即可抓取单条推文，高级功能可选配 Camofox 浏览器后端。 |
| **GitHub 地址** | https://github.com/ythx-101/x-tweet-fetcher |
| **安装位置** | `~/.openclaw/skills/x-tweet-fetcher/` |

### 使用方法

```bash
# 单条推文（零依赖）
python3 scripts/fetch_tweet.py --url "https://x.com/username/status/123456"

# 纯文本输出
python3 scripts/fetch_tweet.py --url "..." --text-only

# 用户时间线（需 Camofox）
python3 scripts/fetch_tweet.py --user username --limit 50

# 获取回复（需 Camofox）
python3 scripts/fetch_tweet.py --url "..." --replies

# 中文平台
python3 scripts/fetch_china.py --url "https://weibo.com/..."
python3 scripts/fetch_china.py --url "https://mp.weixin.qq.com/..."

# 推文增长监控
python3 scripts/tweet_growth_cli.py --run --fast
```

---

## 2. academic-deep-research-pro

| 项目 | 内容 |
|------|------|
| **名称** | Academic Deep Research（学术深度研究） |
| **概述** | 透明、严谨的多轮深度学术研究——非黑盒 API 封装。每个研究主题强制进行 2 轮调研循环，支持 APA 第 7 版引用格式和证据等级标注，含 3 个用户检查点。使用 OpenClaw 原生工具（web_search、web_fetch、sessions_spawn），适合文献综述、竞争情报等需要学术严谨性和可复现性的研究。 |
| **GitHub 地址** | https://github.com/kesslerio/academic-deep-research-clawhub-skill |
| **ClawHub 页面** | https://clawhub.ai/nancliu/academic-deep-research-pro |
| **安装位置** | `workspace/skills/academic-deep-research-pro/` |

### 使用方法

在对话中直接提出研究需求，Skill 会自动触发。例如：

> "帮我深度调研一下 Retrieval-Augmented Generation 的最新进展"
> "做一篇关于 LLM Agent 的文献综述"

Skill 会：
1. 先问 2~3 个澄清问题确认研究范围
2. 提交研究计划供确认
3. 执行 2 轮研究循环，使用多源验证
4. 生成附带 APA 7 引用的完整叙事报告

---

## 3. academic-writing-refiner

| 项目 | 内容 |
|------|------|
| **名称** | Academic Writing Refiner（学术论文润色） |
| **概述** | CS 顶会论文写作润色，专攻 NeurIPS、ICLR、ICML、AAAI、IJCAI、ACL、EMNLP、CVPR 等顶级会议。支持全文润色和分节精修，保留 LaTeX 格式（引用、公式、标签等）。核心原则：清晰 > 花哨，精确 > 模糊，简洁 > 冗长。支持 rebuttal 回复润色。 |
| **GitHub 地址** | https://github.com/Zihan-Zhu/academic-writing-refiner |
| **ClawHub 页面** | https://clawhub.ai/zihan-zhu/academic-writing-refiner |
| **安装位置** | `workspace/skills/academic-writing-refiner/` |

### 使用方法

在对话中粘贴论文内容或提出润色请求即可自动触发：

> "帮我润色这段 abstract，投 NeurIPS"
> "优化一下 introduction 部分，目标是 ICLR"
> "帮我精修这段 methodology 的实验描述"
> "帮我写 rebuttal 回复审稿人的意见"

支持的模式：
- **全文精修**：逐段优化
- **单节精修**：只优化指定段落
- **快速润色**：仅修语法拼写
- **迭代优化**：根据反馈反复调整
- **Rebuttal 撰写**：针对性回复审稿意见

输入 LaTeX 格式则输出 LaTeX，输入纯文本则输出纯文本。

---

## 4. tushare-finance

| 项目 | 内容 |
|------|------|
| **名称** | Tushare Finance（A股金融数据） |
| **概述** | 通过 Tushare Pro API 获取中国金融市场数据，支持 220+ 个数据接口。涵盖 A股/港股/美股/基金/期货/债券行情、财务报表、宏观经济指标（GDP/CPI）、分红送转、龙虎榜等。**做 A 股量化回测最全的数据源。** |
| **GitHub 地址** | https://github.com/LeoYeAI/openclaw-master-skills/tree/main/skills/tushare-finance |
| **ClawHub 页面** | https://clawhub.ai/tushare-finance |
| **安装位置** | `workspace/skills/tushare-finance/` |

### 使用方法

**前置准备：**
1. 访问 https://tushare.pro 注册并获取 Token
2. 配置环境变量：`export TUSHARE_TOKEN="your_token"`
3. 安装依赖：`pip install tushare pandas`

**常用接口：**

```python
import tushare as ts
pro = ts.pro_api()

# 股票列表
pro.stock_basic()

# 日线行情
df = pro.daily(ts_code='000001.SZ', start_date='20260101', end_date='20260516')

# 财务指标（ROE等）
pro.fina_indicator(ts_code='600519.SH')

# 指数行情
pro.index_daily(ts_code='000001.SH')

# 龙虎榜
pro.longhubang(trade_date='20260515')
```

---

## 5. ths-advanced-analysis

| 项目 | 内容 |
|------|------|
| **名称** | THS Advanced Analysis（同花顺高级分析） |
| **概述** | 基于 thsdk 进行高级股票分析：分钟K线（1m/5m/15m/30m/60m/120m）、板块/指数行情、多股票批量对比、盘口深度、大单流向、集合竞价异动、日内分时、问财 NLP 选股。**短线交易和盘中决策的最佳工具。** |
| **GitHub 地址** | https://github.com/LeoYeAI/openclaw-master-skills/tree/main/skills/ths-advanced-analysis |
| **ClawHub 页面** | https://clawhub.ai/ths-advanced-analysis |
| **安装位置** | `workspace/skills/ths-advanced-analysis/` |

### 使用方法

**前置准备：** `pip install thsdk`

**支持的分析类型：**

| 功能 | 说明 |
|------|------|
| 分钟K线 | 1m/5m/15m/30m/60m/120m + 均线 + 成交量异动标注 |
| 板块行情 | 行业排名 + 概念板块成分股 + 指数行情 |
| 多股对比 | 表格 + 归一化走势图 + 相关性热力图 |
| 大单流向 | 大单追踪 + 竞价异动扫描 + 盘口深度 |
| 问财选股 | NLP 自然语言选股（如"今日主力资金流入前10"） |
| 批量分析 | 同时查询多只股票，短线量化研究 |

**对话触发示例：**
> "帮我看看宁德时代的分钟K线"
> "查一下今天涨停的股票"
> "对比茅台和五粮液"
> "问财：今日主力资金流入的概念板块"

---

## 6. eastmoney-financial-data

| 项目 | 内容 |
|------|------|
| **名称** | Eastmoney Financial Data（东方财富金融数据） |
| **概述** | 东方财富金融/基金数据查询，支持股票/基金/债券/资金流向查询，**无需注册和Token。** |
| **GitHub 地址** | https://github.com/LeoYeAI/openclaw-master-skills/tree/main/skills/eastmoney-financial-data-1-0-2 |
| **ClawHub 页面** | https://clawhub.ai/eastmoney-financial-data-1-0-2 |
| **安装位置** | `workspace/skills/eastmoney-financial-data-1-0-2/` |

### 使用方法

无需额外配置，直接调用即可查询东方财富的金融数据。

> "查一下 600519 的行情"
> "看看今天北向资金流向"
> "查询半导体板块资金情况"
