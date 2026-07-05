# 矿权日报 Agent 面试讲解稿

## 1. 项目一句话介绍

这个项目是一个基于 MCP 协议的矿权日报 Agent。

用户输入一句自然语言请求，比如：

```bash
给我生成一份关于 Pilbara 锂矿的今日简报
```

Agent 会调用 3 个 MCP 工具服务，分别获取矿业新闻、矿权储量数据和价格走势，然后把这些结构化证据交给 DeepSeek 大模型，最终生成一份带引用链接的 Markdown 简报。

## 2. 为什么选择这个题

三道题里我选择了题目 #2：矿权日报 Agent。

原因是：

- 它和我学习的 Agent 方向最贴近。
- 交付边界比较清楚：3 个 MCP server + 1 个 Agent client。
- 比大规模爬虫和复杂 PDF 对抗抽取更容易在 24 小时内做出稳定可运行的工程项目。
- 更适合展示 Agent 编排、工具调用、MCP 协议和工程化交付能力。

## 3. 整体架构

项目主要分为 4 层：

```text
用户输入
  ↓
Agent Client
  ↓
调用 3 个 MCP Server
  ↓
组装 EvidenceBundle 证据包
  ↓
DeepSeek 大模型生成 Markdown 简报
```

3 个 MCP server 分别是：

- `mining-news-mcp`：矿业新闻搜索和文章获取。
- `mineral-pdf-mcp`：矿权报告 PDF / 储量数据抽取。
- `lme-price-mcp`：价格查询和趋势分析。

Agent client 的入口是：

```bash
python -m mineral_daily_agent.cli "Generate today's briefing for the Pilbara lithium project"
```

## 4. 为什么选择 Python

我选择 Python 是因为这个题涉及 Agent、数据处理、PDF 解析和工具编排，Python 生态更成熟。

主要原因：

- MCP Python SDK 可以快速实现 MCP server。
- `pdfplumber` 适合处理 PDF 文本和表格抽取。
- `pydantic` 适合定义结构化数据模型。
- Python 写 Agent 编排和测试比较高效。
- 面试题要求 24 小时交付，Python 更适合快速做出稳定版本。

## 5. 为什么没有使用 LangGraph

题目允许：

```text
LangGraph / 自写 ReAct / 你的方案
```

我选择的是“自写轻量 Agent 编排”，不是 LangGraph。

原因是这个任务的工具调用流程比较确定：

```text
查新闻 -> 查储量 -> 查价格 -> 汇总证据 -> 生成日报
```

这种流程不需要很复杂的图状态管理。使用 LangGraph 会增加依赖和复杂度，但对当前任务收益不大。

所以我采用了更稳定、可解释、容易调试的确定性编排方式。这样更符合“5 分钟内跑起来”的要求。

## 6. 为什么使用 MCP

题目明确要求 MCP。

MCP 的价值是把 Agent 和工具能力解耦：

- Agent 不直接写死所有数据处理逻辑。
- 每类能力独立成一个 MCP server。
- 后续替换真实数据源时，只需要改对应的 MCP server。
- Agent 主流程可以保持稳定。

比如以后要接真实新闻 API，只需要升级 `mining-news-mcp`；要接真实行情 API，只需要升级 `lme-price-mcp`。

## 7. 为什么使用 fixture-first 数据

项目默认使用内置 fixture 数据。

这是一个工程取舍，原因是题目要求 5 分钟内跑起来，而真实数据源存在很多不确定性：

- 新闻网站可能有反爬。
- 行情数据可能有登录墙或频控。
- PDF 格式差异很大，容易解析不稳定。
- 面试官现场网络环境不可控。

所以我采用 fixture-first：

- 默认 demo 稳定可复现。
- 不依赖外部矿业网站。
- 测试结果稳定。
- MCP 接口和 Agent 流程仍然是真实的。
- 后续可以平滑替换为真实数据源。

