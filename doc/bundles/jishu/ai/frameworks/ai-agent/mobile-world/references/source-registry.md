---
type: Reference
title: "MobileWorld 信源登记"
description: "MobileWorld 源码精读束的信源登记簿——按根配置/agents/core/runtime/tasks/docker/docs/scripts/site 分层逐项登记相对路径与覆盖事实范围（F-001~F-080）"
tags: [MobileWorld, 信源登记, 源码溯源]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T14:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T14:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: mobile-world-facts
    resource: /references/facts.md
    title: MobileWorld 源码事实台账
---

# MobileWorld 信源登记

> **信源根**：`external/libs/tools/Tongyi-MAI/MobileWorld`（下表所有相对路径均相对此根；该目录为 git 检出的 MobileWorld 仓库源码）。
> **采集日期**：2026-08-29 ｜ **采集方式**：源码直读（零推测），每条事实登记于 [facts.md](facts.md) 对应 F-xxx。

## 信源总览

| 分组 | 文件数 | 覆盖事实 |
|---|---|---|
| 根配置 | 6 | F-001~F-006、F-078、F-079 |
| src/mobile_world/agents/ | 6 | F-007~F-017 |
| src/mobile_world/core/ | 22 | F-018~F-045 |
| src/mobile_world/runtime/ | 12 | F-045~F-059 |
| src/mobile_world/tasks/ | 5 | F-060~F-066 |
| docker/ | 4 | F-067~F-070 |
| docs/ | 7 | F-071、F-073~F-077、F-080 |
| scripts/ | 4 | F-072 |

## 根配置与元信息

| 相对路径 | 说明 | 覆盖事实 |
|---|---|---|
| `pyproject.toml` | 包定义、构建后端、CLI 入口、40 项依赖、optional-groups、ruff/mypy/pytest 配置 | F-001、F-002、F-003、F-004 |
| `README.md` | 项目说明信源（背景阅读，未单独登记编号事实） | — |
| `CHANGELOG.md` | 版本时间线与关键分数数字 | F-078 |
| `.env.example` | 6 个环境变量清单 | F-005 |
| `.gitmodules` | 3 个 submodule 应用资源 | F-006 |
| `.github/workflows/deploy-pages.yml` | 唯一 GitHub Pages 部署工作流（与 site/ 配套） | F-079 |

## src/mobile_world/agents/（Agent 抽象与注册）

| 相对路径 | 说明 | 覆盖事实 |
|---|---|---|
| `agents/base.py` | BaseAgent 抽象基类、openai_chat_completions_create 模型怪癖分支、token 记账、MCPAgent | F-007~F-010 |
| `agents/registry.py` | AGENT_CONFIGS 九项注册表、create_agent 双路径、load_agent_from_file | F-011~F-013 |
| `agents/grounding/uiins.py` | UIINSGroundingAgent grounding 子代理 | F-014 |
| `agents/utils/agent_mapping.py` | 三张动作映射字典 | F-015 |
| `agents/utils/helpers.py` | 图像处理常量与工具函数 | F-016 |
| `agents/utils/test_agent.py` | 统一 agent 测试脚本入口 | F-017 |

## src/mobile_world/core/（CLI、服务、编排）

| 相对路径 | 说明 | 覆盖事实 |
|---|---|---|
| `core/cli.py` + `core/subcommands/__init__.py` | CLI 顶层 8 子命令注册与分发 | F-018 |
| `core/subcommands/eval.py` | eval 公共参数、专有参数、pass@k 与 ALL 统计报告 | F-019、F-020、F-021、F-022 |
| `core/subcommands/server.py` | server 子命令默认参数 | F-023 |
| `core/subcommands/env.py` | env 容器生命周期子动作、check 校验、restart | F-024、F-025、F-026 |
| `core/subcommands/info.py` | info task/agent/app/mcp 查询与 Excel 导出 | F-027 |
| `core/subcommands/logs.py` | logs view/results | F-028 |
| `core/subcommands/eval_server.py` | eval-server 子命令参数 | F-029 |
| `core/subcommands/test.py` | test 交互式任务设备自动发现 | F-030 |
| `core/server.py` | FastAPI 服务、/health 自愈、19 端点全表、/step 动作分发表 | F-031、F-032、F-033、F-034 |
| `core/api/server.py` | start_server 编程接口与 uvicorn 配置 | F-035 |
| `core/api/env.py` | 容器管理与前置检查函数族 | F-036 |
| `core/runner.py` | run_agent_with_evaluation、任务执行主循环、env 初始化分派 | F-037、F-038、F-039 |
| `core/user_task_runner/runner.py` | 交互式运行器（test 子命令调用） | F-040 |
| `core/eval_server/db.py` | SQLite WAL jobs 表结构 | F-041 |
| `core/eval_server/app.py` + `core/eval_server/routes.py` | FastHTML 应用与 11 条路由 | F-042 |
| `core/eval_server/worker.py` | 后台 worker（40 容器/tmux/5 秒轮询） | F-043 |
| `core/log_viewer/` | FastHTML 日志查看器模块 | F-044 |
| `core/device_viewer.py` | ScrcpyScreenViewer 设备查看器 | F-045 |

