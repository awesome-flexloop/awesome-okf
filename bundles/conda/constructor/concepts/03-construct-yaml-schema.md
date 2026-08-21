---
type: concept
title: "construct.yaml 配置规范"
description: "construct.yaml 的完整字段说明、Selector 语法、Jinja2 模板支持、JSON Schema 校验机制，以及 Pydantic 模型到 YAML 的映射。"
tags: [construct.yaml, 配置, Schema, Pydantic, Selector, Jinja2, 字段参考]
status: stable
stale_after: 2027-12-31
level: intermediate
prerequisites: ["00-introduction", "01-getting-started"]
reading_time: 18
generated: { by: "concept_agent/trae-cn", at: "2026-08-21T00:00:00Z" }
sources:
  - id: constructor-schema
    resource: "constructor/_schema.py"
  - id: constructor-construct
    resource: "constructor/construct.py"
---

# construct.yaml 配置规范

`construct.yaml` 是 constructor 的唯一输入配置文件，采用 YAML 格式，支持 Selector 条件注释和 Jinja2 模板。constructor 在解析阶段对其进行 JSON Schema 校验，确保配置合规。

## 解析流程

construct.yaml 的解析分为四步：

1. **Selector 行过滤**：处理 `# [condition]` 条件注释，保留匹配当前平台的行
2. **Jinja2 渲染**（可选）：如果 YAML 中包含 `{{` 或 `{%`，通过 Jinja2 渲染
3. **YAML 加载**：使用 ruamel.yaml 解析为 Python 字典
4. **Schema 校验**：通过 JSON Schema (Draft 2020-12) + Pydantic 模型双重校验

## Selector 语法

Selector 是行尾条件注释，用于指定配置项仅在特定平台生效：

```yaml
welcome_image: img/win.bmp      # [win]
welcome_image: img/mac.png      # [osx]
specs:
  - python
  - pywin32                     # [win]
  - pyobjc                      # [osx]
```

### 可用 Selector 变量

| 变量 | 匹配平台 |
|------|---------|
| `linux` | 所有 Linux |
| `linux32` / `linux64` / `aarch64` / `ppc64le` / `s390x` / `armv7l` | 特定 Linux 架构 |
| `osx` | 所有 macOS |
| `arm64` | macOS Apple Silicon |
| `win` | 所有 Windows |
| `win32` / `win64` / `win_arm64` | 特定 Windows 架构 |
| `x86` / `x86_64` | x86/x86_64 架构 |
| `unix` | Linux + macOS |

支持逻辑运算：`# [linux64 or osx]`、`# [win and not win_arm64]`

## Jinja2 模板支持

当 YAML 中包含 Jinja2 语法（`{{ }}` 或 `{% %}`）时，constructor 使用 Jinja2 渲染。可用的全局变量：

- `environ`：操作系统环境变量字典
- `os`：Python `os` 模块

```yaml
name: {{ environ.get("INSTALLER_NAME", "myenv") }}
version: "1.0"
channels:
  - {{ environ.get("CONDA_CHANNEL", "conda-forge") }}
specs:
  - python {{ os.environ.get("PY_VER", "3.14.*") }}
```

模板加载器 `FilteredLoader` 在加载模板时会自动应用 Selector 过滤，因此模板中也可以使用 selectors。

## 完整字段参考

字段按功能分组如下（来源：[`ConstructorConfiguration` Pydantic 模型](../references/construct-schema.md)）。

### 基本标识

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `$schema` | string | 否 | `https://schemas.conda.org/constructor/v0/construct.schema.json` | JSON Schema URL/路径 |
| `name` | string | ✅ | — | 安装程序名称，正则 `^[a-zA-Z0-9_][\w.-]*$` |
| `version` | string | ✅ | — | 版本号，同 name 的正则约束 |
| `company` | string | 否 | `None` | 公司/组织名称 |
| `reverse_domain_identifier` | string | 否 | 自动生成 | 反向域名标识符（MSI/PKG用），如 `io.continuum.mypython` |

