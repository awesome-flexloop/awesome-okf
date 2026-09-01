---
type: Concept
title: "项目概述：一个把 Android 评测环境装进单个 Docker 镜像的框架"
description: "MobileWorld 的包定义与双 CLI 入口、40 项依赖与 optional-groups、ruff/mypy 工程配置、3 个 submodule 应用资源、CHANGELOG 版本时间线与 Pages 站点/轨迹提交机制"
tags: [MobileWorld, GUI智能体, 评测框架, 阿里通义, 项目概述]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T14:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T14:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: mobile-world-facts
    resource: /references/facts.md
    title: MobileWorld 源码事实台账
  - id: mobile-world-sources
    resource: /references/source-registry.md
    title: MobileWorld 信源登记
---

# 项目概述：一个把 Android 评测环境装进单个 Docker 镜像的框架

MobileWorld（PyPI 包名 `mobile-world`，版本 0.1.0）是 Tongyi-MAI 团队开源的移动 GUI 智能体评测框架，自述为 "Mobile GUI automation and testing framework"（F-001）。它把整套 Android 评测环境——DinD 容器里的 Android 模拟器、FastAPI 控制服务、任务体系与判分逻辑——压缩进单个 Docker 镜像，通过两条等价 CLI 入口 `mobile-world` 与 `mw` 驱动从环境启动、Agent 评测到大规模编排的全流程（F-002）。初版于 2025-12-23 发布并附 arXiv 技术报告 2512.19432（F-078）。

本篇是全束入口：先看包怎么定义、命令怎么组织，再看它带了哪些应用资源和版本演进，为后续分层精读建立整体坐标。

## 包定义与双 CLI 入口

`pyproject.toml` 中的包元数据（F-001）：

- 包名 `mobile-world`，版本 `0.1.0`
- 描述 "Mobile GUI automation and testing framework"
- `requires-python = ">=3.12,<3.13"`（锁定 Python 3.12）
- 构建后端 `hatchling.build`

`[project.scripts]` 定义两个**等价入口**，指向同一个函数 `mobile_world.core.cli:main`（F-002）：

```toml
[project.scripts]
mobile-world = "mobile_world.core.cli:main"
mw = "mobile_world.core.cli:main"
```

因此本文档中 `mobile-world ...` 与 `mw ...` 可互换——官方脚本（F-072）用短形式 `mw`，docs（F-073）用长形式 `mobile-world`。

## 依赖与工程配置

运行时依赖共 40 项（F-003），关键组件勾勒出技术栈轮廓：

| 依赖 | 用途指向 |
|---|---|
| `fastapi>=0.104.0` + `uvicorn[standard]` | 控制服务（F-031 的 FastAPI 服务） |
| `gradio>=5.49.0` | 设备查看器界面 |
| `mcp>=1.9.4`、`fastmcp>=2.9.2` | MCP 工具协议 |
| `openai>=1.106.1` | Agent 模型调用 |
| `python-fasthtml>=0.12.33` | eval-server 与 log_viewer 界面 |
| `psycopg2-binary` | Mattermost/Mastodon 后端数据库直连 |
| `joblib` | 评测线程并行（F-038） |
| `android_env==1.2.3`、`absl-py==2.1.0` | Android 环境基础 |
| `imagehash`、`markdownify`、`loguru`、`python-dotenv`、`qwen-agent` | 辅助能力 |

optional-dependencies 三组（F-003）：

```toml
agents = ["openai>=1.106.1"]
dev = ["pytest", "pytest-asyncio", "ruff", "pylint", "black", "mypy", "ipdb"]
all = ["mobile-world[agents,dev]"]
```

工程配置（F-004）：`target-version = "py312"`、`line-length = 100`，lint select 含 `E,W,F,I,UP,FA`；对 `core/log_viewer/routes.py` 豁免 `F405/F403`（FastHTML 星号导入标准模式）；pytest `testpaths = ["tests"]`。

## 应用资源：3 个 submodule

真实感任务依赖 3 个 git submodule 应用资源（F-006）：

| 路径 | 仓库 |
|---|---|
| `resources/mall` | https://github.com/qykong/mall_fork.git |
| `resources/mail` | https://github.com/nrgao/mail_fork.git |
| `resources/mastodon-android` | https://github.com/patdooog/mastodon-android.git |

它们与 `APP_DICT` 中的包名对应（F-055），任务初始化时会配套启动/停止其后端（F-061）。

## 版本时间线与社区机制

CHANGELOG 记录的关键节点（F-078）：

| 日期 | 事件 |
|---|---|
| 2025-12-23 | 初版发布（arXiv 2512.19432，镜像 `ghcr.io/Tongyi-MAI/mobile_world:latest`） |
| 2025-12-29 | MAI-UI 41.7% |
| 2026-01-16 | Seed-1.8 52.1% GUI-Only；MAI-UI-235B-A22B 45.4% |
| 2026-03-20 | Seed-2.0-Pro 63.2%/61.4% + 真机支持（新增 `gui_owl_1_5`、`ui_venus_agent` 两个 agent） |
| 2026-04-15 | Mattermost 会话过期修复（任务初始化时自动运行，无需重建镜像） |
| 2026-04-22 | 加入 Claude-Opus-4.7 与 Kimi-K2.6 |
| 2026-04-29 | Arena 对比页 + `site/bundle_trajs.py` 社区提交 |

仓库的 `.github/workflows/deploy-pages.yml` 是唯一工作流文件，负责 GitHub Pages 部署，与 `site/` 目录配套——`site/` 下含 `leaderboard.json`、`bundle_trajs.py` 与 `trajs/*.json.gz` 轨迹包，构成官方榜单与社区轨迹提交机制（F-079，提交流程见 `/examples/03-real-device-and-leaderboard-submit.md`）。

## 全束速览

- 想跑起来：`/concepts/01-quickstart-installation.md`
- 想懂结构：`/concepts/02-architecture-layers.md`
- 想接模型：`/concepts/03-agent-registry.md`

## 相关概念

- [/concepts/01-quickstart-installation.md](/concepts/01-quickstart-installation.md)——.env 配置、容器启动与 Windows/WSL/KVM 前置
- [/concepts/02-architecture-layers.md](/concepts/02-architecture-layers.md)——四层架构地图与 CLI 八子命令
- [/concepts/07-docker-environment.md](/concepts/07-docker-environment.md)——单容器全栈镜像的构建细节
- [../mai-ui/index.md](../mai-ui/index.md)——MAI-UI 是 MobileWorld 排行榜上的模型提交方（F-078 记录其 41.7%），其导航 Agent 以 `mai_ui_agent` 注册进本框架注册表（F-011）
- [../qwen-ui-agent/index.md](../qwen-ui-agent/index.md)——Qwen-UI-Agent 的 MobileWorld 82.1% 成绩即在本框架上取得
- [../mobilepa-bench/index.md](../mobilepa-bench/index.md)——同属 MAI Team 生态的结构化工具规划基准，与本项目互补层级
