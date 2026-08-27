---
type: concept
title: "Transifex 平台集成"
description: "sphinx-intl 与 Transifex 云端翻译平台的集成——CLI 检测、资源名规范化、tx config 自动配置"
tags: [transifex, collaboration, cloud-translation, tx-cli, localization]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:52:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-21T14:52:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: transifex-api
    resource: /references/transifex-api.md
    title: "transifex.py Transifex 集成 API 参考"
---

# Transifex 平台集成

Transifex 是一个云端翻译协作平台，允许多个翻译人员通过 Web 界面协同翻译文档。sphinx-intl 提供了可选的 Transifex 集成功能，简化本地 PO 文件与 Transifex 平台之间的同步配置。

## Transifex 工作流

使用 Transifex 时的典型工作流：

```
本地 POT 文件 → tx push -s → Transifex 云端（翻译人员在线翻译）
                                              ↓
本地 MO 文件 ← sphinx-intl build ← tx pull -l <lang> ← 翻译完成的 PO 文件
```

1. **上传源文件**：`tx push -s` 将 POT 文件推送到 Transifex
2. **云端翻译**：翻译人员在 Transifex Web 界面上翻译
3. **拉取翻译**：`tx pull -l ja` 将翻译完成的 PO 文件拉回本地
4. **编译构建**：`sphinx-intl build` 编译 MO，Sphinx 构建文档

sphinx-intl 的 Transifex 相关命令主要解决**配置问题**——自动生成和更新 `.tx/config` 文件，避免手动配置每个资源的繁琐。

## Transifex CLI 依赖

Transifex 功能依赖外部的 Transifex CLI 工具（`tx` 命令），它不是 sphinx-intl 的 Python 依赖，需要单独安装。

### CLI 安装

```bash
curl -o- https://raw.githubusercontent.com/transifex/cli/master/install.sh | bash
```

### CLI 版本检测 [F-054]

sphinx-intl 通过 `check_transifex_cli_installed()` 函数验证环境：

1. **命令存在性**：使用 `shutil.which("tx")` 检查 `tx` 命令是否在 PATH 中
2. **版本类型**：执行 `tx --version`，检查输出是否以 `"TX Client"` 开头——这排除了旧版的 Python transifex_client 库
3. **版本号**：解析版本号（从 `TX Client=1.x.x` 格式中提取），要求 ≥ 1.2.1

任一检查失败都会抛出 `click.BadParameter` 异常，并给出安装命令提示。

## 三个 Transifex 子命令

### create-transifexrc（已废弃）[F-055]

```bash
sphinx-intl create-transifexrc --transifex-token <TOKEN>
```

创建 `~/.transifexrc` 认证文件，包含 API token。

**此命令已废弃**。现代 Transifex CLI 推荐使用 `TX_TOKEN` 环境变量进行认证，不再需要 `.transifexrc` 文件。执行此命令会输出 DeprecationWarning。

生成的文件格式：

```ini
[https://www.transifex.com]
rest_hostname = https://rest.api.transifex.com
token = <your_token>
```

### create-txconfig [F-056]

```bash
sphinx-intl create-txconfig
```

在当前目录创建 `.tx/config` 初始化配置文件。

- 如果 `.tx` 目录不存在则创建
- 如果 `.tx/config` 已存在则跳过（不覆盖）
- 写入最小配置（只包含 `[main]` 段）

生成的文件格式：

```ini
[main]
host = https://www.transifex.com
```

### update-txconfig-resources [F-057]

```bash
sphinx-intl update-txconfig-resources \
  --transifex-organization-name <org> \
  --transifex-project-name <project>
```

这是最有用的 Transifex 命令——自动扫描 POT 文件，为每个文件调用 `tx add` 注册为 Transifex 资源。

**流程**：

1. 检测 Transifex CLI 是否已安装且版本满足要求
2. 清理项目名（空格→连字符，移除非字母数字字符）
3. 递归扫描 `pot_dir/**/*.pot` 文件
4. 使用 `click.progressbar` 显示进度条
5. 对每个 POT 文件：
   - 计算 resource_path（相对 pot_dir 的路径，去扩展名）
   - 调用 `normalize_resource_name()` 生成 Transifex 合法的资源 slug
   - 加载 POT 文件，跳过空文件（`len(pot) == 0`）
   - 构建并执行 `tx add` 命令

**tx add 命令参数**：