## src/mobile_world/runtime/（环境客户端与设备控制）

| 相对路径 | 说明 | 覆盖事实 |
|---|---|---|
| `runtime/client.py` | AndroidEnvClient 签名与任务生命周期、AndroidMCPEnvClient 工具过滤 | F-046、F-047、F-048 |
| `runtime/controller.py` | AndroidController 初始化、35 方法清单、ask_user 用户模拟 | F-049、F-050、F-051 |
| `runtime/mcp_server.py` | MCP_CONFIG 五个远端服务、SyncMCPClient 串行化与重试 | F-052、F-053 |
| `runtime/utils/models.py` | JSONAction 模型与 19 动作常量、请求模型、APP_DICT/COMMON_APP_MAPPER | F-054、F-055 |
| `runtime/utils/constants.py` | artifacts 目录常量 | F-056 |
| `runtime/utils/trajectory_logger.py` | TrajLogger、result.txt 格式、图像标注工具函数 | F-057 |
| `runtime/utils/docker.py` | docker 工具函数族 | F-058 |
| `runtime/app_helpers/`（7 模块：mail、fossify_calendar、mall、mastodon、mattermost、mcp、system） | 应用后端辅助函数 | F-059 |

## src/mobile_world/tasks/（任务体系）

| 相对路径 | 说明 | 覆盖事实 |
|---|---|---|
| `tasks/base.py` | BaseTask 抽象接口、initialize_task 流程、用户代理初始化 | F-060、F-061、F-062 |
| `tasks/registry.py` | TaskRegistry rglob 自动扫描注册 | F-063 |
| `tasks/utils.py` | ModelConfig 与用户模拟应答函数 | F-064 |
| `tasks/test_task.py` | 任务测试脚本 | F-065 |
| `tasks/definitions/` | 10 个场景任务子目录结构统计 | F-066 |

## docker/（容器环境）

| 相对路径 | 说明 | 覆盖事实 |
|---|---|---|
| `docker/Dockerfile` | DinD 基础镜像、Android SDK 34 + AVD、HEALTHCHECK | F-067 |
| `docker/entrypoint.sh` | 十步启动序列（禁 IPv6/iptables 探测/docker load/模拟器/socat/server） | F-068 |
| `docker/start_emulator.sh` | 模拟器启动参数、动画禁用、proxy_chain 接入 | F-069 |
| `docker/proxy_chain.py` | 旁路代理拓扑与直连规则 | F-070 |

## docs/（官方文档 7 篇）

| 相对路径 | 说明 | 覆盖事实 |
|---|---|---|
| `docs/docker_changelog.md` | Docker 镜像版本史 v1.0~v1.2 | F-071 |
| `docs/configure_avd.md` | AVD 快照定制 8 步流程 | F-073 |
| `docs/real-devices.md` | 真机评测前置与各模型坐标约定表 | F-074 |
| `docs/submit.md` | leaderboard 三步提交流程 | F-075 |
| `docs/mcp_setup.md` | DashScope/ModelScope 双 MCP 提供商与密钥 | F-076 |
| `docs/development.md` | dev 模式挂载与容器内调试 | F-077 |
| `docs/setup_for_windows.md` | Windows/WSL/KVM 前置配置 | F-080 |

## scripts/（官方评测脚本 4 个）

| 相对路径 | 说明 | 覆盖事实 |
|---|---|---|
| `scripts/run_agentic.sh` | planner_executor + uiins executor | F-072 |
| `scripts/run_claude_e2e.sh` | general_e2e + claude-sonnet-4-5 | F-072 |
| `scripts/run_gemini_e2e.sh` | general_e2e + gemini-3-pro-preview | F-072 |
| `scripts/run_qwen3vl.sh` | qwen3vl + Qwen3-VL-235B-A22B | F-072 |

## 已登记外部 URL（仅限事实清单内登记项）

| URL | 事实编号 |
|---|---|
| https://arxiv.org/abs/2512.19432（初版发布技术报告） | F-078 |
| https://github.com/qykong/mall_fork.git | F-006 |
| https://github.com/nrgao/mail_fork.git | F-006 |
| https://github.com/patdooog/mastodon-android.git | F-006 |

## 采集边界说明

- `site/` 目录（leaderboard.json、bundle_trajs.py、trajs/*.json.gz）作为 F-075/F-079 的关联信源登记，轨迹包内容未逐字读取。
- `docker/Dockerfile.update`、`docker/start_novnc.sh` 行为经 docker_changelog.md 与 entrypoint.sh 交叉确认，未逐字读取。
- `agents/utils/prompts/`（10 个 prompt 文件）与 `agents/implementations/`（9 个实现类）仅确认文件清单与导入关系，未逐字读取。
