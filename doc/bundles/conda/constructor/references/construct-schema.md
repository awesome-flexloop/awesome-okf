---
type: reference
title: "construct.yaml 解析与 Schema 校验 (construct.py + _schema.py)"
description: "construct.yaml 文件的解析、Selector处理、Jinja2渲染和JSON Schema校验机制源码分析。"
tags: [construct.yaml, JSON-Schema, Pydantic, Selector, Jinja2, YAML解析]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T00:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: constructor-construct
    resource: "constructor/construct.py"
    title: "constructor/construct.py YAML解析模块"
  - id: constructor-schema
    resource: "constructor/_schema.py"
    title: "constructor/_schema.py Pydantic Schema定义"
---

# construct.yaml 解析与 Schema 校验

construct.yaml 是 constructor 的唯一输入配置文件。解析流程分为：**Selector预处理 → Jinja2渲染 → YAML解析 → Schema校验** 四步。

## 解析流程

### `render(path, platform)` → 预处理+渲染

```python
def render(path, platform):
    data = open(path).read()
    content_filter = partial(select_lines, namespace=ns_platform(platform))
    data = content_filter(data)           # Step 1: Selector 行过滤
    try:
        yaml.load(data)                   # Step 2: 尝试直接 YAML 解析
        return data
    except YAMLError:
        if "{{" not in data and "{%" not in data:
            raise UnableToParse(...)
        return render_jinja_for_input_file(data, directory, content_filter)  # Step 3: Jinja2渲染
```

### `parse(path, platform)` → YAML加载

调用 `yaml.load(render(path, platform))`，将 `version` 字段强制转为字符串，删除值为 `None` 的键。

### `verify(info)` → Schema校验

```python
schema = json.loads(SCHEMA_PATH.read_text())  # 加载 construct.schema.json
validator = get_validator_class()(schema)     # Draft202012Validator + deprecated 扩展
for error in validator.iter_errors(info):
    if isinstance(error, DeprecatedFieldWarning):
        print(stderr警告)  # deprecated字段仅警告
    else:
        errors.append(error)  # 其他错误收集后sys.exit
```

额外非Schema校验：`windows_signing_tool` 为 `signtool/signtool.exe` 时必须提供 `signing_certificate`。

## Selector 机制（`select_lines`）

constructor 复用 conda-build 的 Selector 语法，在 YAML 行尾使用 `# [selector]` 条件注释：

```yaml
welcome_image: img/win.bmp  # [win]
welcome_image: img/mac.png  # [osx]
channels:
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main  # [linux64 or osx]
```

正则模式 `sel_pat = re.compile(r"(.+?)\s*(#.*)?\[([^\[\]]+)\](?(2)[^\(\)]*)$")` 提取条件表达式，使用 Python `eval(cond, namespace, {})` 在 `ns_platform(platform)` 命名空间中求值。

`ns_platform(platform)` 返回的布尔命名字典：
- `linux`, `linux32`, `linux64`, `aarch64`, `ppc64le`, `s390x`, `armv7l`
- `osx`, `arm64`（即 osx-arm64）
- `win`, `win32`, `win64`, `win_arm64`
- `x86`, `x86_64`, `unix`

## Pydantic Schema 模型（`_schema.py`）

Schema 使用 Pydantic v2 `BaseModel` 定义，运行 `python -m constructor._schema` 生成 `constructor/data/construct.schema.json`。

核心模型：

| 模型 | 用途 |
|------|------|
| `ConstructorConfiguration` | construct.yaml 根配置（name/version/channels/specs等80+字段） |
| `InstallerTypes` | StrEnum: `all/exe/msi/pkg/sh/docker` |
| `ChannelRemap` | `src/dest` 通道重映射 |
| `ExtraEnv` | 额外环境配置（specs/channels/exclude/menu_packages/freeze_env等） |
| `BuildOutputs` | StrEnum: `hash/info.json/licenses/lockfile/pkgs_list` |
| `WinSignTools` | StrEnum: `azuresigntool/signtool` |
| `CondaInitialization` | StrEnum: `classic/condabin` |
| `PkgDomains` | StrEnum: `enable_anywhere/enable_currentUserHome/enable_localSystem` |

配置字段验证规则：
- `name` / `version`：正则 `^[a-zA-Z0-9_]([a-zA-Z0-9._-]*[a-zA-Z0-9_])?$`
- `extra_envs` 键名：正则 `^[^/:# ]+$`（环境名），禁止 `base`/`root`
- `model_config = ConfigDict(extra="forbid")` — 禁止未声明字段
- `use_attribute_docstrings=True` — 从字段 docstring 生成 Schema 描述

## Jinja2 模板支持

当 YAML 包含 `{{` 或 `{%` 时，constructor 使用 `jinja.py` 中的 `FilteredLoader` 渲染：
- 注入 `environ`（环境变量）和 `os`（Python os模块）到 Jinja2 全局命名空间
- `FilteredLoader` 在加载模板时自动应用 Selector 过滤
- 模板渲染错误抛出 `UnableToParse` 异常
