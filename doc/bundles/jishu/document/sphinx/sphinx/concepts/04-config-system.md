---
type: "concept"
title: "配置系统"
description: "Config类工作原理——_Opt配置选项、_ConfigRebuild级别、conf.py执行机制、config_values默认值、add_config_value扩展API"
tags: [core, config, conf.py, Config-class, configuration]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T09:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T09:47:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: config-py
    resource: sphinx/config.py
    title: "Sphinx Config class and _Opt"
  - id: app-init
    resource: /references/sphinx-app-init.md
    title: "Sphinx应用初始化源码"
---

# 配置系统

Sphinx 的配置系统由 `Config` 类（定义在 sphinx/config.py）负责管理。配置文件 `conf.py` 本质上是一个普通的 Python 文件，Sphinx 在初始化时执行它，然后将其中定义的变量作为配置项加载。

## _Opt：配置选项定义

每个配置选项由不可变的 `_Opt` 对象定义，包含四个字段 [F-014]：

| 字段 | 类型 | 说明 |
|------|------|------|
| `default` | `Any` | 默认值。可以是值或lambda函数（lambda config: ...） |
| `rebuild` | `_ConfigRebuild` | 配置变更时需要重建的级别 |
| `valid_types` | `frozenset[type] \| ENUM \| Any` | 有效值类型约束 |
| `description` | `str` | 配置项描述（用于文档生成） |

`_Opt` 对象是**不可变的**——构造后不允许修改或删除任何字段：

```python
class _Opt:
    __slots__ = 'default', 'rebuild', 'valid_types', 'description'
    # __setattr__ 和 __delattr__ 会对核心字段抛 TypeError
```

## _ConfigRebuild：重建级别

`_ConfigRebuild` 是一个字符串字面量类型，定义配置变更时的影响范围 [F-015]：

| 值 | 含义 |
|----|------|
| `''`（空字符串） | 不影响构建，无需重建 |
| `'env'` | 变更需要重建环境（doctree缓存失效），触发全量READING |
| `'html'` | 变更只影响HTML输出，不需要重新读取源文件 |
| `'epub'` | 只影响EPUB输出 |
| `'gettext'` | 只影响gettext翻译模板输出 |
| `'applehelp'` | 只影响AppleHelp输出（sphinxcontrib-applehelp） |
| `'devhelp'` | 只影响DevHelp输出（sphinxcontrib-devhelp） |

这个级别决定了增量构建时哪些缓存需要失效。例如，`'html'` 级别配置变更后，Sphinx 可以跳过重新解析源文件（READING阶段），直接进入WRITING阶段重新生成HTML。

## config_values：内置配置默认值

`Config.config_values` 是一个类级字典，定义了所有内置配置项及其默认值。截至 Sphinx 9.1.1，包含约50个内置配置项 [F-016]：

### 通用配置

| 配置项 | 默认值 | 重建级别 | 类型 | 说明 |
|--------|--------|---------|------|------|
| `project` | `'Project name not set'` | `'env'` | `str` | 项目名称 |
| `author` | `'Author name not set'` | `'env'` | `str` | 作者名 |
| `project_copyright` | `''` | `'html'` | `str\|tuple\|list` | 版权声明 |
| `copyright` | `lambda config: config.project_copyright` | `'html'` | `str\|tuple\|list` | copyright别名 |
| `version` | `''` | `'env'` | `str` | 短版本号 |
| `release` | `''` | `'env'` | `str` | 完整版本号 |
| `language` | `'en'` | `'env'` | `str` | 文档语言 |
| `today` | `''` | `'env'` | `str` | 今天日期（空则自动生成） |
| `today_fmt` | `None`（locale依赖） | `'env'` | `str` | 日期格式 |

### 源文件配置

| 配置项 | 默认值 | 重建级别 | 类型 | 说明 |
|--------|--------|---------|------|------|
| `master_doc` | `'index'` | `'env'` | `str` | 主文档名（root_doc别名） |
| `root_doc` | `lambda config: config.master_doc` | `'env'` | `str` | 主文档名（推荐使用） |
| `source_suffix` | `{'.rst': 'restructuredtext'}` | `'env'` | `dict` | 源文件后缀与解析器映射 |
| `source_encoding` | `'utf-8-sig'` | `'env'` | `str` | 源文件编码 |
| `exclude_patterns` | `[]` | `'env'` | `list[str]` | 排除的文件模式 |
| `include_patterns` | `['**']` | `'env'` | `list[str]` | 包含的文件模式 |
| `default_role` | `None` | `'env'` | `str` | 默认reST角色 |
| `primary_domain` | `'py'` | `'env'` | `str\|None` | 默认域 |

### 显示配置

| 配置项 | 默认值 | 重建级别 | 类型 | 说明 |
|--------|--------|---------|------|------|
| `pygments_style` | `None` | `'html'` | `str` | Pygments语法高亮主题 |
| `highlight_language` | `'default'` | `'env'` | `str` | 默认高亮语言 |
| `highlight_options` | `{}` | `'env'` | `dict` | 高亮选项 |
| `add_function_parentheses` | `True` | `'env'` | `bool` | 函数名后加括号 |
| `add_module_names` | `True` | `'env'` | `bool` | 描述中显示模块名 |
| `show_authors` | `False` | `'env'` | `bool` | 显示代码作者 |
| `toc_object_entries` | `True` | `'env'` | `bool` | 目录中显示对象条目 |
| `toc_object_entries_show_parents` | `'domain'` | `'env'` | ENUM | 目录中父级显示方式 |
| `numfig` | `False` | `'env'` | `bool` | 自动编号图表表格 |
| `numfig_secnum_depth` | `1` | `'env'` | `int\|None` | 编号的章节深度 |
| `smartquotes` | `True` | `'env'` | `bool` | 智能引号转换 |
| `smartquotes_action` | `'qDe'` | `'env'` | `str` | 智能引号行为 |
| `nitpicky` | `False` | `''` | `bool` | 严格模式（所有未解析引用报错） |

