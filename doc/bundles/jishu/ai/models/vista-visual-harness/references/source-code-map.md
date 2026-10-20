---
type: reference
title: "VISTA 源码快照登记"
description: "登记 VISTA 代码仓库的不可变 commit、目录结构与模块规模、脚本计数口径、源码事实引用边界，以及八个工具与帧档案的实现坐标。"
tags: [vista, source-code, python, snapshot, mcp]
generated: { by: "opencode/minimax-m3.1-flash-free", at: "2026-10-20" }
verified:
  - { by: "process:seven-concepts-v", at: "2026-10-20" }
status: stable
stale_after: 2027-04-20
sources:
  - id: vista-commit
    url: "https://github.com/joshhhhhan/VISTA/tree/c97c354f0a8948256545a3e8850a1848f8e5b8c1"
    title: "VISTA 固定源码 commit"
  - id: vista-repo
    url: "https://github.com/joshhhhhan/VISTA"
    title: "VISTA 代码仓库"
  - id: paper
    url: "https://arxiv.org/abs/2610.02200"
    title: "VISTA: A Visual Harness for Reasoning in an Interactive World"
---

# VISTA 源码快照登记

## 一、信源坐标

| 项目 | 值 |
|------|-----|
| 项目 | VISTA——多模态模型的视觉原生 Harness 实现（Python）[F-086] |
| 远端仓库 | `https://github.com/joshhhhhan/VISTA` |
| 许可 | MIT License [F-086] |
| release tag | **无任何 tag**（GitHub API 查询结果为空）→ 按 Skill 规范固定到 commit hash [F-086] |
| 固定源码 commit | `c97c354f0a8948256545a3e8850a1848f8e5b8c1`（2026-10-04，提交信息 `update`）[F-086] |
| commit 页面 | [固定 commit](https://github.com/joshhhhhan/VISTA/commit/c97c354f0a8948256545a3e8850a1848f8e5b8c1) |
| 提交历史 | 仅 2 个提交：首提交 `900aa3380e4f1120436d83b2ce1115a38ac29bf9`（2026-09-05, Initial release）、次提交即本束固定 commit [F-086]。**核验口径**：提交总数经 GitHub API 取得；本地为 depth=1 浅克隆，`rev-list --count` 只能数出 1，故不可本地复核总数 |
| 本地只读检出位 | `external/libs/joshhhhhan/VISTA/`（仅工作区定位，**不作 bundle 引用**） |
| 盘点日期 | 2026-10-20 |

**引用规则**：源码文件引用一律采用 GitHub `blob/<commit>/<path>#Lx-Ly` 形式。本束**不写入任何本机绝对路径**，也不使用 file 协议的绝对路径引用。

## 二、规模盘点（脚本计数，非人工枚举）

计数对象为固定 commit 的工作树，**排除 `.git` 目录**；行数口径为 `len(open(f, encoding='utf-8').read().splitlines())` [F-087][F-088][F-089]：

| 指标 | 数量 | 计数口径 |
|------|------|---------|
| 工作树文件总数 | **104** | 递归遍历，排除 `.git` |
| `.py` 文件 | **82** | 后缀匹配 |
| `.sh` 文件 | **8** | 后缀匹配 |
| `.md` 文件 | **5** | 后缀匹配 |
| Dockerfile | **2** | 文件名前缀 `Dockerfile` |
| Python 总行数 | **18,754** | `splitlines()` 求和 |
| `def`/`async def` 定义 | **705**（其中 `async def` **7**） | 正则 `^\s*(?:async\s+)?def\s+(\w+)`，AST 交叉一致 |
| 去重函数名 | **465** | 上述捕获名去重 |
| `class` 定义 | **90** | 正则 `^\s*class\s+(\w+)`，AST 交叉一致 |
| 去重类名 | **84** | 上述捕获名去重 |

> **为什么同时给原始匹配数与去重名数**：两者不等是正常的（同名方法分布在不同类中）。本表两行都列出，避免下游把 705 当成"705 个不同函数"。

## 三、目录结构与分层

```
VISTA/
├── src/vista/
│   ├── cli.py            # 统一 CLI 入口（--profile / --backend）
│   ├── core/             # 与基准无关的 Harness 核心（14 个 .py / 3,647 行）
│   │   ├── contracts.py  # 契约层：ToolSpec / ToolReply / Observation / Effect ...
│   │   ├── tools.py      # 八件套工具的 JSON Schema 定义
│   │   ├── session.py    # SessionController：工具派发、裁剪放大、像素读出
│   │   ├── support.py    # TaskContext：帧档案、笔记文件、压缩标记
│   │   ├── dispatcher.py # 工具白名单与压缩后次序约束
│   │   ├── profiles.py   # ContextMode / InteractionMode / CompactionMode / AgentProfile
│   │   ├── runtime.py    # TaskRuntime：预算、超时、运行期状态
│   │   └── prompts/      # claude.md / codex.md —— 核心提示词契约
│   ├── backends/         # Agent CLI 后端适配（6 个 .py / 691 行）
│   │   ├── claude/       # Claude Code CLI：10 个文件 / 3,271 行
│   │   └── codex/        # Codex CLI：4 个文件 / 1,808 行
│   └── benchmarks/       # 四个基准适配
│       ├── arc3/         # ARC-AGI-3（7 个 .py / 1,291 行，另有 claude/ codex/ 子包）
│       ├── aigamestore/  # AI GameStore（6 / 1,546）
│       ├── babyvision/   # BabyVision（8 / 1,369）
│       └── gameworld/    # GameWorld（9 / 1,308）
├── scripts/              # 8 个 .sh + run_arc3_batch.py
├── Dockerfile.codex-player / Dockerfile.claude-player
└── pyproject.toml / .env.example / README.md / LICENSE
```

四个基准子包的规模均来自同一计数脚本 [F-088]。

## 四、打包、依赖与入口

| 项 | 值 | F |
|----|-----|---|
| 包名 / 版本 | `vista-arc3` / `0.1.0` | [F-090] |
| Python 要求 | `>=3.12,<3.13` | [F-090] |
| 构建后端 | setuptools | [F-090] |
| 控制台入口 | `vista`、`vista-gameworld`、`vista-aigamestore`、`vista-babyvision` | [F-090] |
| 固定依赖 | `arc-agi==0.9.9`、`arcengine==0.9.3`、`numpy==2.5.1`、`pillow==12.2.0`、`python-dotenv==1.2.2`、`requests==2.34.2`、`urllib3==2.7.0`、`jsonschema>=4.23,<5` | [F-091] |
| 可选 extras | gameworld（playwright/PyYAML/Jinja2）、aigamestore（playwright）、babyvision（regex）、dev（ruff） | [F-091] |

## 五、九个工具的实现坐标

| 工具 | 定义位置 | 实现位置 | F |
|------|---------|---------|---|
| `inspect` | `core/tools.py:62` `build_inspect_tool` | `core/support.py` `_inspect` / `core/session.py` 裁剪放大 | [F-096][F-097] |
| `read_pixels` | `core/tools.py:130` `build_read_pixels_tool` | `core/session.py:645` `_read_pixels` | [F-098][F-099] |
| `history` | `core/tools.py:316` `HISTORY_TOOL`；`arc3/*/tools.py:118` | `arc3/*/controller.py:576` `_history` | [F-095] |
| `play` | `arc3/*/tools.py:74` `build_play_tool` | `arc3/*/controller.py` | [F-100][F-101] |
| `read_guide` / `write_guide` | `core/tools.py:31` / `:211` | `core/dispatcher.py` | [F-095][F-121] |
| `read_working` / `write_working` | `core/tools.py:273` / `:290` | `core/dispatcher.py` | [F-095] |
| `save_compact_checkpoint` | `core/tools.py:237` | `core/dispatcher.py:98`（派发）、`:187`（完成回执 "WORKING.md updated; compact checkpoint ready."） | [F-121][F-122] |

工具白名单（派发允许集）为 `{"save_compact_checkpoint","inspect","read_pixels","history","play"}` [F-107]。

## 六、帧档案与工作目录坐标

| 产物 | 位置 | F |
|------|------|---|
| 帧档案（通用会话） | `visuals/turn_%06d_frame_0<ext>`，落盘后 `chmod 0o400` | [F-102] |
| 帧截图（ARC-AGI-3） | `screenshots/turn_%03d_frame_%02d.png` | [F-102] |
| 跨关卡笔记 | `GUIDE.md`（0600，初始内容 `"No reliable model yet.\n"`） | [F-103] |
| 当前工作笔记 | `WORKING.md`（0600） | [F-103] |
| 工作笔记溯源 | `working_memory_provenance.json` | [F-103] |
| 压缩恢复日志 | `compact_recovery.jsonl` | [F-103] |
| 压缩状态标记 | `compact_checkpoint.requested` / `.ready` / `compact_restore.pending` / `compact_guide.snapshot` / `retry_boundary.pending` | [F-103] |

## 七、版本锚点（上游依赖被固定到不可变坐标）

| 上游 | 锚定 revision | F |
|------|--------------|---|
| VISTA 自身发布版 | `900aa3380e4f1120436d83b2ce1115a38ac29bf9` | [F-113] |
| BabyVision 数据集 | `7f92fd4b1dc1c68b7b936a9bc09c68b4a944a55a` | [F-113] |
| GameWorld 仓库 | `f2883c34e377c8b73fdb503a4a8e87be12310df7` | [F-113] |
| GameWorld 游戏集 | `a23b4370c3f99df6fa4ee01ea0299fdab9668b86` | [F-113] |
| ARC-AGI-3 SDK | `arc-agi==0.9.9` / `arcengine==0.9.3` | [F-091] |

> 这些锚点是源码实现"可复现性"的真正基础：论文只给了论文版本，而源码把**每一个外部上游**都固定到了具体 revision。

## 八、源码事实的引用边界

- 源码事实编号为 **F-086 ~ F-130**，与论文/博文事实（F-001 ~ F-085）同表登记，便于统一回溯。
- **不把源码实现细节等同于论文主张**：例如 `DEFAULT_MAX_STEPS = 2000` 与论文的 "2,000 total actions" 数值一致，但"论文说的是实验协议、源码说的是默认参数"，两者在正文中分别标注。
- 源码**未实现**的部分（私有/半私有集适配、BabyVision 的 48 题任务集多于论文的 39 题）同样登记，避免读者误以为源码覆盖了论文全部实验面 [F-130]。

## 九、关联

- 论文谱系与阅读地图：[paper-reading-map.md](paper-reading-map.md)
- 事实登记：[article-source.md](article-source.md)
- 核验报告：[verification.md](verification.md)
