---
type: Reference
title: 辅助模块源码信源
description: tljh/ 下辅助模块（utils, yaml, log, migrator, normalize, apt, user_creating_spawner）API 信源文档
tags: [reference, source, utilities, yaml, migrator, apt, spawner, api]
sources:
  - id: tljh-utils
    title: tljh/utils.py
  - id: tljh-yaml
    title: tljh/yaml.py
  - id: tljh-log
    title: tljh/log.py
  - id: tljh-migrator
    title: tljh/migrator.py
  - id: tljh-normalize
    title: tljh/normalize.py
  - id: tljh-apt
    title: tljh/apt.py
  - id: tljh-user-creating-spawner
    title: tljh/user_creating_spawner.py
---

# 辅助模块源码信源

## utils.py

### `run_subprocess(cmd, *args, **kwargs)`

执行子进程：
- 默认 stdout=PIPE, stderr=STDOUT
- 失败时 logger.error 输出命令和 stdout 并抛 CalledProcessError
- 成功时 logger.debug 输出

### `get_plugin_manager() → PluginManager`

每次创建新的 pluggy.PluginManager("tljh") 实例：
1. `pm.add_hookspecs(hooks)`
2. `pm.load_setuptools_entrypoints("tljh")`
3. 返回 pm

### `parse_version(version_string) → tuple`

使用正则 `\d+` 提取所有数字，返回 int 元组。例如 `"24.7.1-2"` → `(24, 7, 1, 2)`。用于版本号比较（类似 distutils.version.LooseVersion）。

## yaml.py

全局 `yaml` 对象：使用 `ruamel.yaml.YAML(typ="rt")`（round-trip 模式），配置了自定义 Composer 修复 ruamel.yaml issue #255（空容器的 flow_style 问题）。

### `_NoEmptyFlowComposer(Composer)`

自定义 Composer，重写 `compose_mapping_node` 和 `compose_sequence_node`：空映射/序列设置 flow_style=False。

## log.py

### `init_logging()`

配置 "tljh" logger：
1. 如果 INSTALL_PREFIX 不存在则创建目录
2. 如果已有 handlers 则直接返回（幂等）
3. 添加 FileHandler：`{INSTALL_PREFIX}/installer.log`，格式 `%(asctime)s %(message)s`
4. 添加 StreamHandler：stderr，格式 `%(message)s`
5. 日志级别 INFO

## migrator.py

### `migrate_file(old_path, new_path)`

迁移单个文件：
1. old_path 不存在则跳过
2. new_path 已存在时，移动到 `{new_path}.old.{YYYY-MM-DD}`（如存在则加序号 `.1`, `.2`...）
3. shutil.move 到 new_path

### `migrate_directory(old_dir, new_dir)`

递归迁移目录：
1. new_dir 存在时逐文件调用 migrate_file
2. new_dir 不存在时整体 shutil.move

### `migrate_config_files()`

迁移旧版配置路径：
- 旧 `config.yaml` → `CONFIG_DIR/config.yaml`
- 旧 `jupyterhub_config.d/` → `CONFIG_DIR/jupyterhub_config.d/`

## normalize.py

### `generate_system_username(username) → str`

生成符合 Linux 32 字符限制的系统用户名：
1. 长度 < 26：直接返回
2. 长度 ≥ 26：`{前26字符}-{sha256前5字符}`

## apt.py

### `trust_gpg_key(key)`

通过 stdin 执行 `apt-key add` 添加 GPG 密钥。如果 gpg2 不可用，先安装 gnupg2。

### `add_source(name, source_url, section)`

添加 APT 源：
1. 读取 `/etc/os-release` 获取 VERSION_CODENAME
2. 检查 `/etc/apt/sources.list.d/{name}.list` 是否已包含该源（避免重复）
3. 写入 `deb {source_url} {codename} {section}` 格式
4. 添加后执行 `apt-get update`

### `install_packages(packages)`

安装 APT 包：
1. `/var/lib/apt/lists` 为空时先 `apt-get update`
2. 设置 DEBIAN_FRONTEND=noninteractive
3. 执行 `apt-get install --yes packages`

## user_creating_spawner.py

### `UserCreatingSpawner(SystemdSpawner)`

继承 systemdspawner.SystemdSpawner，在 spawn 时自动创建系统用户：

**Traitlets**：
- `user_groups = Dict(key_trait=Unicode(), value_trait=List(Unicode()), config=True)`：用户组映射

**`start()` 方法**：
1. `generate_system_username("jupyter-" + self.user.name)` 生成系统用户名
2. 设置 `self.username_template`
3. `user.ensure_user(unix_username)` 创建系统用户
4. 将用户加入 jupyterhub-users 组
5. 管理员用户：加入 jupyterhub-admins 组，设置 `self.disable_user_sudo = False`
6. 普通用户：确保不在 jupyterhub-admins 组，设置 `self.disable_user_sudo = True`
7. 遍历 self.user_groups，将用户加入对应组
8. 调用 `super().start()` 启动服务器
