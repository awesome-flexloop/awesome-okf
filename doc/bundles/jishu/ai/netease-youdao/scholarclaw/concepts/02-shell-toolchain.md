---
type: concept
title: Shell 脚本工具链与命令体系
description: "`common.sh` 公共库的调用模式与取值优先级、15 个功能脚本清单、URL 编码与超时常量差异、install/package 安装打包体系与 npm 别名桥接。"
tags: [scholarclaw, shell, curl, toolchain, install]
generated: { by: "reference_agent/trae-cn", at: 2026-09-09T10:00:00+08:00 }
verified: { by: "process:facts-cross-check", at: 2026-09-09T10:00:00+08:00 }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: ScholarClaw 源码事实清单
  - id: insights
    resource: /references/insights.md
    title: ScholarClaw 架构洞察
---

# Shell 脚本工具链与命令体系

Shell 脚本是 ScholarClaw 的**主交付物**：`install.sh` 把脚本安装为 `sc-*` 系统别名，SKILL.md 教 LLM 调用的也是这套命令（F-sc-042）。`scripts/` 目录下共 16 个 `.sh` 文件——1 个公共库 `common.sh` + 15 个功能脚本；仓库根目录另有 `package.sh`、`install.sh` 两个脚本（F-sc-029）。

## 公共库 common.sh：全部脚本的统一调用模式

`common.sh` 统一了所有脚本的调用约定（F-sc-030）：

- **配置初始化**：`init_config`；`get_api_key`/`get_server_url` 的取值优先级为**环境变量 > 配置文件 > 默认值**。
- **curl 统一模式**：`-s -w "\n%{http_code}"`——响应体与 HTTP 状态码一并捕获，脚本随后分离两者并据此分支。
- **错误处理**：`handle_http_error` 集中处理非 200 响应。
- **输出美化**：检测到 `jq` 时用 `jq .` 美化输出；**无 jq 时输出原始紧凑 JSON**——下游做脚本化解析时不能假设格式稳定（F-sc-051）。

## 15 个功能脚本清单

| 脚本 | 路由 | 要点 |
|------|------|------|
| `search.sh` | `/search` | 通用搜索；自实现 URL 编码函数；参数含 query、engine、limit、page、mode、sort 等（F-sc-031） |
| `scholar.sh` | `POST /scholar/search`（默认）/ `POST /scholar/analyze`（`--analyze-only`） | 学术搜索；curl `--max-time 60`（F-sc-032） |
| `citations.sh` | `/citations` | 引用列表，支持分页与排序参数（F-sc-033） |
| `citations_stats.sh` | `/citations/stats` | 引用统计（F-sc-033） |
| `openalex_cited.sh` | `/openalex/cited_by` | 使用 `jq -sRr @uri` 做 URL 编码（F-sc-034） |
| `openalex_find.sh` | `/openalex/find_and_cited_by` | 同样使用 `jq -sRr @uri` 编码（F-sc-034） |
| `blog_submit.sh` | `POST /api/blog/submit` | multipart 表单（curl `-F` 参数）提交，输出任务 ID 等字段（F-sc-035） |
| `blog_status.sh` | `GET /api/blog/task/{id}` | 任务状态查询（F-sc-036） |
| `blog_result.sh` | `GET /api/blog/result/{id}` | 结果内容获取（F-sc-036） |
| `blog.sh` | 以上三者的串行封装 | 「提交→轮询→取结果」同步流程；`POLL_INTERVAL=5` 秒、默认总超时 `DEFAULT_TIMEOUT=600` 秒；状态分支含 `completed|success`、`failed|error`、`pending|running|processing|queued` 三组并集匹配（F-sc-037） |
| `benchmark_chat.sh` | 基准对话 | 默认超时 `DEFAULT_TIMEOUT=120`；`-s` 切换 SSE 模式（curl `-N` 加 `Accept: text/event-stream` 头）；history 参数默认 `[]`（F-sc-038） |
| `recommend_papers.sh` | `/api/recommend/papers` | 论文推荐（F-sc-039） |
| `recommend_blogs.sh` | `/api/recommend/blogs` | 博客推荐（F-sc-039） |
| `paper_repos.sh` | `/api/recommend/paper/{id}/detail` | 论文关联代码仓库（F-sc-039） |
| `health.sh` | `/health`（默认）/ `/search/health`（`-v` 追加） | curl `--max-time 10`（F-sc-040） |

## 两套调用面细节各自为政

实现层没有强制统一约定，集成时需注意三处差异：

1. **URL 编码**：`search.sh` 用自实现编码函数；`openalex_cited.sh`/`openalex_find.sh` 改用 `jq -sRr @uri`（F-sc-031、F-sc-034）。提交含特殊字符的查询时，绕过封装直接 curl 应参照后者的方案。
2. **博客表单编码**：TS 侧 `submitBlog()` 用 `URLSearchParams`（F-sc-015），shell 侧 `blog_submit.sh` 用 curl `-F` multipart（F-sc-035）。
3. **超时常量**：scholar 搜索 60s（F-sc-032）、博客轮询最长 600s（F-sc-037）、基准对话 120s（F-sc-038）、健康检查 10s（F-sc-040）——CI 中需按脚本内常量显式放宽步骤超时。

## 安装与打包

- **install.sh**：安装至 `~/.scholarclaw` 目录，生成 `scholarclaw.env`，写入 `aliases.sh` 的 `sc-*` 命令别名，并分发 `scholarclaw` 快速启动脚本（F-sc-042）。
- **package.sh**：构建 `dist/` 目录内容并生成 tar.gz、zip 归档及对应 sha256 校验文件（F-sc-041）。

## npm 别名桥接

`package.json` 定义 14 个 npm scripts 别名，对应各 shell 脚本功能（F-sc-058）；`lobsterai` 元数据块含 skillType=`api`、requiresAuth=`false`、14 个 supportedCommands、defaultServerUrl 及环境变量声明（F-sc-059），把 shell 层桥接进宿主工具的命令生态。

判断某个功能"是否存在"时，**shell 脚本集是更全的清单**：`blog.sh` 同步封装与 `health.sh` 简易模式均不在 supportedCommands 中，但 `sc-blog` 别名却指向 `blog.sh`（F-sc-064，详见 [/concepts/04-evolution-inconsistency.md](/concepts/04-evolution-inconsistency.md)）。

## 故障排查顺序

1. 先用 `sc-health`（10s 超时，`-v` 追加详细检查）区分网络/服务端问题（F-sc-040）；
2. 再查 apiKey 配置——401/403/429 判定为认证类错误（F-sc-020，见 [/concepts/01-server-client.md](/concepts/01-server-client.md)）；
3. 自动化流水线消费输出时，显式检查 `jq` 是否存在并统一用 `jq -c` 归一化，不要直接 diff 原始输出。

## 相关概念

- [/concepts/00-overview.md](/concepts/00-overview.md)
- [/concepts/01-server-client.md](/concepts/01-server-client.md)
- [/concepts/03-skill-contract.md](/concepts/03-skill-contract.md)
- [/concepts/04-evolution-inconsistency.md](/concepts/04-evolution-inconsistency.md)
