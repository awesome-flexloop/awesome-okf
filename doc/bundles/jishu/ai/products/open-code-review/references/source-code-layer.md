---
type: "Wiki Tutorial"
title: "源码层信源登记（commit 375f64cd）"
description: "Open Code Review 源码层知识包的信源登记页——固定不可变 commit 坐标、仓库拓扑、六个主题的覆盖矩阵与未读边界、证据等级与定位方法。"
tags: ["open-code-review", "source-code", "provenance", "ai-code-review"]
sources:
  - id: ocr-src-commit
    resource: "https://github.com/alibaba/open-code-review/tree/375f64cd6f67a48a135da83cfcf59c52669a09cb"
    title: "alibaba/open-code-review 源码快照 commit 375f64cd"
  - id: ocr-src-go-mod
    resource: "https://github.com/alibaba/open-code-review/blob/375f64cd6f67a48a135da83cfcf59c52669a09cb/go.mod"
    title: "go.mod（模块坐标与依赖）"
  - id: ocr-src-pkg
    resource: "https://github.com/alibaba/open-code-review/blob/375f64cd6f67a48a135da83cfcf59c52669a09cb/package.json"
    title: "package.json（npm 分发包定义）"
  - id: ocr-src-pages
    resource: "https://github.com/alibaba/open-code-review/tree/375f64cd6f67a48a135da83cfcf59c52669a09cb/pages/src/content/docs/zh"
    title: "官方文档站中文源文件（仓库内 pages/）"
generated: { by: process:seven-concepts, at: 2026-10-21 }
verified: { by: process:seven-concepts-v, at: 2026-10-21 }
---

# 源码层信源登记（commit 375f64cd）