### 通道与包配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `channels` | list\<string\> | `[]` | conda 通道 URL 列表（优先级从高到低） |
| `channels_remap` | list\<ChannelRemap\> | `[]` | 构建通道→安装后通道映射（见下文） |
| `mirrored_channels` | dict | `{}` | 通道镜像 URL 映射（需要 mamba） |
| `specs` | list\<string\> \| string | `[]` | 包规格列表，或 requirements.txt 路径 |
| `user_requested_specs` | list\<string\> | 同 `specs` | 记录为"用户请求"的包（影响后续 conda 行为） |
| `virtual_specs` | list\<string\> | `[]` | 虚拟包约束，如 `__glibc>=2.24`、`__osx>=11` |
| `exclude` | list\<string\> | `[]` | 排除的包名列表 |
| `menu_packages` | list\<string\> \| `null` | `null` | 创建开始菜单快捷方式的包（空列表禁用快捷方式） |
| `environment` | string | `None` | 从已有环境名构建（忽略 specs） |
| `environment_file` | string | `None` | 从 environment.yml/txt 构建 |
| `transmute_file_type` | `".conda"` \| `null` | `None` | 将包转换为 `.conda` 格式 |
| `ignore_duplicate_files` | bool | `True` | 跨包重复文件时仅警告（`False`为报错） |

> **注意**：`channels` 和 `channels_remap` 至少必须提供一个。`specs`、`environment`、`environment_file` 三选一。

#### channels_remap 详解

`channels_remap` 允许构建时和安装后使用不同的通道：

```yaml
channels_remap:
  - src: file:///D:/internal/conda-bld   # 构建时使用本地通道
    dest: https://repo.anaconda.com/pkgs/main  # 安装后显示为公共通道
```

典型用途：
- 企业内网构建时使用内部镜像/本地通道，安装后配置为公共通道
- 构建时包含私有包但不在用户端暴露私有通道 URL

### 多环境配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `extra_envs` | dict\<string, ExtraEnv\> | `{}` | 额外环境配置，键为环境名 |
| `register_envs` | bool | `True` | 是否在 `~/.conda/environments.txt` 注册环境 |

`extra_envs` 的每个值是 `ExtraEnv` 模型，支持以下子字段：

| 子字段 | 类型 | 说明 |
|--------|------|------|
| `specs` | list\<string\> | 环境包规格 |
| `channels` | list\<string\> | 环境专属通道（继承全局 channels） |
| `exclude` | list\<string\> | 环境专属排除列表（覆盖全局 exclude，空列表覆盖全局为空） |
| `environment` | string | 从已有环境复制 |
| `environment_file` | string | 从 environment 文件创建 |
| `menu_packages` | list\<string\> \| `null` | 该环境的菜单包 |
| `user_requested_specs` | list\<string\> | 用户请求规格 |
| `freeze_env` | dict \| `null` | Frozen 标记（CEP-22），同 `freeze_base` |

```yaml
extra_envs:
  datascience:
    specs:
      - numpy
      - pandas
      - jupyter
    channels:
      - conda-forge
```

> 当使用 `extra_envs` 时，`ignore_duplicate_files` 强制为 `True`，且 base 环境必须包含 `conda`。

### 安装程序类型与输出

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `installer_type` | InstallerTypes \| list | 平台默认 | 安装程序类型：`sh`/`pkg`/`exe`/`msi`/`docker`/`all` |
| `installer_filename` | string | 自动生成 | 自定义输出文件名 |
| `installer_filename_suffix` | string | 自动生成 | 文件名后缀 |

### conda 配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `write_condarc` | bool | `False` | 是否写入 `.condarc` 文件 |
| `condarc` | string \| dict | `None` | 直接指定 `.condarc` 内容（覆盖其他 condarc 选项） |
| `conda_default_channels` | list\<string\> | `[]` | `.condarc` 中的 default_channels |
| `conda_channel_alias` | string | `None` | `.condarc` 中的 channel_alias |
| `initialize_conda` | CondaInitialization \| bool | `True` | 是否提供 conda init 选项：`classic`/`condabin`/`False` |
| `initialize_by_default` | bool | 平台相关 | conda init 默认选中状态 |
| `freeze_base` | dict | `None` | 保护 base 环境不被修改（CEP-22 frozen标记） |

