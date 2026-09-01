---
type: Reference
title: user.py 源码信源
description: tljh/user.py 模块公共 API 信源文档
tags: [reference, source, user, system-user, group, permissions, api]
sources:
  - id: tljh-user
    title: tljh/user.py
---

# user.py 源码信源

> Linux 系统用户和组管理模块。负责创建/删除系统用户、管理用户组成员关系。

## 公共函数

### `ensure_user(username)`

确保系统用户存在：
1. 尝试 `pwd.getpwnam(username)` 检查用户是否已存在，存在则直接返回
2. 不存在则执行 `useradd --create-home {username}` 创建用户及主目录
3. `chmod o-rwx {homedir}` 保护用户主目录（其他用户无法读取）
4. 调用 `tljh_new_user_create` 插件钩子

### `remove_user(username)`

删除系统用户：
1. 检查用户是否存在
2. 存在则执行 `deluser --quiet {username}`

### `ensure_group(groupname)`

确保用户组存在：
1. 执行 `groupadd --force {groupname}`（已存在不报错）

### `remove_group(groupname)`

删除用户组：
1. 检查组是否存在（grp.getgrnam）
2. 存在则执行 `delgroup --quiet {groupname}`（仅当无成员时成功）

### `ensure_user_group(username, groupname)`

确保用户属于指定组：
1. 通过 `grp.getgrnam` 获取组信息
2. 检查用户是否已在组成员列表中
3. 不在则执行 `gpasswd --add {username} {groupname}`

### `remove_user_group(username, groupname)`

从指定组中移除用户：
1. 检查用户是否在组中
2. 在则执行 `gpasswd --delete {username} {groupname}`

## 依赖

- Python 标准库：pwd, grp, shutil, os, os.path, subprocess
- tljh.utils.run_subprocess
- tljh.utils.get_plugin_manager（用于调用 tljh_new_user_create 钩子）
