---
type: Example
title: 消息网关服务化与 Cron 定时作业实操
description: 用 systemd 用户服务或 CLI gateway 子命令管理网关生命周期，并用函数式 cron tick 与 create_job 字段创建定时作业；前置阅读概念篇 08。
tags: [kylin-agent-runtime, gateway, cron, systemd, operations]
generated: { by: "process:seven-concepts-e/trae-cn", at: 2026-10-14T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00+08:00 }
status: stable
stale_after: 2027-10-14
sources:
  - id: source-code
    resource: /references/source-code-map.md
    title: Kylin Agent Runtime 源码信源
---

# 示例：网关服务化与 Cron 定时作业

> 前置阅读：[08-gateway-and-cron](/concepts/08-gateway-and-cron.md)（GatewayRunner 生命周期、平台双轨制、会话存储与函数式调度的设计原理）。本篇只讲操作面。

## 一、用 systemd 用户服务管理网关（Linux）

网关安装后注册为 `kylin-agent-runtime-gateway.service` 用户服务（README.zh-CN.md:52，F-012）。启动、停止或重启（来源：README.zh-CN.md:56-58）：

```bash
systemctl --user start kylin-agent-runtime-gateway.service
systemctl --user stop kylin-agent-runtime-gateway.service
systemctl --user restart kylin-agent-runtime-gateway.service
```

查看状态（README.zh-CN.md:61）、启用/禁用开机自启（:64-65）、实时跟踪日志（:68）：

```bash
systemctl --user status kylin-agent-runtime-gateway.service
systemctl --user enable kylin-agent-runtime-gateway.service
systemctl --user disable kylin-agent-runtime-gateway.service
journalctl --user -u kylin-agent-runtime-gateway.service -f
```

**系统级服务**：去掉命令中的 `--user`，并对相应 `systemctl` 命令使用 `sudo` 执行（README.zh-CN.md:71）。

## 二、用 CLI 管理网关（不依赖 systemd）

`kylin-agent-runtime gateway` 提供 10 个二级命令（F-136，注册于 kylin_agent_runtime_cli/main.py:10712-10857）：

| 子命令 | 用途（parser help 文案，F-136） |
|---|---|
| `run` | 前台运行网关 |
| `start` / `stop` / `restart` | 后台方式启动/停止/重启网关进程 |
| `status` | 查看网关运行状态 |
| `install` / `uninstall` | 安装/卸载服务（systemd 单元） |
| `list` | 列出全部配置档案及其网关状态 |
| `setup` | 交互式配置消息平台 |
| `migrate-legacy` | 迁移旧版网关配置 |

基本调用形式：

```bash
kylin-agent-runtime gateway status
kylin-agent-runtime gateway run
kylin-agent-runtime gateway setup
```

说明：以上为二级命令的基础形态（F-136）；各子命令的具体参数以 `kylin-agent-runtime gateway <子命令> --help` 的实际输出为准，本篇不臆造参数。优雅重启走 SIGUSR1 信号与 ProfileGatewayProcess 快照（F-136）。

## 三、理解 Cron：函数式 tick，而非常驻 Scheduler

Cron 子系统**没有 Scheduler 类**：执行靠 `run_job(job)`、轮询靠 `tick(verbose, adapters, loop)`（cron/scheduler.py:1232、:1885，F-125）。CLI 暴露的对应面为 `cron list/create/edit/tick/status`（另有 pause/resume/run/remove，F-144；注册见 main.py:11236-11381）：

```bash
kylin-agent-runtime cron list
kylin-agent-runtime cron status
kylin-agent-runtime cron tick
```

- `cron list`：列出全部作业及 `[active]/[paused]/[completed]/[disabled]` 状态（kylin_agent_runtime_cli/cron.py:77-85）；
- `cron status`：查看调度器是否在运行；
- `cron tick`：运行一次所有到期作业后退出（parser help："Run due jobs once and exit"，main.py:11381），适合挂系统 crontab 或由网关周期触发。

