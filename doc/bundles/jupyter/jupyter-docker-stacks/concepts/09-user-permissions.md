---
type: Concept
title: "用户与权限模型"
description: "jovyan用户模型、UID/GID动态重映射、sudo授权机制、fix-permissions权限修复、容器安全模型"
tags: [permissions, user-model, jovyan, sudo, uid-gid, security, setgid]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - { id: src-foundation, resource: "/references/dockerfiles.md", title: "Foundation层用户创建" }
  - { id: src-start-sh, resource: "/references/startup-scripts.md", title: "start.sh权限逻辑" }
---

# 用户与权限模型

Jupyter Docker Stacks 采用**非root默认运行+root启动时动态重映射**的权限模型，兼顾安全性、灵活性和宿主机文件共享需求。

## 默认用户：jovyan

所有镜像默认创建一个名为 `jovyan` 的用户：

| 属性 | 默认值 | 说明 |
|------|-------|------|
| 用户名 | jovyan | Jupyter社区传统用户名（"木星居民"） |
| UID | 1000 | Ubuntu系统第一个普通用户UID |
| GID | 100 | users组（Ubuntu系统默认用户组） |
| Home目录 | /home/jovyan | 用户主目录 |
| Shell | /bin/bash | 默认shell |
| Conda目录 | /opt/conda（组可写） | 系统级Conda安装 |

jovyan用户通过`useradd --no-user-group`创建，加入users组（GID 100），不创建同名的私有用户组。

## 为什么默认以root启动？

这是Jupyter Docker Stacks最常被误解的设计决策。容器的ENTRYPOINT（start.sh）需要在root权限下执行以下操作，然后才降权到jovyan：

1. **UID/GID动态重映射**：让容器内jovyan的UID/GID匹配宿主机挂载目录的所有者，避免权限问题
2. **可选sudo授权**：通过GRANT_SUDO=yes授予无密码sudo
3. **目录chown**：CHOWN_HOME/CHOWN_EXTRA指定的目录需要root权限修改所有者
4. **系统级Hook**：start-notebook.d hooks可能需要root权限

执行完这些操作后，start.sh通过`sudo --preserve-env --set-home --user jovyan`降权执行CMD。最终Jupyter Server以jovyan身份运行。

> 如果你不需要上述任何功能（即不需要动态UID映射、sudo、chown），可以直接用`--user 1000`或`--user jovyan`启动，跳过root启动流程。

## UID/GID动态重映射

当以root启动容器时，start.sh会根据环境变量动态调整用户身份：

### 用户名重映射（NB_USER）

```bash
# 如果 NB_USER != "jovyan"，重命名用户
if id jovyan &>/dev/null; then
    usermod --home "/home/${NB_USER}" --login "${NB_USER}" jovyan
fi
```

NB_USER改变时：
- jovyan用户被重命名为NB_USER
- /home/jovyan被复制到/home/${NB_USER}（如果不存在）
- 复制失败则尝试创建符号链接
- 当前工作目录如果在旧home下，自动切换到新路径

### UID/GID重映射（NB_UID/NB_GID）

```bash
if [ "${NB_UID}" != "$(id -u "${NB_USER}")" ] || [ "${NB_GID}" != "$(id -g "${NB_USER}")" ]; then
    groupadd --force --gid "${NB_GID}" --non-unique "${NB_GROUP:-${NB_USER}}"
    userdel "${NB_USER}"
    useradd --no-log-init --home "/home/${NB_USER}" --shell /bin/bash \
        --uid "${NB_UID}" --gid "${NB_GID}" --groups 100 "${NB_USER}"
fi
```

UID/GID不匹配时：
1. 确保目标GID的组存在（`groupadd --force --non-unique`允许多个组共享同一GID）
2. 删除旧用户
3. 创建新用户，指定UID/GID，并加入users组（GID 100）

### 典型用法：匹配宿主机UID

```bash
# 让容器内jovyan的UID匹配当前宿主机用户，解决挂载目录权限问题
docker run -it --rm \
    -p 8888:8888 \
    -e NB_UID=$(id -u) \
    -e NB_GID=$(id -g) \
    -v "${PWD}":/home/jovyan/work \
    quay.io/jupyter/base-notebook
```

这样容器内创建的文件在宿主机上属于当前用户，不会产生权限混乱。

### root用户特殊处理

当`NB_USER=root`且`NB_UID=0`时（即容器以root身份运行Jupyter），start.sh会特殊处理：
- 修改/etc/passwd中root的home目录为/home/root
- 复制home目录时使用`--no-preserve=ownership`
- 直接exec CMD（不通过sudo降权）

> 不推荐以root身份运行Jupyter Server，这是安全反模式。仅在特殊场景下使用。

## Sudo授权机制

默认情况下，jovyan用户**没有**sudo权限。Foundation层的Dockerfile特意禁用了默认的sudo组权限：

```dockerfile
RUN echo "auth requisite pam_deny.so" >> /etc/pam.d/su && \
    sed -i.bak -e 's/^%admin/#%admin/' /etc/sudoers && \
    sed -i.bak -e 's/^%sudo/#%sudo/' /etc/sudoers
```

要授予sudo权限，必须在启动时设置环境变量并以root启动：

