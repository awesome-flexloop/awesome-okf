---
okf_version: "0.2"
type: bundle
title: "wigolo：AI Agent 的本地 Web 情报层"
description: "本地优先的 MCP 搜索/抓取/研究工具——18 公共引擎适配器、十工具、核心功能零 API Key、字节级证据与本地缓存，含安装接线、CLI、REST/Docker/LLM 可照做实操（源自微信博文经官方核验）"
tags: [wigolo, mcp, mcp-server, ai-agent, local-first, web-search, web-crawler, claude-code, cursor, 博文转化]
generated:
  by: seven-concepts-cmd+blog-article-to-okf-wiki
  at: "2026-09-16T21:25:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-09-16T21:25:00+08:00"
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/IXBNcf2zJI6Bja7gVGOy9w
  - id: github-repo
    url: https://github.com/KnockOutEZ/wigolo
  - id: github-api
    url: https://api.github.com/repos/KnockOutEZ/wigolo
  - id: official-readme
    url: https://raw.githubusercontent.com/KnockOutEZ/wigolo/main/README.md
  - id: official-installation
    url: https://raw.githubusercontent.com/KnockOutEZ/wigolo/main/docs/installation.md
  - id: official-cli
    url: https://raw.githubusercontent.com/KnockOutEZ/wigolo/main/docs/cli.md
---

# wigolo：AI Agent 的本地 Web 情报层

> **类型**：技术教程/选型（含可照做 examples/，操作可复现性两问皆"是"）
> **信源**：微信公众号「GHub开源甄选」博文（2026-09-15，作者小涛）→ 2026-09-16 经 GitHub API 与官方 README/docs 逐项核验
> **核验结论**：18 项 P0/P1 声明 **14✅ / 4⚠️ / 0❌**，全部安装命令逐字一致，无核心声明失败
> **数据时点**：Star 等动态数字为 2026-09-16 快照；功能口径为 main 分支 Public Beta 阶段

## 本文概要

[wigolo](https://github.com/KnockOutEZ/wigolo) 是一个 TypeScript 编写、AGPL-3.0 许可、2026-04 开源的本地优先 Web 情报层：AI 编程 Agent（Claude Code、Cursor、Codex 等 9 类客户端）经 MCP 调用它完成联网搜索、页面抓取、整站爬取、结构化提取、本地缓存、相似查找、深度研究与自动采集。搜索走 **18 个公共搜索引擎的直接适配器**，重排序与嵌入模型在本机运行——**6 个核心工具零 API Key、$0/query**；所有数据落在 `~/.wigolo/`，重复查询命中本地缓存、离线可查。

## 阅读路径

**先建立概念（10 分钟）**

1. [wigolo 是什么：项目身份与发布事实](concepts/00-what-is-wigolo.md)——定位、作者、许可证、热度（带时点）
2. [十工具矩阵与证据模型](concepts/01-ten-tools-and-evidence-model.md)——工具划分、6 免 Key+3 需 LLM、字节级来源定位与可解释评分
3. [本地优先架构与四种部署形态](concepts/02-local-first-architecture.md)——数据边界、MCP/REST/Docker/SDK、fail-closed

**再动手实操**

4. [安装并接入 AI 编程 Agent](examples/00-install-and-agent-wiring.md)——两条命令完成 init + doctor
5. [CLI 搜索、并行扇出与缓存](examples/01-cli-search-and-cache.md)——域名锁定、深度搜索、缓存即私有知识库
6. [REST API、Docker 与 LLM 配置](examples/02-rest-docker-and-llm.md)——自托管与 research 成稿

## 核心事实速查

| 项 | 值 |
|----|-----|
| 仓库 / 作者 | [KnockOutEZ/wigolo](https://github.com/KnockOutEZ/wigolo)（个人开发者，X @yourtowhid） |
| 开源时间 / 许可 | 2026-04-12 / AGPL-3.0 / TypeScript / Public Beta |
| 社区数据 | Star 5,268、Fork 419（**2026-09-16 时点**，博文 9-15 口径为"三千多"） |
| 运行要求 | Node.js ≥ 20，约 1.5GB 磁盘（引擎+模型），macOS/Linux/Windows |
| 工具数 | 10（search/fetch/crawl/extract/cache/find_similar/research/agent/diff/watch） |
| 免 Key 范围 | 6 个核心工具；research、agent、search format=answer 的**合成**可选配 LLM |
| 默认端口 | REST `127.0.0.1:3333`（`POST /v1/{tool}`，OpenAPI 3.1，同端口 /mcp /sse） |
| Docker | `ghcr.io/knockoutez/wigolo`（slim，首用下载至 /data 卷） |
| 数据位置 | `~/.wigolo/`（默认无数据外传） |

## ⚠️ 阅读前必知的四条口径勘误

1. **Star 数**：博文"三千多颗"为发文时口径，本知识包采用官方现值 **5,268（2026-09-16）**，动态数字引用须带时点。
2. **"对比测试"性质**：博文所述四工具对比出自项目官方 README 的**自述演示**（单会话 Claude Fable 5，口径 2026-07），非第三方独立评测；详见 [concepts/01 §5](concepts/01-ten-tools-and-evidence-model.md)。
3. **CLI 参数名**：博文 npx 示例的 `--limit` 在官方 headless 签名中为 `--max-results`（`--limit` 是 `wigolo shell` 内别名）；脚本请用 [examples/01](examples/01-cli-search-and-cache.md) 的官方写法。
4. **`:full` 标签**：官方文档确认 full 是 Dockerfile 构建目标（`docker build --target full`），未确认 ghcr 已发布 `:full` 预构建标签；"GitHub Trending 挂榜"的官方证据为第三方 Trendshift（#79424），非 GitHub 官方 Trending。

## 采用提示与已知边界

- **AGPL-3.0 许可证**：个人/内部调用无负担；修改源码后以 SaaS 对外提供服务会触发 AGPL 网络开源义务，商业内嵌前建议法务确认（详见 [concepts/02 §5](concepts/02-local-first-architecture.md)）。
- **单人维护的 Beta 项目**：owner 为个人开发者、状态 Public Beta，CLI 参数与镜像标签在快速迭代（本次已观测到博文与官方文档参数口径差异），生产依赖前建议锁定版本并关注 GitHub 变更。
- **数字时效**：Star/功能集为 2026-09-16 核验时点快照，`stale_after: 2026-12-31`，到期前复核。
- **Benchmark 性质**：四工具对比为官方自述演示，非独立评测（见上条勘误 2）。

## 信源与可信度

- 事实清单与逐条核验状态：[references/article-source.md](references/article-source.md)（F-001~F-055）
- P0 核验报告与勘误四张清单：[references/verification.md](references/verification.md)
- 信源距离：第三方开源推介号 → 已升级为官方一手文档交叉核验；Benchmark 段已标注厂商自述性质

## 主题关联

- [todesk-ai](../todesk-ai/index.md)：跨设备 AI 助手的 Computer Use 工具化实践（Agent 工具生态相邻话题）
- [browseract](../browseract/index.md)：浏览器自动化 Agent（wigolo 专注"只读型 Web 情报"，BrowserAct 专注"操作型浏览器自动化"，互补）
- [open-code-review](../open-code-review/index.md)：同样以 MCP 工具形态接入 Claude Code/CI 的开发者工具
- [context-optimization](../context-optimization/index.md)：本地缓存降低重复检索成本，与上下文 Token 优化同属 Agent 成本治理主题

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
