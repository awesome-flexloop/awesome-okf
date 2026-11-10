---
type: Reference
title: "官方教程信源清单（F-101 ~ F-114）"
description: "minimal-agent.com 官方教程《Building a minimal AI agent from scratch》的事实登记——50 行原型、三组件、两种动作格式、异常与格式纠错、与 v2.4.6 生产代码的差异"
tags: [信源, 官方教程, minimal-agent, 从零构建, F编号]
generated: { by: "seven-concepts-cmd/R", at: "2026-11-10T17:18:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:20:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: minimal-agent-tutorial
    resource: https://minimal-agent.com/
    title: "Building a minimal AI agent from scratch（Kilian Lieret, Carlos Jimenez, John Yang, Ofir Press）"
  - id: tutorial-repo
    resource: https://github.com/SWE-agent/minimal-agent-tutorial
    title: "教程源码仓库（本地 commit 8ed09f1，2026-02-03）"
---

# 官方教程信源清单（F-101 ~ F-114）

> 本地路径：`external/dao/SWE-agent/minimal-agent-tutorial/`，正文在 `docs/index.md`（24,083 字节，commit `8ed09f1`，2026-02-03）。教程是“从零实现”的独立文档，不是 mini-swe-agent 的 README 子页。

| 编号 | 事实或声明 | 来源层级 | 核验 |
|---|---|---|---|
| F-101 | 教程站点为 `minimal-agent.com`，源码仓库为 `SWE-agent/minimal-agent-tutorial`，内容集中在 `docs/index.md`（24,083 字节）。 | 官方教程 | 通过（本地目录） |
| F-102 | 教程作者为 Kilian Lieret、Carlos Jimenez、John Yang、Ofir Press；贡献者 Cesar Garcia、piot。 | 官方教程 | 单源（教程署名） |
| F-103 | 教程称初始最小 Agent “only some 60 lines long”，首个原型为 50 行。 | 官方教程 | 通过（正文；与代码块规模一致） |
| F-104 | 核心循环为：`messages` 列表 → `query_lm` → 追加 assistant → `parse_action` → 若 `exit` 则退出 → `execute_action` → 追加 user output。 | 官方教程 | 通过（正文伪代码与完整代码） |
| F-105 | 实现只需三件事：查询 LM API、解析动作、执行动作；若模型支持 tool calling，可跳过文本解析，但教程为简化不展开。 | 官方教程 | 通过（正文） |
| F-106 | 教程给出 OpenAI、Anthropic、OpenRouter、LiteLLM、GLM 五种查询示例，并推荐 LiteLLM 作为默认选择。 | 官方教程 | 通过（正文 tab） |
| F-107 | 动作编码支持两种格式：三反引号 `bash-action` 块与 XML `<bash_action>`；教程推荐三反引号。 | 官方教程 | 通过（正文） |
| F-108 | 三反引号解析使用 `re.findall(r"```bash-action\\s*\\n(.*?)\\n```", lm_output, re.DOTALL)`，取第一个匹配，找不到返回空串。 | 官方教程 | 通过（正文代码） |
| F-109 | 执行函数使用 `subprocess.run(shell=True, text=True, env=os.environ, encoding="utf-8", errors="replace", stdout=PIPE, stderr=STDOUT, timeout=30)`。 | 官方教程 | 通过（正文代码） |
| F-110 | 教程承认两个限制：不能持久 `cd`、不能持久 `export`；并认为减少隐藏状态、强制绝对路径可能对模型有帮助，类比 Claude Code 的子 shell 行为。 | 官方教程 | 作者观点（与 F-072/F-073 一致） |
| F-111 | 健壮性建议：捕获异常并把错误消息追加到 `messages`；格式错误时追加纠正提示；设置 `PAGER`/`MANPAGER`/`LESS`/`PIP_PROGRESS_BAR`/`TQDM_DISABLE` 避免交互式工具卡住。 | 官方教程 | 通过（正文） |
| F-112 | 教程把生产代码映射为 `Agent.run` / `Model.query` / `Environment.execute`；Docker 环境只是把 `subprocess.run` 换成 `docker exec`；并称按此教程可达到 74% SWE-bench verified。 | 官方教程 | 部分通过（结构与 F-049/F-062 一致；74% 同 F-070 口径） |
| F-113 | 教程示例提到 `TerminatingException` / `NonterminatingException`，但 v2.4.6 源码中不存在这两个名字；实际异常体系为 `InterruptAgentFlow`/`Submitted`/`LimitsExceeded`/`TimeExceeded`/`UserInterruption`/`FormatError`。 | 官方教程 vs 源码 | ⚠️ 文档漂移（以源码为准） |
| F-114 | 教程的完成信号是 `exit` 命令；v2.4.6 的完成信号是 `COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT` 魔法行（F-055、F-062）。 | 官方教程 vs 源码 | ⚠️ 版本差异（以源码为准） |

```{toctree}
:hidden:
:maxdepth: 3

../blog-source
../repo-source
../verification
```