```bash
docker run -it --rm \
    -p 8888:8888 \
    -e GRANT_SUDO=yes \
    --user root \
    quay.io/jupyter/base-notebook
```

此时start.sh会创建`/etc/sudoers.d/added-by-start-script`：

```bash
echo "${NB_USER} ALL=(ALL) NOPASSWD:ALL" >/etc/sudoers.d/added-by-start-script
```

这授予jovyan**无密码**sudo权限。在容器内可以执行：
```bash
sudo apt-get update
sudo apt-get install -y some-package
```

> 安全提示：GRANT_SUDO=yes降低了容器安全性，仅在可信环境中使用。

## 目录权限控制

### CHOWN_HOME

```bash
-e CHOWN_HOME=yes
```

将/home/${NB_USER}目录的所有者递归设为NB_UID:NB_GID。当挂载了宿主机目录且UID不匹配时有用。

> 注意：对挂载的宿主机目录执行chown -R会修改宿主机文件的所有者！在共享机器上谨慎使用。

### CHOWN_HOME_OPTS

传递给chown的额外参数，如`-R`（递归）。

### CHOWN_EXTRA

逗号分隔的额外chown路径：

```bash
-e CHOWN_EXTRA=/data,/shared
-e CHOWN_EXTRA_OPTS=-R
```

### secure_path配置

start.sh将conda路径添加到sudo secure_path：

```bash
sed -r "s#Defaults\s+secure_path\s*=\s*\"?([^\"]+)\"?#Defaults secure_path=\"${CONDA_DIR}/bin:\1\"#" \
    /etc/sudoers | grep secure_path >/etc/sudoers.d/path
```

确保sudo执行的命令能找到conda安装的python/jupyter等。

## fix-permissions 脚本

fix-permissions是所有镜像中频繁使用的权限修复工具，其设计对Docker镜像体积优化至关重要：

```bash
for d in "$@"; do
    find "${d}" \
        ! \( -group "${NB_GID}" -a -perm -g+rwX \) \
        -exec chgrp "${NB_GID}" -- {} \+ \
        -exec chmod g+rwX -- {} \+
    find "${d}" \
        -type d \
        ! -perm -g+s \
        -exec chmod g+s -- {} \+
done
```

### 关键设计原则

1. **条件修改**：使用`! \( -group "${NB_GID}" -a -perm -g+rwX \)`跳过已经正确设置权限的文件。盲目`chmod -R`会触发OverlayFS的Copy-on-Write，将所有文件复制到可写层，导致镜像体积暴增。

2. **SetGID位**：对目录设置setgid位（`chmod g+s`），确保在该目录下新建的文件/子目录自动继承users组（而不是创建者的主组），实现组内共享。

3. **大写X权限**：`g+rwX`中的大写`X`表示"仅在文件是目录或已有执行权限时添加执行权限"，避免给普通数据文件添加不必要的执行位。

### 何时使用fix-permissions

每次mamba/pip安装软件包或修改/home/jovyan后，都应该运行fix-permissions：

```dockerfile
RUN mamba install --yes some-package && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"
```

这确保：
- Conda目录下的文件对users组可读写
- 用户home下的文件对users组可读写
- 新建文件自动继承组权限

## Conda目录权限

Conda安装在`/opt/conda`（系统级目录），初始所有者为jovyan:users，组可写。这是因为：
- conda/mamba安装包时需要写权限
- jovyan用户通过组权限可以安装/更新包
- 配合fix-permissions和setgid位，所有conda文件保持组可写

## 非root启动的限制

使用`--user $(id -u)`或`--user 1000`启动时，start.sh的root路径不执行，以下功能不可用：

| 功能 | root启动 | 非root启动 |
|------|---------|-----------|
| NB_USER重命名 | ✅ | ❌（警告） |
| NB_UID/GID重映射 | ✅ | ❌（警告） |
| GRANT_SUDO | ✅ | ❌（警告） |
| CHOWN_HOME | ✅ | ❌ |
| CHOWN_EXTRA | ✅ | ❌ |
| /etc/passwd修复 | N/A | ⚠️ 尝试修复（需要/etc/passwd组可写） |

非root启动时，如果UID在/etc/passwd中没有条目，start.sh会尝试添加：

```bash
if ! whoami &>/dev/null; then
    if [[ -w /etc/passwd ]]; then
        sed --expression="s/^jovyan:/nayvoj:/" /etc/passwd >/tmp/passwd
        echo "${NB_USER}:x:$(id -u):$(id -g):,,,:/home/jovyan:/bin/bash" >>/tmp/passwd
        cat /tmp/passwd >/etc/passwd
        rm /tmp/passwd
    fi
fi
```

这依赖Foundation层设置的`chmod g+w /etc/passwd`。

## JUPYTER_ENV_VARS_TO_UNSET

降权时可以通过此环境变量取消设置敏感环境变量：

```bash
-e JUPYTER_ENV_VARS_TO_UNSET=AWS_SECRET_ACCESS_KEY,DB_PASSWORD
```

这些变量在root阶段设置（如用于下载数据），但不会传递给降权后的Jupyter进程。

## 相关概念

- [启动生命周期](07-startup-lifecycle.md)
- [Hook扩展与自定义](08-hooks-and-customization.md)
- [Foundation层详解](03-foundation-layer.md)