### 安装路径与行为

| 字段 | 类型 | 默认值 | 平台 | 说明 |
|------|------|--------|------|------|
| `default_prefix` | string | 平台默认 | 所有 | 默认安装路径 |
| `default_prefix_domain_user` | string | `%LOCALAPPDATA%\<name>` | Win | 域用户默认路径 |
| `default_prefix_all_users` | string | `%ALLUSERSPROFILE%\<name>` | Win | 所有用户安装默认路径 |
| `default_location_pkg` | string | `None` | macOS | PKG 安装子目录 |
| `pkg_domains` | dict | `enable_anywhere:true, enable_currentUserHome:true` | macOS | PKG 安装域 |
| `batch_mode` | bool | `False` | SH | 默认批处理模式（无交互） |
| `keep_pkgs` | bool | `False` | 所有 | 保留包缓存 |
| `check_path_spaces` | bool | `True` | 所有 | 检查路径是否含空格 |
| `pkg_name` | string | 同 `name` | macOS | PKG 内部标识符 |
| `install_path_exists_error_text` | string | 默认消息 | macOS | 路径已存在时的错误提示 |
| `progress_notifications` | bool | `False` | macOS | PKG 进度通知 |

### 许可与法律

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `license_file` | string | `None` | 许可证文件路径（.txt/.rtf/.html） |
| `license_ecosystem` | list | `[]` | 额外许可证采集的包生态系统（如 pypi/npm） |

### 自定义脚本

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `pre_install` | string | `None` | 安装前脚本路径 |
| `pre_install_desc` | string | `None` | pre_install 描述（GUI中显示复选框） |
| `post_install` | string | `None` | 安装后脚本路径 |
| `post_install_desc` | string | `None` | post_install 描述 |
| `pre_uninstall` | string | `None` | 卸载前脚本（仅 Windows） |
| `script_env_variables` | dict | `{}` | 传递给脚本的环境变量 |

脚本可用环境变量：
- `${PREFIX}` / `%PREFIX%` — 安装路径
- `${INSTALLER_NAME}` / `%INSTALLER_NAME%` — 安装程序名称
- `${INSTALLER_VER}` / `%INSTALLER_VER%` — 版本
- `${INSTALLER_PLAT}` / `%INSTALLER_PLAT%` — 平台
- `${INSTALLER_TYPE}` / `%INSTALLER_TYPE%` — `SH`/`PKG`/`EXE`/`MSI`
- `${INSTALLER_UNATTENDED}` / `%INSTALLER_UNATTENDED%` — 无人值守安装时为 `"1"`

### 图片与品牌

| 字段 | 类型 | 默认值 | 平台 | 说明 |
|------|------|--------|------|------|
| `welcome_image` | string | 自动生成/默认logo | Win/macOS | 欢迎图片（164x314 NSIS, 1227x600 PKG） |
| `header_image` | string | 自动生成 | Win | 头图（150x57） |
| `icon_image` | string | 自动生成 | Win | 图标（256x256） |
| `default_image_color` | `red/green/blue/yellow` | `"blue"` | Win | 默认图片颜色 |
| `welcome_image_text` | string | `name` | Win/macOS | 默认欢迎图片文字 |
| `header_image_text` | string | `name` | Win | 默认头图文字 |

### Windows 特定配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `register_python` | bool | `True` | 是否提供"注册为系统Python"选项 |
| `register_python_default` | bool | `False` | 注册Python默认选中 |
| `nsis_template` | string | `None` | 自定义 NSIS 模板路径 |
| `uninstall_name` | string | 自动生成 | "程序和功能"中显示的名称 |
| `uninstall_with_conda_exe` | bool | `None` | 使用 conda-standalone 执行卸载（需要>=24.11.0） |
| `welcome_file` (nsi) | string | `None` | 自定义 NSIS 欢迎页面 |
| `post_install_pages` | list\<string\> | `None` | 安装后自定义 NSIS 页面 |
| `conclusion_file` (nsi) | string | `None` | 自定义 NSIS 完成页面 |