> **本层定位**：[官方文档层](official-doc-facts.md) 记录的是 `open-codereview.ai` 站点上的**文档声明**；本页与[源码层事实清单](source-code-facts.md) 记录的是**同一产品的实现事实**。两层分列，不互相覆盖；出现分歧时，本层的口径优先级见 [源码层与文档层的四处口径差](source-code-facts.md#源码层与文档层的四处口径差)。
>
> **口径纪律**：本层事实全部来自静态源码阅读，**未运行 `ocr` 二进制、未调用任何 LLM、未发起任何网络请求**。凡涉及运行期行为的描述，一律以「代码中如此声明」为限，不作「实测如此」的断言。

## 1. 固定信源坐标

| 项 | 值 |
|----|-----|
| 仓库 | `alibaba/open-code-review` |
| 活动信源（不可变） | <https://github.com/alibaba/open-code-review/tree/375f64cd6f67a48a135da83cfcf59c52669a09cb> |
| commit | `375f64cd6f67a48a135da83cfcf59c52669a09cb` |
| 提交时间 | 2026-10-20T17:50:03+08:00 |
| 提交标题 | `fix(tool): report an empty code_comment batch instead of success (#1773)` |
| 与最近 tag 的关系 | `git describe` 输出 `v1.13.2-4-g375f64c`（tag `v1.13.2` 之后 4 个提交，HEAD 本身无 tag）——**本层记录的是该 tag 之后的状态**；涉及「发布版行为」的断言应以 `v1.13.2` 为坐标重新核对 |
| Go 模块名 | `github.com/alibaba/open-code-review` |
| Go 版本要求 | `go 1.26.9` |
| npm 包 | `@alibaba-group/open-code-review`，可执行名 `ocr`（`bin/ocr.js`） |
| npm `version` 字段 | `0.0.0`（占位值，真实版本由 `scripts/version.js` 在发布时注入） |
| 许可证 | Apache-2.0 |
| 仓库文件总数 | 1125 个受版本控制文件 |

> **本机 checkout 只是读取通道**：本轮在本机检出 `375f64cd` 读取源码，**未做任何 checkout 切换、未修改任何源码文件、未运行构建或测试**。对外引用一律使用上表的不可变 commit URL。

## 2. 仓库拓扑（`git ls-files` 按顶层目录归组）

| 顶层目录 | 文件数 | 内容 |
|---------|-------|------|
| `internal/` | 391 | 全部实现代码，按 19 个子包划分 |
| `pages/` | 210 | 官方文档站前端（Astro），其中 `pages/src/content/docs/zh/` 为**中文文档源文件** |
| `extensions/` | 160 | 桌面与 IDE 扩展（frontend / idea / vscode） |
| `acp/` | 117 | ACP（Agent Client Protocol）适配器，**独立 go.mod** |
| `cmd/` | 104 | CLI 入口 `cmd/opencodereview/` |
| `.github/` | 22 | 仓库治理文件与 CI 工作流（dependabot / release / SECURITY / workflows 等） |
| `scripts/` | 23 | npm 安装/更新脚本与 GitHub Actions 契约测试 |
| `plugins/` | 21 | 多宿主插件 `plugins/open-code-review/`（Claude Code / Codex / Cursor / Kimi / **OpenCode** / QCA 六个宿主目录） |
| `examples/` | 21 | 各 CI 平台集成示例 |
| 根部散文件 | 19 | `README.md`、`AGENTS.md`、`CLAUDE.md`、`ROADMAP.md`、`GOVERNANCE.md`、`ASSURANCE_CASE.md`、`CONTRIBUTING.md`、`CODE_OF_CONDUCT.md`、`Makefile`、`action.yml`、`install.sh`、`install.ps1`、`go.mod`、`go.sum`、`package.json`、`LICENSE`、`.gitignore`、`.gitattributes`、`.npmignore` |
| `imgs/` | 13 | README 配图 |
| `docs/` | 8 | 贡献指南与 README 的 4 语言 i18n 版本（zh-CN / ja-JP / ko-KR / ru-RU，各 2 篇） |
| `npm/` | 6 | 六平台（darwin/linux/win32 × arm64/x64）分发包定义 |
| `bin/`、`skills/` | 各 2 | `bin/ocr.js` 启动脚本；`skills/` 两个 Agent Skill 定义（`open-code-review`、`open-code-review-delegate`） |
| `.claude/` | 2 | 仓库自身的 Claude Code 命令（commit / tag） |
| `.agents/`、`.claude-plugin/`、`.kimi-plugin/`、`.opencodereview/` | 各 1 | 插件市场清单与 OCR 默认规则 |

### `internal/` 包子包分布

| 子包 | 文件数 | 职责 |
|------|-------|------|
| `internal/agent` | 24 | 评审编排：文件选择、语义分组、plan/main 循环、预览 |
| `internal/llm` | 56 | LLM 客户端、provider 注册表、协议分发、重试与报告 |
| `internal/llmloop` | 18 | 通用 LLM 循环、记忆压缩、并发池 |
| `internal/config` | 97 | 模板、规则、工具 schema、扩展名白名单、连通性测试 |
| `internal/viewer` | 39 | 会话查看器 HTTP 服务与存储 |
| `internal/session` | 29 | 会话持久化与 run manifest |
| `internal/tool` | 23 | 六个内置工具的实现与参数修复 |
| `internal/scan` | 22 | `ocr scan` 全量扫描路径 |
| `internal/telemetry` | 15 | OpenTelemetry 埋点 |
| `internal/diff` | 22 | diff 获取、解析、hunk 切分、行号解析与重定位 |
| `internal/chatgptauth` | 16 | ChatGPT OAuth（PKCE）与凭据存储 |
| `internal/mcp` | 9 | MCP 客户端接入 |
| `internal/delegate` | 5 | 委托模式的分组与格式化 |
| `internal/gitcmd` | 4 | git 子进程执行器 |
| `internal/model` | 5 | 数据模型与 preview 条目 |
| `internal/release` | 1 | 版本信息 |
| `internal/pathutil` | 2 | 路径工具 |
| `internal/stdout` | 2 | stdout 捕获 |
| `internal/suggestdiff` | 2 | 建议差异 |

## 3. 官方文档站源文件在仓库内

`pages/src/content/docs/zh/` 收录 **18 篇中文文档源文件**：

`architecture.md`、`chatgpt-preview.md`、`cli-reference.md`、`configuration.md`、`contributing.md`、`faq.md`、`installation.md`、`integrations/acp.md`、`integrations/agent-skill.md`、`integrations/ci.md`、`integrations/claude-code.md`、`integrations/delegate.md`、`mcp.md`、`quickstart.md`、`review-rules.md`、`telemetry.md`、`tools.md`、`viewer.md`

**这一事实改变了本层的可验证性**：文档站页面与被描述的实现处在同一个版本控制历史内，文档陈述与代码常量可以按同一 commit 对照。除 `zh` 外另有 `en`、`ja`、`ko`、`ru` 四个语言目录。

> **依赖声明**：此性质依赖「文档站源码与实现同仓管理」。上游若把文档站拆分为独立仓库或独立发布流水线，本层的同 commit 对照方法需改为跨版本比对，届时口径差表需重新生成。

> 与[官方文档层勘误表](official-doc-corrections.md) E-06 相关的旧结论需要限定：该条记录的是「仓库根目录没有 `docs/` 目录」这一观察，而文档站源文件实际位于 `pages/src/content/docs/`，两者路径不同。

## 4. 六主题覆盖矩阵

| 主题 | 主要读取文件（相对仓库根） | 读取深度 |
|------|--------------------------|---------|
| **A 差异获取链** | `internal/diff/git.go`、`parser.go`、`hunk.go`、`resolver.go`、`quotedpath.go`、`gitignore.go`、`internal/gitcmd/runner.go` | 关键函数全文 + 常量逐条复核 |
| **B 文件选择与过滤** | `internal/agent/selection.go`、`internal/config/allowlist/allowed_ext.go`、`secret_path.go`、`internal/config/rules/system_rules.go` | 关键函数全文 + 内嵌 JSON 逐条计数 |
| **C 分组调度与主循环** | `internal/agent/grouping.go`、`estimate.go`、`agent.go`、`internal/llmloop/loop.go`、`compression.go`、`internal/config/template/` | 分组链全文 + 主循环片段 + 模板常量逐条复核 |
| **D LLM 客户端与 Provider** | `internal/llm/providers.go`、`protocol.go`、`client.go`、`resolver.go`、`retry_report.go`、`embedded_loader.go`、`chatgpt.go`、`internal/chatgptauth/` | provider 注册表逐条清点 + 客户端片段 |
| **E 工具与输出契约** | `internal/tool/`、`internal/config/toolsconfig/tools.json`、`cmd/opencodereview/output.go`、`sarif.go`、`main.go`、`internal/session/manifest.go`、`internal/delegate/` | schema 与输出结构逐字段核对 |
| **F 扩展与集成** | `internal/mcp/`、`internal/viewer/`、`internal/telemetry/`、`internal/scan/`、`acp/`、`plugins/`、`skills/`、`examples/` | 关键常量与清单核对（ACP 仅读 README 与 go.mod） |

### 证据等级约定

本层的每条事实按以下四级标注，引用时随事实一同理解：

| 等级 | 含义 | 本层适用范围 |
|------|------|------------|
| **L1 直接读值** | 本轮逐字读过源码行并取到字面值（常量、字符串、签名） | 全部过滤门顺序、原因码字面量、provider 清单、阈值常量、工具清单、模板 JSON |
| **L2 片段读值** | 读过相关函数片段并确认行为，未通读全文件 | 客户端超时与重试、输出 JSON 结构、viewer 路由、遥测指标名 |
| **L3 声明转述** | 仅读到注释或文档字符串，未读到执行路径 | `acp/` 内部实现（仅读 README 与 go.mod） |
| **L4 未覆盖** | 本轮未读 | 见下节 |

## 5. 未读边界

**以下内容本轮未读，任何相关结论都不在本层的事实清单内**：

- `internal/llm/` 的 `keycmd*.go`、`api_error.go`、`browser_*.go`、`lock_*.go`、`gen/`（provider 常量前端代码生成器）
- `internal/llm/client.go` 的 L652–L1795 区段（流式响应解码的逐行实现）
- `internal/agent/agent.go` 的 L284–L443、L629–L856、L1189–L1241、L1379–L1559 区段
- `internal/llmloop/loop.go` 的 L95–L280、L660–L880 区段
- `internal/scan/agent.go` 除 token 阈值与并发相关的片段
- `internal/mcp/` 除 `client.go`、`provider.go` 外的文件
- `internal/viewer/handler.go`、`store.go`
- `acp/internal/` 的全部 Go 源码（本层仅读 `acp/go.mod` 与 `acp/README.md`）
- `extensions/frontend|idea|vscode` 的实现源码（本层仅读 `package.json` / `plugin.xml` 的清单字段）
- `examples/` 中 `codeup`、`bitbucket`、`gitflic` 三个示例的完整文件
- 全部 `*_test.go` 文件（测试用例可作为行为的第二证据源，本轮未系统读取）
- `pages/src/content/docs/` 除 `zh/` 外的四个语言目录

## 6. 定位方法与复核纪律

- **行号锚点格式**：正文中的 `文件:起-止` 均指**仓库根起算的 1-based 行号**，指向该 commit 下的文件内容。
- **锚点有效期**：行号锚点**仅在 commit `375f64cd` 下有效**。跨版本引用时必须先重新定位行号，**不得直接沿用旧行号**；commit 坐标保证可回溯，行号不保证。
- **机械复核**：本层全部行段锚点经脚本核验——文件存在、行段不越界（EOF 检查）、引用的字面值在锚定行段内命中。三项任一不成立即回退修正。
- **计数口径**：provider 数、工具数、扩展名白名单条目数、默认排除模式条目数、排除原因码数，均由脚本对源码清单逐项计数得出，不采用文档或注释中的数字。
- **口径漂移防护**：本层与[官方文档层](official-doc-facts.md) 引用同一套 F 编号空间——文档层占 F-001~F-100，源码层从 F-101 起续编，分歧点在事实清单内以「口径差」小节显式列出，不在两页之间静默改写。