`cron create` / `cron edit` 用于新建与编辑作业（main.py:11240、:11292），其参数集合对应作业模型字段；下表按源码函数签名逐字段说明。

## 四、新建定时作业：create_job 字段级说明

作业在代码中是普通 dict，由 `create_job(...)` 创建（cron/jobs.py:509-527，F-126）。函数签名（源码逐字）：

```python
def create_job(
    prompt: Optional[str],
    schedule: str,
    name: Optional[str] = None,
    repeat: Optional[int] = None,
    deliver: Optional[str] = None,
    origin: Optional[Dict[str, Any]] = None,
    skill: Optional[str] = None,
    skills: Optional[List[str]] = None,
    model: Optional[str] = None,
    provider: Optional[str] = None,
    base_url: Optional[str] = None,
    script: Optional[str] = None,
    context_from: Optional[Union[str, List[str]]] = None,
    enabled_toolsets: Optional[List[str]] = None,
    workdir: Optional[str] = None,
    profile: Optional[str] = None,
    no_agent: bool = False,
) -> Dict[str, Any]:
```

来源：cron/jobs.py:509-527。字段语义（docstring，cron/jobs.py:532-544；F-126）：

| 字段 | 含义 |
|---|---|
| `prompt` | 自包含的提示词；设置 `skill` 时作为任务指令；`no_agent=True` 时被忽略，仅作名称提示 |
| `schedule` | 调度字符串，解析规则见 `parse_schedule`（依赖 croniter，F-003/F-126） |
| `name` | 可选的友好名称 |
| `repeat` | 执行次数：`None` 永久、`1` 一次 |
| `deliver` | 结果投递目标，如 `"origin"` / `"local"` / `"telegram"` 等 |
| `origin` | 作业创建来源信息，供 `deliver="origin"` 回投 |
| `skill` / `skills` | 运行前加载的单个旧版技能 / 有序技能列表 |
| `model` / `provider` / `base_url` | 作业级模型、供应商与端点覆盖 |
| `script` | 脚本路径，其 stdout 喂给作业；与 `no_agent` 配合可只跑脚本不调模型 |
| `context_from` | 上下文来源（字符串或列表） |
| `enabled_toolsets` | 该作业启用的工具集白名单 |
| `workdir` / `profile` | 工作目录 / 配置档案名 |
| `no_agent` | 为 `True` 时不启动 Agent 模型对话 |

字段级示例（**示例值非源码常量**，仅演示上表字段的合法组合；调度表达式遵循 parse_schedule 的 croniter 规则，F-126）：

```python
from cron.jobs import create_job  # cron/jobs.py:509

job = create_job(
    prompt="汇总工作目录下今日的 git 提交并生成日报",
    schedule="0 18 * * 1-5",      # 周一至周五 18:00（croniter 规则，F-003/F-126）
    name="daily-git-report",
    repeat=None,                  # 永久重复
    deliver="local",              # 结果留在本地
    workdir="/path/to/repo",
    enabled_toolsets=["terminal"],
    no_agent=False,
)
```

安全提示：无论 prompt 来自哪里，组装后的完整提示词都会经过注入扫描，命中注入模式会抛出 `CronPromptInjectionBlocked`（cron/scheduler.py:48、:1207，F-125）；`script` 的 stdout 因此也无法伪造系统指令。桌面端会话由 `reconcile_desktop_job_sessions` 自动对账（cron/desktop_sessions.py:15，F-127）。

## 相关概念

- [08-gateway-and-cron](/concepts/08-gateway-and-cron.md)：设计原理——GatewayRunner、会话三件套、22/21/32 平台口径。
- [示例 01：安装、初始化与首次运行](/examples/01-install-setup-first-run.md)：安装与 setup 前置步骤。
- [09-acp-mcp-protocols](/concepts/09-acp-mcp-protocols.md)：MCP 可读取网关会话与审批事件。
