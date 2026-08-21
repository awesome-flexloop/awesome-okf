---
type: Reference
title: "启动脚本源码索引"
description: "Jupyter Docker Stacks 容器启动脚本源码信源登记（start.sh、start-notebook.py、run-hooks.sh等）"
tags: [startup, script, entrypoint, shell, python, hooks]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:source-grep", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - { id: src-start-sh, resource: "external/libs/jupyter/docker-stacks/images/docker-stacks-foundation/start.sh", title: "start.sh（ENTRYPOINT入口）" }
  - { id: src-run-hooks, resource: "external/libs/jupyter/docker-stacks/images/docker-stacks-foundation/run-hooks.sh", title: "run-hooks.sh（Hook执行器）" }
  - { id: src-fix-perm, resource: "external/libs/jupyter/docker-stacks/images/docker-stacks-foundation/fix-permissions", title: "fix-permissions（权限修复脚本）" }
  - { id: src-log, resource: "external/libs/jupyter/docker-stacks/images/docker-stacks-foundation/_docker_stacks_log.sh", title: "_docker_stacks_log.sh（日志工具）" }
  - { id: src-activate, resource: "external/libs/jupyter/docker-stacks/images/docker-stacks-foundation/10activate-conda-env.sh", title: "10activate-conda-env.sh（Conda激活Hook）" }
  - { id: src-start-nb-py, resource: "external/libs/jupyter/docker-stacks/images/base-notebook/start-notebook.py", title: "start-notebook.py（Notebook启动器）" }
  - { id: src-start-nb-sh, resource: "external/libs/jupyter/docker-stacks/images/base-notebook/start-notebook.sh", title: "start-notebook.sh（Bash shim）" }
  - { id: src-start-su, resource: "external/libs/jupyter/docker-stacks/images/base-notebook/start-singleuser.py", title: "start-singleuser.py（JupyterHub启动器）" }
  - { id: src-start-su-sh, resource: "external/libs/jupyter/docker-stacks/images/base-notebook/start-singleuser.sh", title: "start-singleuser.sh（Bash shim）" }
  - { id: src-healthcheck, resource: "external/libs/jupyter/docker-stacks/images/base-notebook/docker_healthcheck.py", title: "docker_healthcheck.py（健康检查）" }
  - { id: src-server-conf, resource: "external/libs/jupyter/docker-stacks/images/base-notebook/jupyter_server_config.py", title: "jupyter_server_config.py（服务器配置）" }
  - { id: src-condarc, resource: "external/libs/jupyter/docker-stacks/images/docker-stacks-foundation/initial-condarc", title: "initial-condarc（Conda配置）" }
---

# 启动脚本源码索引

本文档登记 Jupyter Docker Stacks 容器启动链路中所有脚本的源码路径与职责。

## 启动链路总览

```
tini (PID 1)
  └─ start.sh (ENTRYPOINT)
       ├─ [start-notebook.d/] hooks (以启动用户身份运行)
       ├─ root模式：用户重映射/授权/sudo配置
       │    └─ [before-notebook.d/] hooks (以root运行)
       └─ exec sudo → jovyan 用户
            └─ [before-notebook.d/] hooks (以jovyan运行)
                 └─ start-notebook.py (CMD)
                      ├─ 检测JUPYTERHUB_API_TOKEN → start-singleuser.py
                      └─ exec jupyter lab (默认)
```

## 脚本源码索引

| 脚本 | 位置 | 类型 | 职责 |
|------|------|------|------|
| start.sh | images/docker-stacks-foundation/ | Bash | ENTRYPOINT入口：用户重映射、权限管理、sudo授权、Hook调度、降权执行 |
| run-hooks.sh | images/docker-stacks-foundation/ | Bash | Hook执行器：source *.sh文件，执行可执行文件，容错继续 |
| _docker_stacks_log.sh | images/docker-stacks-foundation/ | Bash | 日志函数：_log_info/_log_warn/_log_error/_log_fatal |
| fix-permissions | images/docker-stacks-foundation/ | Bash | 权限修复：设置组写权限和setgid位，避免OverlayFS膨胀 |
| 10activate-conda-env.sh | images/docker-stacks-foundation/ | Bash | before-notebook.d Hook：激活conda base环境 |
| start-notebook.py | images/base-notebook/ | Python | CMD默认启动器：选择jupyter子命令、支持RESTARTABLE、传递NOTEBOOK_ARGS |
| start-notebook.sh | images/base-notebook/ | Bash | 兼容shim：打印警告后调用start-notebook.py |
| start-singleuser.py | images/base-notebook/ | Python | JupyterHub单用户服务器启动器 |
| start-singleuser.sh | images/base-notebook/ | Bash | 兼容shim |
| docker_healthcheck.py | images/base-notebook/ | Python | HEALTHCHECK：检查Jupyter Server是否响应 |
| jupyter_server_config.py | images/base-notebook/ | Python | Jupyter Server配置：监听地址、证书、umask、内联图形格式 |
| initial-condarc | images/docker-stacks-foundation/ | YAML | Conda初始配置 |

## Hook 目录

| 目录 | 创建位置 | 执行时机 | 执行身份 |
|------|---------|---------|---------|
| /usr/local/bin/start-notebook.d/ | Foundation层Dockerfile | start.sh早期（降权前） | 容器启动用户 |
| /usr/local/bin/before-notebook.d/ | Foundation层Dockerfile | 降权前后各执行一次 | root模式先root后jovyan；非root模式直接执行 |

## 关键环境变量

| 变量 | 默认值 | 作用 |
|------|-------|------|
| NB_USER | jovyan | 目标用户名 |
| NB_UID | 1000 | 目标用户UID |
| NB_GID | 100 | 目标用户GID(users组) |
| GRANT_SUDO | (无) | 设为1/yes授予无密码sudo |
| CHOWN_HOME | (无) | 设为1/yes执行chown home目录 |
| CHOWN_EXTRA | (无) | 逗号分隔额外chown路径 |
| RESTARTABLE | (无) | 设为yes使用run-one-constantly重启 |
| DOCKER_STACKS_JUPYTER_CMD | lab | Jupyter子命令(lab/notebook/server/retro等) |
| NOTEBOOK_ARGS | (无) | 额外传递给jupyter命令的参数 |
| JUPYTER_ENV_VARS_TO_UNSET | (无) | 降权时取消设置的环境变量（逗号分隔） |
| GEN_CERT | (无) | 设置则自动生成自签名SSL证书 |
| NB_UMASK | (无) | 设置Jupyter子进程umask（八进制） |
| JUPYTER_PORT | 8888 | Jupyter Server监听端口 |
| CONDA_DIR | /opt/conda | Conda安装目录 |
