---
type: Concept
title: 配置系统
description: NbParserConfig 三层覆盖体系（全局→文件→Cell）、nb_* 配置项、配置继承与覆盖规则
tags: [myst-nb, config, nbparserconfig, metadata, cell-config]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:30:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: mystnb-source
    resource: /references/mystnb-source.md
    title: MyST-NB 源码路径映射
---

## 配置系统

MyST-NB 的配置由 `NbParserConfig` 数据类统一管理，实现**全局→文件→Cell** 三层配置覆盖，优先级：Cell > 文件 > 全局 > 默认值。

## 配置前缀

在 Sphinx 的 `conf.py` 中，所有配置项以 `nb_` 为前缀：

```python
# conf.py
nb_execution_mode = "cache"
nb_execution_timeout = 60
nb_remove_code_source = False
```

## 三层覆盖体系

### 第 1 层：全局配置（conf.py）

在 `conf.py` 中设置 `nb_*` 配置项，作用于所有 notebook 文件：

```python
nb_execution_mode = "auto"
nb_execution_timeout = 30
nb_output_stderr = "show"
```

### 第 2 层：文件级配置（frontmatter）

在 notebook 的 YAML frontmatter 中设置 `mystnb:` 键覆盖全局配置：

```markdown
---
file_format: mystnb
kernelspec:
  name: python3
mystnb:
  execution_mode: "force"
  execution_timeout: 120
  remove_code_outputs: false
---
```

对于 `.ipynb` 文件，在 notebook metadata 中设置：

```json
{
  "metadata": {
    "kernelspec": {"name": "python3"},
    "mystnb": {
      "execution_mode": "force",
      "execution_timeout": 120
    }
  }
}
```

### 第 3 层：Cell 级配置（cell metadata）

在单个 cell 的 metadata 中设置 `mystnb:` 键：

文本格式：
````markdown
```{code-cell}
---
mystnb:
  remove_code_source: true
  scroll_outputs: true
---
print("这段代码会被隐藏源码")
```
````

.ipynb 格式：
```json
{
  "cell_type": "code",
  "metadata": {
    "mystnb": {
      "remove_code_source": true,
      "scroll_outputs": true
    }
  },
  "source": ["print('...')"]
}
```

或者使用 cell tags（简单开关）：
````markdown
```{code-cell}
:tags: [remove-input, remove-stderr]

print("隐藏源码和 stderr")
```
````

### 优先级规则

配置查找顺序（由高到低）：
1. Cell metadata 中的 `mystnb.<cell_key>` 值
2. 文件级 frontmatter 中的 `mystnb.<field>` 值
3. 全局 conf.py 中的 `nb_<field>` 值
4. NbParserConfig 默认值

## 配置分类

### 执行配置

| 配置项 | 类型 | 默认 | 说明 | 适用级别 |
|--------|------|------|------|---------|
| `nb_execution_mode` | str | "auto" | 执行模式 | 全局/文件 |
| `nb_execution_timeout` | int | 30 | 单 cell 超时（秒） | 全局/文件/Cell |
| `nb_execution_cache_path` | str | "" | 缓存路径 | 全局/文件 |
| `nb_execution_in_temp` | bool | False | 临时目录执行 | 全局/文件 |
| `nb_execution_allow_errors` | bool | False | 允许执行错误 | 全局/文件 |
| `nb_execution_raise_on_error` | bool | False | 失败抛异常 | 全局/文件 |
| `nb_execution_show_tb` | bool | False | 显示 traceback | 全局/文件 |
| `nb_execution_excludepatterns` | list | [] | 排除执行的 glob 模式 | 全局 |
| `nb_kernel_rgx_aliases` | dict | {} | Kernel 名称映射 | 全局 |
| `nb_eval_name_regex` | str | "^[a-zA-Z_]..." | eval 变量名正则 | 全局/文件 |

### 渲染配置

