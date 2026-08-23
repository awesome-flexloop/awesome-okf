---
type: Concept
title: 配置系统
description: MdParserConfig 数据类、配置项自动注册、全局/文件级双层配置体系详解
tags: [myst, sphinx, config, mdparserconfig, myst-parser]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: myst-parser-source
    resource: /references/myst-parser-source.md
    title: MyST-Parser 源码路径映射
---

## 配置系统

MyST-Parser 的配置系统以 `MdParserConfig` 数据类为单一真相源（Single Source of Truth），通过字段元数据驱动 Sphinx/docutils/文档三处的自动注册。

## MdParserConfig 数据类

`MdParserConfig` 是一个 Python dataclass，集中定义了所有 MyST 配置选项。每个字段通过 `dc.field()` 声明类型、默认值和元数据：

```python
@dc.dataclass()
class MdParserConfig:
    enable_extensions: set[str] = dc.field(
        default_factory=set,
        metadata={"validator": check_extensions, "help": "Enable syntax extensions"},
    )
    heading_anchors: int = dc.field(
        default=0,
        metadata={
            "validator": optional(in_([0,1,2,3,4,5,6,7])),
            "help": "Heading level depth to assign HTML anchors",
        },
    )
```

### 字段元数据键

| metadata 键 | 作用 |
|------------|------|
| `validator` | 字段值验证/转换函数，在 `__post_init__` 时调用 |
| `help` | 帮助文本，用于自动生成文档 |
| `extension` | 标记该字段属于哪个扩展（如 "dollarmath"） |
| `global_only` | 标记为仅全局配置（不可在文件级 frontmatter 中覆盖） |
| `omit` | 列表，包含 "sphinx" 或 "docutils"，表示在该宿主中不注册 |
| `merge_topmatter` | True 表示文件级配置与全局配置合并（字典类型）而非覆盖 |
| `repr` | False 表示不在 `__repr__` 中显示该字段 |
| `doc_type` | 文档中显示的类型字符串 |

## Sphinx 配置自动注册

在 `setup_sphinx()` 中，通过遍历 `MdParserConfig` 的字段自动注册所有 Sphinx 配置值：

```python
for name, default, field in MdParserConfig().as_triple():
    if "sphinx" not in field.metadata.get("omit", []):
        app.add_config_value(f"myst_{name}", default, "env", types=Any)
```

- 配置名自动加 `myst_` 前缀
- 重建级别为 `"env"`（环境变更时触发重建）
- 字段标记了 `omit=["sphinx"]` 的不会注册

### builder-inited 配置创建

`create_myst_config(app)` 在 builder-inited 事件中执行：

1. 从 `app.config[f"myst_{name}"]` 读取所有配置值
2. 构造 `MdParserConfig(**values)` 实例
3. 存入 `app.env.myst_config`
4. 配置无效时记录错误并回退到默认配置
5. 检查 `attrs_image` 弃用警告和 `linkify` 依赖缺失警告

## Docutils CLI 配置自动生成

在 docutils 独立使用时，`create_myst_settings_spec()` 自动从 `MdParserConfig` 字段生成 optparse 选项：

```python
def create_myst_settings_spec(config_cls=MdParserConfig):
    defaults = config_cls()
    return tuple(
        attr_to_optparse_option(at, getattr(defaults, at.name))
        for at in config_cls.get_fields()
        if ("docutils" not in at.metadata.get("omit", []))
    )
```

每个字段类型映射到对应的 optparse 类型（int、bool、str、逗号分隔列表、YAML 字典等）。

## 双层配置体系

### 全局配置层

通过 Sphinx `conf.py` 中的 `myst_*` 变量或 docutils CLI 参数设置，作用于所有文档。

```python
# conf.py — 全局配置
myst_enable_extensions = ["dollarmath", "colon_fence"]
myst_heading_anchors = 3
```

### 文件级配置层

每个 Markdown 文件开头的 YAML frontmatter 中 `myst` 键可以覆盖全局配置：

```markdown
---
myst:
  enable_extensions: ["dollarmath"]
  substitutions:
    project: "我的项目"
---
```

### 合并策略

`merge_file_level()` 函数处理合并逻辑：

- 普通字段：文件级值直接覆盖全局值
- `merge_topmatter=True` 的字段（如 `html_meta`、`substitutions`）：字典合并（`{**old_value, **value}`）
- `global_only=True` 的字段：不可在文件级设置
- 未知字段：发出 `MD_TOPMATTER` 警告
- 值验证失败：发出警告但继续处理

## 常用配置项参考

### 核心配置

| 配置项 | 类型 | 默认 | 说明 |
|--------|------|------|------|
| `myst_enable_extensions` | set[str] | set() | 启用的扩展语法 |
| `myst_disable_syntax` | list[str] | [] | 禁用的 CommonMark 语法 |
| `myst_commonmark_only` | bool | False | 严格 CommonMark 模式 |
| `myst_gfm_only` | bool | False | 严格 GFM 模式 |

### 链接配置

| 配置项 | 类型 | 默认 | 说明 |
|--------|------|------|------|
| `myst_all_links_external` | bool | False | 所有链接作为外部链接 |
| `myst_url_schemes` | dict | {http,https,mailto,ftp:None} | 外部链接 URL scheme |
| `myst_ref_domains` | list[str] | None | 引用搜索的 Sphinx 域 |

### 标题配置

| 配置项 | 类型 | 默认 | 说明 |
|--------|------|------|------|
| `myst_heading_anchors` | int(0-7) | 0 | 自动锚点深度 |
| `myst_heading_slug_func` | str/Callable | None | slug 函数预设名或调用able |
| `myst_heading_anchors_html_ids` | bool | True | 同时输出 HTML id |

### 其他配置

| 配置项 | 类型 | 默认 | 说明 |
|--------|------|------|------|
| `myst_html_meta` | dict | {} | HTML meta 标签（可合并） |
| `myst_substitutions` | dict | {} | 替换变量（可合并） |
| `myst_footnote_sort` | bool | True | 脚注排序 |
| `myst_number_code_blocks` | list[str] | [] | 加行号的代码块语言 |
| `myst_title_to_header` | bool | False | frontmatter title 转 H1 |
| `myst_fence_as_directive` | set[str] | set() | 指定语言代码围栏转为指令 |
| `myst_suppress_warnings` | list[str] | [] | 抑制的警告类型 |

## 相关概念

- [三阶段解析管线](/concepts/03-architecture-pipeline.md)
- [扩展语法系统](/concepts/05-extension-system.md)
- [YAML Frontmatter](/concepts/12-frontmatter.md)
- [Sphinx 集成机制](/concepts/11-sphinx-integration.md)
- [警告系统](/concepts/14-warning-system.md)
