---
type: Concept
title: "启动生命周期"
description: "容器从docker run到Jupyter Server就绪的完整启动链路：tini→start.sh→hooks→降权→start-notebook.py"
tags: [startup, lifecycle, entrypoint, tini, hook-execution]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - { id: src-start-sh, resource: "/references/startup-scripts.md", title: "start.sh启动脚本" }
  - { id: src-start-nb, resource: "/references/startup-scripts.md", title: "start-notebook.py" }
---

# 启动生命周期

理解 Jupyter Docker Stacks 容器的启动链路，是排查启动问题、自定义容器行为的关键。本章详细解析从 `docker run` 到 Jupyter Server 就绪的完整流程。

## 启动链路总览

```
docker run [OPTIONS] IMAGE [CMD]
  │
  ▼
Docker 创建容器，设置 ENTRYPOINT + CMD
  │
  ▼
tini -g -- start.sh          ← PID 1（ENTRYPOINT，Foundation层）
  │
  ├─ 加载日志函数 (_docker_stacks_log.sh)
  ├─ 解析命令（无CMD则默认bash）
  │
  ├─ ▶ run-hooks.sh /usr/local/bin/start-notebook.d/
  │     （以容器启动用户身份运行，通常是root）
  │
  ├─ 判断：是否以root启动？(id -u == 0)
  │     │
  │     ├─ 是（root模式，默认docker run行为）：
  │     │    ├─ 用户重映射（jovyan→NB_USER，UID/GID调整）
  │     │    ├─ Home目录迁移/符号链接
  │     │    ├─ CHOWN_HOME/CHOWN_EXTRA目录权限
  │     │    ├─ 配置sudo secure_path
  │     │    ├─ GRANT_SUDO→无密码sudo
  │     │    ├─ ▶ run-hooks.sh /usr/local/bin/before-notebook.d/ （root身份）
  │     │    ├─ unset_explicit_env_vars()
  │     │    └─ exec sudo --preserve-env --set-home --user NB_USER CMD
  │     │         │
  │     │         ▼
  │     │    降权到jovyan用户后：
  │     │    └─ ▶ run-hooks.sh /usr/local/bin/before-notebook.d/ （jovyan身份）
  │     │         └─ 10activate-conda-env.sh（激活conda base）
  │     │              └─ exec CMD
  │     │
  │     └─ 否（非root模式，--user指定）：
  │          ├─ 警告：GRANT_SUDO需要root启动
  │          ├─ 修复/etc/passwd中UID条目（如果缺失）
  │          ├─ 警告：无法修改NB_USER/NB_UID/NB_GID
  │          ├─ ▶ run-hooks.sh /usr/local/bin/before-notebook.d/
  │          └─ exec CMD
  │
  ▼
CMD = start-notebook.py        ← Base Notebook层
  │
  ├─ 检测 JUPYTERHUB_API_TOKEN → exec start-singleuser.py
  │
  ├─ RESTARTABLE=yes? → 包装为 run-one-constantly
  │
  ├─ 构建命令：jupyter ${DOCKER_STACKS_JUPYTER_CMD} ${NOTEBOOK_ARGS} $@
  │
  └─ os.execvp("jupyter", ["jupyter", "lab", ...])
       │
       ▼
  Jupyter Server 启动，监听8888端口
       │
       ▼
  HEALTHCHECK 通过 /etc/jupyter/docker_healthcheck.py 就绪
```

## 第一阶段：tini 初始化

tini 作为 PID 1 进程，负责：
- **僵尸进程回收**：Jupyter内核可能产生子进程，tini确保这些子进程被正确回收
- **信号转发**：将docker stop发送的SIGTERM转发给Jupyter Server，实现优雅关闭
- 使用 `-g` 参数（进程组模式），确保信号发送到整个进程组

## 第二阶段：start.sh 执行

start.sh 是 ENTRYPOINT 的核心，它的行为因启动用户不同而分为两条路径。

### 默认路径（root启动，`docker run` 默认行为）

当以root启动容器时（不加`--user`参数），start.sh 执行以下步骤：

**Step 1：start-notebook.d hooks**

这是第一批执行的hook，以root身份运行（在用户重映射之前）。通常用于：
- 系统级配置
- 需要root权限的初始化操作

**Step 2：用户重映射**

start.sh 支持动态修改jovyan用户以匹配主机环境：

1. **用户名重映射**：如果`NB_USER != "jovyan"`，将jovyan用户重命名为NB_USER
2. **UID/GID调整**：如果`NB_UID != 1000`或`NB_GID != 100`，重建用户：
   - 确保目标组存在（`groupadd --force`）
   - 删除旧用户，创建新用户并指定UID/GID
   - 将新用户加入users组（GID 100）
3. **Home目录迁移**：如果用户名改变，将/home/jovyan复制或符号链接到/home/${NB_USER}
4. **工作目录更新**：如果PWD在旧home下，切换到新home对应路径

**Step 3：目录权限修复**

- `CHOWN_HOME=yes`：chown用户home目录
- `CHOWN_EXTRA`：chown指定的额外路径（逗号分隔）
- 支持`CHOWN_HOME_OPTS`和`CHOWN_EXTRA_OPTS`传递额外chown参数

**Step 4：Sudo配置**

