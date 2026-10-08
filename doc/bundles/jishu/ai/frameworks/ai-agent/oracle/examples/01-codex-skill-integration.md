---
okf_version: "0.2"
type: Example
title: "把 Oracle 接进 Codex：skill 安装、AGENTS.md 接线与协作工作流"
description: "复制官方 Codex skill、AGENTS.md 30 秒接线、三类官方协作模式、MCP 备选接入、安全卫生与多 Agent 并发注意"
tags: [Oracle, Codex, AGENTS.md, Skill, MCP, 工作流, 实战]
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/_J1BzyqyoNWuj_998DLo1g
  - id: docs-agents
    url: https://raw.githubusercontent.com/steipete/oracle/main/docs/agents.md
  - id: docs-browser
    url: https://raw.githubusercontent.com/steipete/oracle/main/docs/browser-mode.md
---

# 把 Oracle 接进 Codex

> **可复现性声明**：本篇依据官方 `docs/agents.md`（2026-09-16 main 分支）整理，博文命令经逐项核验一致（F-016/F-017）；博文作者未声明一手实测。目录名 `~/.codex/skills` 等随 Codex 版本可能调整，以官方文档为准。

## 1. 安装 Codex skill（博文方式，与官方一致）

```bash
git clone https://github.com/steipete/oracle.git
mkdir -p ~/.codex/skills
cp -R oracle/skills/oracle ~/.codex/skills/oracle
```

这是博文给出的三行（F-016），官方「Codex」节原文同样是这三行：Codex 启动时会自动加载该目录下的 `SKILL.md`，在调试、重构、设计评审等触发条件命中时调用 Oracle。

> 前提：`oracle` 可执行文件已在 PATH（见 [实战 00](00-install-and-browser-login.md)），且 Browser Mode 首次登录已完成。

可选增强：官方还支持在 `~/.codex/prompts/oracle.md` 放一个 slash prompt 包装器，固化你偏好的引擎/模型/follow-up 默认值（F-034）。

## 2. AGENTS.md 接线：30 秒配置

博文要求"在项目的 AGENTS.md 里告诉 Codex：复杂任务、架构分析、疑难问题优先通过 Oracle 调用网页端 ChatGPT，拿到方案后再继续执行"（F-017）。官方推荐的最小配置（"30-second wiring"，同时适用 `AGENTS.md`/`CLAUDE.md`，F-034）：

```markdown
- Oracle bundles a prompt plus the right files so a Pro model (GPT-5.5 Pro,
  Gemini 3 Pro, Claude Opus) can answer with real repo context. Use when stuck,
  debugging hard bugs, doing architecture review, or cross-validating a plan.
- Run `npx -y @steipete/oracle --help` once per session before first use.
```

中文项目可按同样语义书写，关键是写清**触发场景**（卡住、难 bug、架构评审、方案交叉验证）与**一次性自检**（每会话先跑 `--help`，防止 CLI 升级后参数漂移）。

接好后的闭环即博文所总结（F-018）：

```
Codex 找上下文 → Oracle 送给 GPT → GPT 思考 → Codex 验证并执行
```

注意闭环里隐含的官方纪律：Oracle 的回答是 **advisory（建议）**，Codex 必须对照真实代码与测试验证后再落地，不能把第二意见当补丁直接合并。

## 3. 三类官方协作模式

| 模式 | 时机 | 做法 |
|------|------|------|
| Stuck → Oracle | 同一个 bug 上转了 3 轮以上 | 把失败测试 + 涉及文件交给 Pro 模型一轮定症 |
| Plan → Oracle → execute | 方案/架构设计成型 | 先让外部模型挑战方案（可用 --browser-follow-up 连续追问"推翻你上一个建议"），再实现 |
| Refactor → cross-check | 非平凡重构完成 | diff + 规格发给**另一家**模型复核（API 模式可切 Anthropic/Gemini 等），快速发现漂移 |

一次跨模型评审的命令形态（API 模式示例，F-027）：

```bash
oracle --engine api --model claude-opus \
  -p "审查这个重构 diff 是否偏离规格" \
  --file docs/spec.md --file src/changed/
```

## 4. 备选：以 MCP server 方式接入（博文未提）

Oracle 同时提供 `oracle-mcp` stdio server，MCP 感知的客户端（Claude Code、Cursor、Codex）都可挂（F-035）：

- Claude Code 一条命令生成本地浏览器路径的 `.mcp.json`：

  ```bash
  oracle bridge claude-config --local-browser > .mcp.json
  ```

  之后可直接调 `oracle.consult` / `oracle.sessions` 工具，无需 API key；consult 支持 `preset: "chatgpt-pro-heavy"` 与 `dryRun: true`
- Cursor：写 `.cursor/mcp.json`，command 为 `oracle-mcp`（或用官方一键安装链接）
- Codex：除 skill 方式外也可按其 MCP 配置挂同一 stdio server

## 5. 安全卫生清单

官方在 agents.md 专列的 Cost / safety hygiene（F-038），团队接入时建议制度化：

- [ ] **默认不附 secrets**：`.env`、密钥、token 用 `--file "!..."` 排除；附件清单先看 `--dry-run --files-report`
- [ ] **Pro/API 调用先预演**：`--dry-run summary --files-report` 看 token 量（token 是费用的近似代理）
- [ ] **API 模式真实计费**：自动化场景 pin `--model`、设 `--browser-timeout`/`--timeout`、定期审计 `~/.oracle/sessions/`；很多团队把 API 模式放在显式人工同意之后，browser 模式放开
- [ ] **文件大小**：单文件默认 1 MB 上限（`maxFileSizeBytes` / `ORACLE_MAX_FILE_SIZE_BYTES`）
- [ ] **网页投递的合规性**：Browser 模式会把代码内容送进 ChatGPT 网页会话，私有仓库先确认公司政策
- [ ] **结果需验证**：模型只看到被打包的文件，建议必须带"对照代码与测试验证"的收尾步骤

## 6. 多个 Agent 共用一台浏览器

当 Codex、Claude Code 等多个调用方共享同一个 manual-login profile 时（F-037）：

- Oracle 自动串行化 profile 上的 Chrome 启动，并给 ChatGPT 标签位设软上限：**默认 3 个并发标签，第 4 个调用排队等待**（`--browser-max-concurrent-tabs`，另可配 profile 锁超时与 `--browser-reuse-wait`）
- 最稳定的团队形态：一台机器开着带远程调试的、已登录的 Chrome，所有调用方用 `--remote-chrome host:port` 指过去，避免多进程抢同一 profile
- 无头服务器/CI 可用 `oracle serve` 托管浏览器，调用方走 `--remote-host/--remote-token`（详见概念篇 [02](../concepts/02-browser-mode-mechanism.md)）

## 7. 日常使用速查

```bash
# 卡住时：最小文件集 + 一个明确问题
oracle --engine browser \
  -p "这个测试为什么在 CI 上超时？错误：<verbatim>，已尝试：<...>" \
  --file tests/foo.test.ts --file src/foo.ts

# 方案评审后继续同一会话追问
oracle --engine browser \
  -p "评审以下迁移方案，列最大风险" --file docs/migration.md \
  --browser-follow-up "在生产环境什么会先失败？" \
  --browser-follow-up "给出最小安全下一步"

# 查历史会话/接住长回答
oracle status --hours 72
oracle session <id> --render
```

Prompt 高信号模板（官方 SKILL.md 要点）：项目简报（栈+构建/测试命令+平台约束）、目录地图、逐字报错与已尝试项、约束条件、期望输出格式——Oracle 对项目零预知，这些都不能省。
