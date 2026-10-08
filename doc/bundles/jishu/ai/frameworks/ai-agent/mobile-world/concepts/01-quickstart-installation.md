---
type: Concept
title: "快速开始：环境变量、首个容器与 Windows/WSL/KVM 前置"
description: ".env 六变量与 env check 校验规则、env run 启动首个容器的四组起始端口、Windows 宿主的 WSL/KVM/nestedVirtualization 前置条件"
tags: [MobileWorld, 快速开始, Docker, WSL, KVM, 环境变量]
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

# 快速开始：环境变量、首个容器与 Windows/WSL/KVM 前置

MobileWorld 的最小可用路径是三步：配好 `.env` 六个变量 → 通过 `env check` 校验 → `env run` 拉起第一个评测容器。Windows 宿主还需要先完成 WSL/KVM 前置配置，因为容器内的 Android 模拟器依赖嵌套虚拟化。

## 前置条件：Windows/WSL/KVM

Windows 宿主按 `docs/setup_for_windows.md` 要求（F-080）：

```powershell
wsl --install
sudo usermod -a -G kvm ${USER}
```

并在 `/etc/wsl.conf` 中添加：

```ini
[boot]
command = /bin/bash -c 'chown -v root:kvm /dev/kvm && chmod 660 /dev/kvm'

[wsl2]
nestedVirtualization = true
```

`nestedVirtualization = true` 是关键：容器方案是 Docker-in-Docker 里再跑 Android 模拟器的三层虚拟化（F-067、F-068），没有嵌套虚拟化，模拟器无法启动。

## 配置 .env 六个变量

`.env.example` 定义了共 6 个变量（F-005）：

| 变量 | 用途 |
|---|---|
| `API_KEY` | agent 模型密钥 |
| `DASHSCOPE_API_KEY` | MCP 用（DashScope 提供商） |
| `MODELSCOPE_API_KEY` | MCP 用（ModelScope 提供商） |
| `USER_AGENT_API_KEY` | 用户代理 LLM 密钥 |
| `USER_AGENT_BASE_URL` | 用户代理 LLM 服务地址 |
| `USER_AGENT_MODEL` | 用户代理模型名（示例值 `gpt-4.1`） |

`env run` 会把宿主 `.env` 挂载为容器内 `/app/service/.env`（F-024），容器内的 server 进程因此能读到这些密钥。

## env check：启动前校验

`mw env check` 的 `_check_env_file()` 检查 `.env` 是否缺失或仍为占位符（F-025）。占位符字面量包括：

```
API_KEY="your_api_key_for_agent_model"
DASHSCOPE_API_KEY="dashscope_api_key_for_mcp"
MODELSCOPE_API_KEY="modelscope_api_key_for_mcp"
USER_AGENT_API_KEY="your_user_agent_llm_api_key"
USER_AGENT_BASE_URL="your_user_agent_base_url"
```

判定规则（F-025）：`API_KEY` 缺失/占位为 **issue**（阻断项），MCP 与 `USER_AGENT_*` 键缺失为 **warning**（仅提示）。也就是说，只跑纯 GUI 评测可以不配 MCP/用户代理密钥；启用 `--enable-mcp` 或 `--enable-user-interaction` 时必须补齐。

## 启动第一个容器

```bash
sudo mw env run
```

`env run` 的默认参数（F-024）：

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--backend-start-port` | 6800 | FastAPI 控制服务端口 |
| `--viewer-start-port` | 7860 | 设备查看器端口 |
| `--vnc-start-port` | 5800 | VNC 端口 |
| `--adb-start-port` | 5556 | ADB 中继端口 |
| `--count` | 1 | 容器数量 |
| `--launch-interval` | 10 | 多容器启动间隔（秒） |

四组端口从各自起始值递增分配，多容器（`--count N`）时第 i 个容器依次占用各组的第 i 个端口。`env` 下共 8 个子动作：`run/rm/list(ls)/info/restart/exec/check`（F-024）。

两个常用选项（F-024）：

- `--dev`：只允许单容器（count>1 时直接 `sys.exit(1)`），额外把本地 `src/` 挂载到 `/app/service/src`，便于改代码调试（F-077）。
- `--http-proxy`：配置代理时说明 "10.0.2.2/127.0.0.1/localhost are always excluded"——这三类地址始终直连（F-024，容器内由 proxy_chain 落实，见 `/concepts/07-docker-environment.md`）。

启动后容器内的服务拓扑：控制服务监听 6800（F-068 第⑨步 `uv run mobile-world server --port 6800`），ADB 经 socat 中继暴露在 5556（F-068 第⑧步），镜像 `HEALTHCHECK` 直通 `http://localhost:6800/health`（F-067）。

## 重启与调试

`mw env restart <container_name>` 重启容器内服务：交互模式执行 `cd /app/service && uv run mobile-world server --port 6800 --enable-mcp`，非交互调用 `restart_server_in_container(container_name, detach=True, enable_mcp=True)`（F-026）。dev 模式下容器内日志查看 `tail -f /app/service/logs/server.log`，测试 `cd /app/service && uv run pytest`（F-077）。

## 相关概念

- [/concepts/07-docker-environment.md](/concepts/07-docker-environment.md)——容器内部十步启动序列与 DinD 镜像分层
- [/concepts/02-architecture-layers.md](/concepts/02-architecture-layers.md)——env 子命令在 CLI 全家福中的位置
- [/examples/02-customize-avd-snapshot.md](/examples/02-customize-avd-snapshot.md)——基于 dev 容器的快照定制实操
