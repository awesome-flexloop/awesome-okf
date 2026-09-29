---
type: bundle
title: ScholarClaw 学术搜索 Agent 服务
okf_version: "0.2"
---

# ScholarClaw 知识库

本知识包是网易有道开源的学术搜索 Agent 服务 [ScholarClaw](https://github.com/netease-youdao/ScholarClaw)（MIT 许可证）的系统化中文源码教程，基于 ScholarClaw 源码（`vendor/netease-youdao/ScholarClaw/` 目录，版本 1.4.1，基线 commit `97bdb5e4a763d4f98d4603f5be876587c0871e0f`）深度阅读生成。ScholarClaw 本身不实现任何搜索逻辑——它是远端 SaaS（`https://scholarclaw.youdao.com`）的纯客户端协议适配层：服务端提供 TypeScript 客户端（`ScholarClawClient`，9 组 20 个方法）与 shell 脚本工具链（16 个 `.sh` = 1 公共库 + 15 功能脚本）双层调用面，`SKILL.md` 以 Markdown 形式定义面向 LLM 的运行时契约（触发条件、SSE 事件过滤、博客异步三步法、重试退避）。全部内容经 R→I→E→V→C 五阶段链路生成，溯源至 vendor 源码。

## 概念篇（concepts/）

* [ScholarClaw 项目概览与定位](concepts/00-overview.md) — 零依赖 skill 包的定位：远端 SaaS 的薄客户端、TS 客户端 + Shell 脚本双层调用面、配置体系（5 字段接口、五级合并链、校验规则）、安装方式与运行时依赖。
* [TypeScript 客户端与 HTTP 路由](concepts/01-server-client.md) — `ScholarClawClient` 的 9 组 20 个方法、统一 `request()` 通道与 `submitBlog()` 表单编码例外、类型体系（分页/搜索/学术/引用/OpenAlex/博客/基准/推荐八族）、错误判定。
* [Shell 脚本工具链与命令体系](concepts/02-shell-toolchain.md) — `common.sh` 公共库统一调用模式与取值优先级、15 个功能脚本清单、URL 编码与超时常量差异、install/package 安装打包体系与 npm 别名桥接。
* [SKILL.md 技能契约与调用时序](concepts/03-skill-contract.md) — 面向 LLM 的五重契约：触发条件、响应时间期望、SSE 事件过滤（仅 `final_response`/`response_chunk`）、博客异步三步法（10–15s×40 轮）、503/504 指数退避重试，及契约层与实现层常量的差异。
* [源码不一致与防御性兼容模式](concepts/04-evolution-inconsistency.md) — 引擎清单、博客状态枚举、命令清单三处源码间不一致的登记与解读：实现层是类型层的超集，集成时应以运行时行为为准、禁止精确等值比较。

## 实战示例（examples/）

* [博客生成三步法调用时序](examples/blog-three-step-pipeline.md) — 基于 `blog_submit.sh`/`blog_status.sh`/`blog_result.sh` 与 `blog.sh` 同步封装，演练「提交→轮询→取结果」完整时序及契约层与实现层的节奏差异。
* [一次学术搜索的完整调用](examples/scholar-search-walkthrough.md) — 基于 `scholar.sh` 真实脚本与官方示例，演练查询分析（`--analyze-only`）、带参数搜索、上下文追问的完整流程及响应结构解读。

## 信源登记簿（references/）

* [ScholarClaw 源码事实清单](references/facts.md) — R 阶段 64 条事实（F-sc-001~F-sc-064），覆盖配置常量、HTTP 路由、类型体系、shell 脚本、SKILL.md 契约与三处存疑不一致，逐条附 vendor 源码证据。
* [ScholarClaw 架构洞察](references/insights.md) — I 阶段 4 条洞察：TS+Shell 双调用面薄壳、SKILL.md 作为 LLM 契约的时序容错参数、curl+jq 零依赖极简主义、源码不一致的"快速演进+防御性兼容"信号。
* [ScholarClaw 信源登记](references/sources.md) — 上游仓库、固定基线 commit（实测核验）、MIT 许可证、版本 1.4.1 与关键信源文件清单（`SKILL.md`/`server/*`/`scripts/*`）的事实支撑映射。

## 信任与生命周期说明

* **文档总数构成**：本知识包共 7 个内容文档——5 个概念（concepts/）+ 2 个示例（examples/），另含 3 个子目录 index.md、3 个信源登记文档（references/ 下 facts/insights/sources）与根 index.md、log.md。
* **status 判定依据**：全部 7 个内容文档均 `status: stable`，内容基于对 ScholarClaw 源码（`server/` 配置与路由、`scripts/` 16 个 shell 脚本、`SKILL.md` 契约文档）的逐文件阅读与事实提取（64 条源码事实 F-sc-001~F-sc-064），经 R→I→E→V→C 五阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-09-09`。ScholarClaw 作为远端 SaaS 的薄客户端，其本地形态（双层调用面、SKILL.md 契约、安装别名体系）随服务端演进可能漂移，尤其 `config.ts` 常量表、SKILL.md 时序参数、`package.json` 的 lobsterai 元数据三处易漂移面；该日期作为针对服务端 API 演进的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-09-09）；`verified.at` 记录 V 阶段 facts 交叉验证事件，两者分离、可追溯。基线 commit 经 `git rev-parse HEAD` 在 vendor 子模块内实测核验。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