可以这样向面试官解释：

```text
我优先保证 5 分钟可运行，所以默认走 fixture-first。
真实抓取作为增强路径保留，但不让演示被外部网站网络、反爬和登录墙影响。
```

## 8. 为什么使用 DeepSeek

我选择 DeepSeek 是因为它提供 OpenAI-compatible API，接入成本低，而且我手头可以提供 key。

配置通过 `.env` 管理：

```env
DEEPSEEK_API_KEY=your_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_TRUST_ENV=false
```

这样做有几个好处：

- API key 不写进代码。
- API key 不上传 GitHub。
- 面试官可以换成自己的 key。
- 默认不读取系统代理，避免本地代理导致 DeepSeek 连接失败。

## 9. Docker Compose 如何满足题目要求

题目要求：

```text
RUN.md — 5 分钟内跑起来，含一条 docker-compose
```

项目提供了 Docker Compose 命令：

```bash
docker compose run --rm agent "Generate today's briefing for the Pilbara lithium project"
```

面试官运行步骤：

```bash
cp .env.example .env
# 填写 DEEPSEEK_API_KEY
docker compose run --rm agent "Generate today's briefing for the Pilbara lithium project"
```

如果 Docker 基础镜像拉取失败，`RUN.md` 里也写了排障说明，避免因为镜像源问题误判为项目错误。

## 10. 工程化设计

项目不是只写了一个脚本，而是按工程项目组织：

- `pyproject.toml`：项目依赖、命令入口、测试和 lint 配置。
- `Dockerfile`：容器构建。
- `docker-compose.yml`：一条命令运行 Agent。
- `.env.example`：环境变量模板。
- `.gitignore`：防止上传真实 key。
- `README.md`：项目说明。
- `RUN.md`：5 分钟运行指南。
- `mcp-config.json`：可接 Claude Desktop / Cursor 的 MCP 配置。
- `tests/`：自动化测试。
- `.github/workflows/ci.yml`：GitHub Actions CI。

## 11. 测试覆盖

测试主要覆盖 4 类：

- fixture schema 测试：确认样例数据结构正确。
- MCP tool 测试：确认工具函数可以返回数据。
- MCP stdio client 测试：确认真的能通过 MCP 协议调用 server。
- Agent flow 测试：确认 Agent 能组装证据并生成结果。

本地验证过：

```bash
pytest
ruff check .
```

都可以通过。

## 12. 本地运行方式

Python 方式：

```bash
python -m mineral_daily_agent.cli "Generate today's briefing for the Pilbara lithium project"
```

如果本机有多个 Python，可以指定解释器：

```powershell
E:\python\python3.10.4\python.exe -m mineral_daily_agent.cli "给我生成一份关于 Pilbara 锂矿的今日简报"
```

Docker 方式：

```bash
docker compose run --rm agent "Generate today's briefing for the Pilbara lithium project"
```

## 13. 可以向面试官这样总结

这个项目的重点不是只做一个能调用大模型的 demo，而是做一个可运行、可测试、可 Docker 交付的 MCP Agent 系统。

我把能力拆成 3 个 MCP server，分别负责新闻、储量和价格；Agent client 负责工具编排、证据汇总和调用 DeepSeek 生成 Markdown 简报。

在选型上，我没有引入过重的 LangGraph，而是用轻量确定性编排，因为当前任务流程固定，这样更稳定、更容易调试，也更符合 5 分钟运行要求。

数据层采用 fixture-first，是为了保证面试现场可复现，不被外部网站、反爬、登录墙和网络问题影响。后续如果要接真实数据源，只需要替换对应 MCP server，不需要重写 Agent 主流程。

整体上，这个方案重点体现的是：

- MCP 协议理解。
- Agent 工具编排能力。
- 工程化交付能力。
- Docker 可运行性。
- 测试和 CI 意识。
- 对不稳定外部数据源的风险控制。
