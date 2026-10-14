---
type: Example
title: 安装、初始化与首次运行 Kylin Agent Runtime
description: 按中文 README 从 gitee 克隆、uv 建 3.11 虚拟环境、[all] 可编辑安装，到 setup 配置与交互/TUI/一次性任务/Dashboard 四种运行方式的完整上手步骤。
tags: [kylin-agent-runtime, install, setup, quickstart, uv]
generated: { by: "process:seven-concepts-e/trae-cn", at: 2026-10-14T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00+08:00 }
status: stable
stale_after: 2027-10-14
sources:
  - id: source-code
    resource: /references/source-code-map.md
    title: Kylin Agent Runtime 源码信源
---

# 示例：安装、初始化与首次运行

> 本篇所有 shell 命令均可在 README.zh-CN.md 逐字匹配，括号内为对应行段；适用环境为 Linux/macOS（README 的激活脚本采用 `source .venv/bin/activate` 形式）。要求 Python 3.11（README.zh-CN.md:15；pyproject.toml 声明 `requires-python >= 3.11`，F-001）。

## 步骤 1：克隆仓库

```bash
git clone https://gitee.com/openkylin/agent-runtime.git
cd agent-runtime
```

来源：README.zh-CN.md:11-12（安装段，F-010）。

## 步骤 2：安装 uv 并创建虚拟环境

如尚未安装 `uv`，使用官方脚本安装；随后以 Python 3.11 创建虚拟环境并激活（README.zh-CN.md:14-16；已有 uv 与 Python 3.11 时可直接从 `uv venv` 开始，README.zh-CN.md:20）：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.11
source .venv/bin/activate
```

## 步骤 3：以可编辑模式安装

```bash
uv pip install -e ".[all]"
```

来源：README.zh-CN.md:17（F-010）。`[all]` 只包含不可懒安装的 extra，模型、搜索、消息平台等可选后端改为首用时懒安装（F-004）。

## 步骤 4：首次配置 setup

首次运行前先激活虚拟环境，再启动交互式配置向导，完成模型提供商与 API Key 等基础配置：

```bash
source .venv/bin/activate
kylin-agent-runtime setup
```

来源：README.zh-CN.md:27-28（F-011）。向导实现为 `run_setup_wizard`（F-137）；配置与密钥最终落在用户目录 `~/.kylin-agent-runtime/`（config.yaml 放配置、.env 只放密钥，F-018）。

## 步骤 5：选择一种方式运行

配置完成后，在项目目录中启动交互式 Agent：

```bash
kylin-agent-runtime
```

来源：README.zh-CN.md:34（F-011）。

也可以按需使用其他三种运行方式：

```bash
# 启动现代终端界面（TUI）
kylin-agent-runtime --tui

# 执行一次性任务并仅输出最终结果
kylin-agent-runtime -z "分析当前项目并给出改进建议"

# 启动 Web 控制台（默认端口 9119）
kylin-agent-runtime dashboard
```

来源：README.zh-CN.md:39-48（F-011；dashboard 默认端口 9119，F-138）。

查看全部命令及参数：

```bash
kylin-agent-runtime --help
```

来源：README.zh-CN.md:75-77。

## 步骤 6：运行测试

运行默认测试脚本，或在已激活虚拟环境中直接用 pytest：

```bash
scripts/run_tests.sh
python -m pytest tests/ -q
```

来源：README.zh-CN.md:113-121。pytest 配置为 testpaths `tests`、`-n auto` 并带 30 秒超时（F-009）。

## 开发安装

参与开发或运行测试时，安装开发依赖 extra：

```bash
git clone https://gitee.com/openkylin/agent-runtime.git
cd agent-runtime

curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[all,dev]"
```

来源：README.zh-CN.md:83-91。

## 更新版本

进入项目目录后拉取最新代码并重新安装：

```bash
git pull
source .venv/bin/activate
uv pip install -e ".[all]"
```

来源：README.zh-CN.md:97-101。若依赖锁文件发生变化，建议同步锁定依赖：

```bash
uv sync --all-extras
```

来源：README.zh-CN.md:103-107。

## 附：作为 Python 库调用

除命令行形态外，本运行时还支持库式调用（9 种运行形态之一，F-017）。核心 API 位于根模块 `run_agent.py`（F-023）：

```python
from run_agent import AIAgent

# chat(self, message, stream_callback=None) -> str，run_agent.py:4019（F-023）
reply = agent.chat("你好")

# run_conversation(self, user_message, system_message=None,
#                  conversation_history=None, task_id=None)，run_agent.py:3996（F-023）
result = agent.run_conversation("总结今天的工作")
```

注意：`AIAgent.__init__` 本身是转发壳，真实初始化逻辑在 `agent.agent_init.init_agent`（F-021/F-024），构造参数较多（平台身份、回调、凭证池、迭代预算等），建议先阅读概念篇 [02-agent-core-loop](/concepts/02-agent-core-loop.md) 再集成。把 Agent 挂到消息平台长期运行的方式，见 [示例 02：网关与 Cron 实操](/examples/02-gateway-and-cron-usage.md)。若命令找不到，确认已激活 `.venv` 且当前在项目目录（入口名 `kylin-agent-runtime`，F-005）；需要重新配置时重跑 `kylin-agent-runtime setup`。

## 相关概念

- [00-overview](/concepts/00-overview.md)：项目定位、版本与 Hermes 血缘。
- [03-cli-and-tui](/concepts/03-cli-and-tui.md)：48 个 CLI 子命令与 TUI/Dashboard 启动链。
- [02-agent-core-loop](/concepts/02-agent-core-loop.md)：库式调用的对话环与初始化转发壳。
- [示例 02：网关与 Cron 实操](/examples/02-gateway-and-cron-usage.md)