| 配置项 | 类型 | 默认 | 说明 | 适用级别 |
|--------|------|------|------|---------|
| `nb_remove_code_source` | bool | False | 移除源码 | 全局/文件/Cell |
| `nb_remove_code_outputs` | bool | False | 移除输出 | 全局/文件/Cell |
| `nb_scroll_outputs` | bool | False | 长输出滚动 | 全局/文件/Cell |
| `nb_number_source_lines` | bool | False | 代码行号 | 全局/文件/Cell |
| `nb_merge_streams` | bool | False | 合并 stdout/stderr | 全局/文件/Cell |
| `nb_output_stderr` | str | "show" | stderr 处理 | 全局/文件/Cell |
| `nb_code_prompt_show` | str | "Show code cell {type}" | 展开提示 | 全局/文件/Cell |
| `nb_code_prompt_hide` | str | "Hide code cell {type}" | 折叠提示 | 全局/文件/Cell |
| `nb_render_text_lexer` | str | "myst-ansi" | 文本 lexer | 全局/文件/Cell |
| `nb_render_error_lexer` | str | "ipythontb" | 错误 lexer | 全局/文件/Cell |
| `nb_render_markdown_format` | str | "commonmark" | Markdown 渲染格式 | 全局/文件/Cell |
| `nb_render_image_options` | dict | {} | 图片选项 | 全局/文件/Cell |
| `nb_render_figure_options` | dict | {} | figure 选项 | 全局/文件/Cell |
| `nb_mime_priority_overrides` | list | () | MIME 优先级覆盖 | 全局/文件 |
| `nb_render_plugin` | str | "default" | 渲染器插件名 | 全局/文件 |

### 其他配置

| 配置项 | 类型 | 默认 | 说明 |
|--------|------|------|------|
| `nb_custom_formats` | dict | {} | 自定义文件格式读取器 |
| `nb_metadata_key` | str | "mystnb" | notebook 级元数据键名 |
| `nb_cell_metadata_key` | str | "mystnb" | cell 级元数据键名 |
| `nb_ipywidgets_js` | dict | CDN 默认 | ipywidgets JS 配置 |

## Cell metadata 中的键名映射

注意 cell metadata 中使用的键名（cell_key）不一定等于配置字段名：

| 配置字段 | cell metadata 键名 |
|---------|-------------------|
| `render_image_options` | `image` |
| `render_figure_options` | `figure` |
| `render_text_lexer` | `text_lexer` |
| `render_error_lexer` | `error_lexer` |
| `render_markdown_format` | `markdown_format` |
| 其他字段 | 字段名本身 |

## output_stderr 选项

| 值 | 行为 |
|----|------|
| `"show"` | 正常显示 stderr |
| `"remove"` | 移除 stderr 不警告 |
| `"remove-warn"` | 移除 stderr 并发警告 |
| `"warn"` | 显示 stderr 并发警告 |
| `"error"` | stderr 作为错误报告 |
| `"severe"` | stderr 作为严重错误报告 |

## execution_mode 详解

| 模式 | 行为 |
|------|------|
| `"off"` | 不执行任何代码，使用文件中已有的 outputs |
| `"auto"` | 检查代码 cell 是否有 outputs，有缺失则执行（默认） |
| `"force"` | 强制重新执行所有代码 cell，忽略已有 outputs |
| `"cache"` | 使用 jupyter-cache 缓存，代码不变则复用缓存 |
| `"inline"` | 内联模式，启动持久 kernel（供 eval 使用） |

## 遗留配置名

以下旧版配置名仍被支持但会发出弃用警告：

| 旧名 | 新名 |
|------|------|
| `jupyter_execute_notebooks` | `nb_execution_mode` |
| `jupyter_cache` | `nb_execution_cache_path` |
| `execution_excludepatterns` | `nb_execution_excludepatterns` |
| `execution_timeout` | `nb_execution_timeout` |
| `execution_in_temp` | `nb_execution_in_temp` |
| `execution_allow_errors` | `nb_execution_allow_errors` |
| `execution_show_tb` | `nb_execution_show_tb` |
| `nb_render_key` | `nb_cell_metadata_key` |
| `nb_render_priority` | `nb_mime_priority_overrides` |

## 相关概念

- [四阶段处理管线](03-processing-pipeline.md)
- [执行模式与缓存](05-execution-modes.md)
- [Sphinx 集成机制](10-sphinx-integration.md)
- [基础配置示例](../examples/01-basic-setup.md)
