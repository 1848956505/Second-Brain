# 安装的 Skills 汇总

> 自动维护：每次安装新 Skill 后更新并推送到仓库。
> 最后更新：2026-05-16

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