| 参数 | 值模板 | 说明 |
|------|--------|------|
| `--organization` | 用户指定 | Transifex 组织名 |
| `--project` | 用户指定（清理后） | Transifex 项目名 |
| `--resource` | normalize 后的 slug | 资源标识符 |
| `--resource-name` | normalize 后的 slug | 资源显示名 |
| `--file-filter` | `<locale_dir>/<lang>/LC_MESSAGES/<path>.po` | 翻译文件模式 |
| `--type` | `PO` | 文件类型 |
| 位置参数 | `<pot_dir>/<path>.pot` | 源 POT 文件路径 |

## 资源名规范化：normalize_resource_name

Transifex 对资源名有严格限制，`normalize_resource_name()` 函数将任意文件路径转换为合法的 Transifex 资源名 [F-058]。

### 转换规则

**规则 1：路径分隔符 → `--`**

```python
name = re.sub(r"[\\/]", "--", name)
```

- `docs/index` → `docs--index`
- `chapter1/section2` → `chapter1--section2`

**规则 2：非法字符 → `_`**

```python
name = re.sub(r"[^\-\w]", "_", name)
```

非 `-`、`_`、字母、数字的字符都替换为下划线。

**规则 3：保留名追加 `_`**

```python
while name in IGNORED_RESOURCE_NAMES:
    name += "_"
```

Transifex 有一些保留的 slug 名（如 `glossary`、`settings`），直接使用会导致 API 错误。sphinx-intl 通过追加下划线来避免冲突：

- `glossary` → `glossary_`
- `settings` → `settings_`
- （理论上 `glossary_` 如果也被占用会继续追加，但这是极端情况）

### IGNORED_RESOURCE_NAMES [F-059]

```python
IGNORED_RESOURCE_NAMES = ("glossary", "settings")
```

当前只处理了两个保留名。注释中明确说明追加 `_` 不处理碰撞问题（如 `glossary` 和 `glossary_` 都会变成 `glossary_`），但这在实际使用中极少遇到。

## 配置文件格式

### .tx/config

执行 `create-txconfig` + `update-txconfig-resources` 后，`.tx/config` 文件大致如下：

```ini
[main]
host = https://www.transifex.com

[o:myorg:p:myproject:r:docs--index]
file_filter = locale/<lang>/LC_MESSAGES/docs/index.po
source_file = locale/pot/docs/index.pot
source_lang = en
type = PO

[o:myorg:p:myproject:r:docs--install]
file_filter = locale/<lang>/LC_MESSAGES/docs/install.po
source_file = locale/pot/docs/install.pot
source_lang = en
type = PO
```

每个资源段的 ID 格式为 `o:<org>:p:<project>:r:<resource_slug>`。

### 认证方式对比

| 方式 | 说明 | 推荐度 |
|------|------|--------|
| `TX_TOKEN` 环境变量 | 现代方式，灵活安全 | ✅ 推荐 |
| `~/.transifexrc` 文件 | 传统方式，create-transifexrc 生成 | ⚠️ 已废弃 |

使用环境变量方式：

```bash
export TX_TOKEN=your_api_token_here
tx push -s    # 上传源文件
tx pull -l ja  # 拉取日语翻译
```

## 空 POT 文件跳过

update-txconfig-resources 在注册资源前会检查 POT 文件是否为空：

```python
pot = load_po(str(pot_path))
if len(pot):
    # 执行 tx add
else:
    click.echo(f"{pot_path} is empty, skipped")
```

空的 POT 文件（不含任何可翻译消息）注册到 Transifex 没有意义，会被自动跳过。这通常对应于占位文档或仅包含 toctree 指令的索引文件。

## Transifex 集成的边界

sphinx-intl 的 Transifex 集成**只做配置管理**，不直接调用 Transifex API 上传/下载翻译。实际上传和下载操作由 `tx` 命令完成：

- **sphinx-intl 负责**：创建配置文件、自动注册资源、规范资源名
- **tx CLI 负责**：认证、上传 POT、拉取 PO、同步翻译状态

这种设计遵循 Unix 哲学——每个工具做好一件事，通过配置文件协作。

## 相关概念

- [CLI 命令体系详解](02-cli-commands.md)
- [配置读取与 Python 兼容层](08-config-and-compat.md)
- [Transifex 协作翻译示例](../examples/transifex-collaboration.md)