### macOS 特定配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `welcome_file` (txt/rtf/html) | string | `None` | 欢迎消息文件 |
| `welcome_text` | string | Anaconda消息 | 欢迎消息文本 |
| `readme_file` | string | `None` | README 文件 |
| `readme_text` | string | Anaconda消息 | README 文本 |
| `conclusion_file` (txt/rtf/html) | string | `None` | 完成消息文件 |
| `conclusion_text` | string | Anaconda消息 | 完成消息文本 |
| `signing_identity_name` | string | `None` | Apple 安装程序证书 ID（pkg 签名） |
| `notarization_identity_name` | string | `None` | Apple 应用证书 ID（conda.exe 公证签名） |

### 签名配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `signing_identity_name` | string | `None` | macOS codesign 身份 |
| `windows_signing_tool` | `azuresigntool` \| `signtool` | `signtool`(如有cert) | Windows 签名工具 |
| `signing_certificate` | string | `None` | Windows 签名证书路径（.pfx） |

### 文件注入

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `extra_files` | list\<string\|dict\> | `[]` | 注入到安装根目录的额外文件 |
| `temp_extra_files` | list\<string\|dict\> | `[]` | 安装过程临时文件（Windows: $PLUGINSDIR） |

extra_files 支持两种格式：
```yaml
extra_files:
  - ./config.yaml                     # 字符串：复制到根目录
  - {"src": "./scripts/init.sh", "dst": "bin/init.sh"}  # 字典：指定源和目标
```

### Docker 构建配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `docker_base_image` | string | `None` | Docker 基础镜像（Docker功能必需） |
| `docker_tag` | string | `<name>:<version>` | Docker 镜像标签 |
| `docker_labels` | dict | `{}` | Docker 镜像额外标签 |
| `docker_image_format` | `"tar"` | `None` | 导出镜像为 tar 包 |

### 构建产物

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `build_outputs` | list\<BuildOutputs\|dict\> | `[]` | 额外构建产物 |

支持的值：
- `"hash"` — 安装程序哈希校验文件（SHA256）
- `"info.json"` — 构建信息 JSON
- `"licenses"` — 所有包的许可证文件集合
- `"lockfile"` — conda-lock 格式锁文件
- `"pkgs_list"` — 包含的包列表（CSV/JSON）

### 已废弃字段

以下字段已废弃，使用时会触发警告但不报错：
- `install_in_dependency_order` — 由 conda-standalone 自动处理
- `attempt_hardlinks` — 同上
- `check_path_length` — 路径长度检查现在始终执行

## Schema 校验机制

constructor 使用 JSON Schema Draft 2020-12 校验配置：

1. **Schema 来源**：`constructor/data/construct.schema.json`，由 `_schema.py` 中的 Pydantic 模型自动生成
2. **校验器**：`jsonschema.Draft202012Validator`，扩展了 deprecated 字段检查
3. **deprecated 字段**：标记为 `deprecated=True` 的字段触发 `DeprecatedFieldWarning`（仅警告），其他错误终止构建
4. **Pydantic 模型**：`ConstructorConfiguration` 使用 `ConfigDict(extra="forbid")`，禁止未声明字段

手动更新 Schema（修改 _schema.py 后）：

```bash
python -m constructor._schema
```

这会重新生成 `construct.schema.json` 文件。

## 查看所有可用配置键

constructor 提供了 `--help-construct` 选项，从 JSON Schema 动态读取并格式化输出所有可用配置键：

```bash
constructor . --help-construct
```

同时列出当前平台可用的 selectors。

## 下一步

- [04-安装程序类型](./04-installer-types.md)：深入了解 sh/pkg/exe/msi/docker 五种安装程序类型
- [05-CLI 命令行入口](./05-cli-and-entrypoint.md)：完整的命令行参数参考