- 将`${CONDA_DIR}/bin`添加到sudo secure_path
- 如果`GRANT_SUDO=yes`，写入`/etc/sudoers.d/added-by-start-script`授予无密码sudo

**Step 5：before-notebook.d hooks（root身份）**

在降权前执行root级别的hook（如系统级配置）。

**Step 6：取消设置敏感环境变量**

`unset_explicit_env_vars()` 取消设置`JUPYTER_ENV_VARS_TO_UNSET`中列出的环境变量（逗号分隔）。这在从root降权到jovyan时使用，防止敏感环境变量泄漏。

**Step 7：降权执行**

```bash
exec sudo --preserve-env --set-home --user "${NB_USER}" \
    LD_LIBRARY_PATH="${LD_LIBRARY_PATH}" \
    PATH="${PATH}" \
    PYTHONPATH="${PYTHONPATH:-}" \
    "${cmd[@]}"
```

使用sudo切换到NB_USER，但显式保留`LD_LIBRARY_PATH`、`PATH`、`PYTHONPATH`环境变量。

> **为什么用sudo而不是su或直接setuid？** sudo的`--preserve-env`标志可以精细控制环境变量传递，配合`/etc/sudoers.d/path`中设置的secure_path，确保conda环境路径可用。

### 非root路径（`--user` 启动）

当使用`--user $(id -u):$(id -g)`或`--user 1000`启动容器时：

1. **/etc/passwd修复**：如果当前UID在/etc/passwd中没有条目（常见于`--user`指定任意UID），start.sh会尝试添加条目（需要/etc/passwd组可写）
2. **无法修改用户**：NB_USER/NB_UID/NB_GID修改需要root权限，非root启动时这些设置被忽略并打印警告
3. **Sudo不可用**：GRANT_SUDO需要root权限
4. **Home目录权限警告**：如果/home/jovyan不可写，建议使用`--group-add=users`
5. **直接执行**before-notebook.d hooks和CMD，无降权过程

## 第三阶段：before-notebook.d hooks（jovyan身份）

降权后，以jovyan用户身份再次执行before-notebook.d hooks（与root身份执行的是同一目录，但执行身份不同）。

默认包含的hook：
- **10activate-conda-env.sh**：执行`eval "$(micromamba activate base)"`或等价的conda激活命令，确保conda环境在shell中可用

用户可以通过挂载或自定义镜像向这两个目录添加脚本：
- `/usr/local/bin/start-notebook.d/`：在用户重映射之前执行（始终以启动用户身份）
- `/usr/local/bin/before-notebook.d/`：在降权前后各执行一次

## 第四阶段：start-notebook.py

### JupyterHub检测

```python
if "JUPYTERHUB_API_TOKEN" in os.environ:
    os.execvp("/usr/local/bin/start-singleuser.py", ...)
```

JupyterHub通过设置`JUPYTERHUB_API_TOKEN`环境变量标识Hub管理的会话，此时自动切换到start-singleuser.py，该脚本配置Jupyter Server以Hub单用户模式运行。

### RESTARTABLE模式

```python
if os.environ.get("RESTARTABLE") == "yes":
    command.append("run-one-constantly")
```

`run-one-constantly`是Ubuntu `run-one`包提供的工具，它会在命令退出后自动重新启动，实现Jupyter Server崩溃自愈。

### Jupyter子命令选择

```python
jupyter_command = os.environ.get("DOCKER_STACKS_JUPYTER_CMD", "lab")
command.append(jupyter_command)
```

默认是`lab`（JupyterLab），可通过环境变量切换。

### 参数传递

1. `NOTEBOOK_ARGS`环境变量：通过`shlex.split()`正确分割为参数列表
2. 命令行参数（`sys.argv[1:]`）：直接追加
3. 这些参数最终传递给`jupyter <subcommand>`

### 进程替换

`os.execvp(command[0], command)` 使用exec系统调用替换当前进程——start-notebook.py进程被jupyter进程替换，不会产生额外进程。这也是为什么tini需要作为PID 1来管理信号。

## 第五阶段：Jupyter Server 就绪

1. Jupyter Server启动，绑定到0.0.0.0:8888
2. 如果设置了`GEN_CERT`，使用自签名证书启用HTTPS
3. 输出启动日志，包含认证token的URL
4. HEALTHCHECK开始通过HTTP探测（间隔3秒），连续3次失败标记为unhealthy

## 启动时序关键节点

| 时间点 | 事件 | 典型耗时 |
|--------|------|---------|
| T+0 | docker run 命令执行 | 0s |
| T+0.1s | tini启动，start.sh开始执行 | <0.1s |
| T+0.2s | start-notebook.d hooks执行 | <0.5s |
| T+0.5s | root模式：用户重映射 | <0.5s |
| T+1s | 降权到jovyan | <0.1s |
| T+1s | before-notebook.d hooks | <0.5s |
| T+1.5s | start-notebook.py执行 | <0.1s |
| T+1.5s | jupyter lab进程启动 | <0.1s |
| T+3-5s | Jupyter Server监听8888 | 2-4s（Python导入） |
| T+6s | HEALTHCHECK首次通过 | 启动后3s开始探测 |

## 相关概念

- [Hook扩展与自定义](08-hooks-and-customization.md)
- [用户与权限模型](09-user-permissions.md)
- [Base Notebook层详解](04-base-notebook.md)