### 模板与路径

| 配置项 | 默认值 | 重建级别 | 类型 | 说明 |
|--------|--------|---------|------|------|
| `templates_path` | `[]` | `'html'` | `list` | 模板搜索路径 |
| `template_bridge` | `None` | `'html'` | `str` | 自定义模板桥接类 |
| `locale_dirs` | `['locales']` | `'env'` | `list\|tuple` | 翻译目录 |
| `rst_prolog` | `None` | `'env'` | `str` | 每个文件开头的reST内容 |
| `rst_epilog` | `None` | `'env'` | `str` | 每个文件末尾的reST内容 |

## Config 类工作原理

### 初始化与读取

```python
# 方式1：从conf.py文件读取（Sphinx初始化时使用）
config = Config.read(confdir, overrides={}, tags=tags)

# 方式2：直接创建
config = Config(config={'project': 'My Proj', 'extensions': []}, overrides=None)
```

`Config.read()` 执行流程 [F-017]：
1. 在 `confdir` 中查找 `conf.py` 文件
2. 调用 `_read_conf_py()` 执行 conf.py：
   - 将 `confdir` 添加到 `sys.path`
   - 在执行命名空间中预注入 `tags` 对象（用于 `if tags.has('...')` 条件判断）
   - `exec(code, namespace)` 执行 conf.py
   - 收集命名空间中不以 `_` 开头的变量作为原始配置
3. 创建 Config 对象，传入原始配置和overrides

### 属性访问

Config 通过 `__getattr__` 实现透明的属性访问：
- 先检查 overrides（命令行 `-D` 覆盖的值）
- 再检查 `_raw_config`（conf.py中定义的值）
- 最后回退到 `_options` 中的默认值
- 默认值如果是callable（如lambda），会调用 `default(config)` 计算实际值

```python
# __getattr__ 的核心逻辑
def __getattr__(self, name):
    if name in self._options:
        if name in self._overrides:
            return self._overrides[name]
        if name in self._raw_config:
            return self._raw_config[name]
        default = self._options[name].default
        return default(self) if callable(default) else default
    raise AttributeError(f'Config has no attribute {name!r}')
```

### 别名处理

Config 通过 `__setattr__` 维护别名对的双向同步 [F-018]：
- `master_doc` ↔ `root_doc`（后者是推荐名称）
- `copyright` ↔ `project_copyright`（后者是推荐名称）

设置其中一个会自动更新另一个。

## ENUM：枚举约束

`ENUM` 类用于约束配置值必须是预定义候选项之一 [F-019]：

```python
# 定义
app.add_config_value('toc_object_entries_show_parents', 'domain', 'env',
                     ENUM('domain', 'all', 'hide'))

# 使用
# 在conf.py中
toc_object_entries_show_parents = 'all'  # OK
toc_object_entries_show_parents = 'foo'  # 警告：无效值
```

`ENUM` 的 `match()` 方法支持单个值和序列值检查，还处理了命令行字符串到布尔值的转换（`'1'` → `True`，`'0'` → `False`）。

## add_config_value：扩展注册配置

扩展通过 `app.add_config_value()` 注册自定义配置项 [F-020]：

```python
def add_config_value(
    self,
    name: str,           # 配置项名称
    default: Any,        # 默认值
    rebuild: _ConfigRebuild,  # 重建级别
    types: type | Collection[type] | _OptValidTypes = Any,  # 类型约束
    description: str = '',   # 描述（用于文档）
) -> None:
```

### rebuild 参数选择指南

| 场景 | 选择 |
|------|------|
| 影响文档解析结果（新增指令/角色等） | `'env'` |
| 只影响HTML外观（颜色、布局、主题选项） | `'html'` |
| 不影响输出（内部开关、调试标志） | `''` |
| 只影响特定输出格式 | `'epub'`/`'gettext'`等 |

### 类型约束示例

```python
from sphinx.config import ENUM

# 布尔值
app.add_config_value('my_feature_enabled', False, 'env', bool)

# 字符串
app.add_config_value('my_color', 'blue', 'html', str)

# 多种类型
app.add_config_value('my_value', None, 'env', (str, int, type(None)))

# 枚举
app.add_config_value('my_mode', 'fast', 'env', ENUM('fast', 'slow', 'auto'))

# 任意类型
app.add_config_value('my_complex', {}, 'env', Any)
```

## 命令行覆盖

通过 `-D` 命令行选项可以覆盖conf.py中的配置值：

```bash
sphinx-build -b html -D language=zh_CN -D html_theme=furo docs _build/html
```

覆盖值通过 `confoverrides` 参数传入 Config，优先级高于 conf.py 中的设置。`Config.convert_overrides()` 负责将命令行字符串值转换为正确的Python类型：
- 布尔配置：`'1'` → `True`，`'0'` → `False`
- 列表配置：逗号分隔字符串 → list
- 整数配置：字符串 → int
- 字典配置：使用点号语法 `name.key=value`
- 字符串配置：直接使用字符串值

## 不可序列化类型

`UNSERIALIZABLE_TYPES = (type, types.ModuleType, types.FunctionType)` 定义了不能被pickle序列化的类型。Config 通过 `is_serializable()` 递归检查配置值是否可序列化，不可序列化的值会导致BuildEnvironment缓存失败。

## 相关概念

- [Sphinx应用类](03-application-class.md)
- [构建环境](07-build-environment.md)
- [编写第一个Sphinx扩展](../examples/01-first-extension.md)
