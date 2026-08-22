---
type: Concept
title: 配置项参考
description: sphinx-exercise 的全部配置项：hide_solutions、exercise_style、numfig 编号格式与 i18n 配置
tags: [sphinx, exercise, configuration, hide-solutions, i18n, numfig]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:54:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: exercise-source
    resource: /references/exercise-source.md
    title: sphinx-exercise 源码路径映射
---

# 配置项参考

## hide_solutions

**类型**：`bool`  
**默认值**：`False`  
**重建类型**：`env`（环境变更，需要全量重建）

全局隐藏所有解答内容。设为 `True` 时构建"学生版"文档，解答在指令解析阶段被物理移除。

```python
hide_solutions = True  # 学生版：所有解答不可见
hide_solutions = False  # 教师版：显示解答（默认）
```

### 与 `:hidden:` 选项的区别

| 机制 | 作用范围 | 配置级别 |
|------|---------|---------|
| `hide_solutions = True` | 全局所有解答 | conf.py 全局配置 |
| `:hidden:` 选项 | 单个练习/解答 | 指令级别 |

## exercise_style

**类型**：`str`  
**默认值**：`""`  
**重建类型**：`env`

控制解答标题的显示风格和位置验证：

```python
exercise_style = ""  # 默认："Solution to Exercise N"
exercise_style = "solution_follow_exercise"  # "Solution" + 编号跟随练习
```

### "solution_follow_exercise" 模式效果

1. 解答标题变为"Solution"而非"Solution to Exercise N"
2. 构建时验证解答是否在对应练习之后
3. 跨文档引用解答时发出警告
4. 解答与练习在同一文档时验证顺序

## numfig 编号配置

sphinx-exercise 在 `config-inited` 事件中自动配置：

```python
config["numfig"] = True
numfig_format = {"exercise": f"{translate('Exercise')} %s"}
```

### 自定义编号格式

在 `conf.py` 中设置 `numfig_format` 覆盖默认格式：

```python
# 中文编号
numfig_format = {"exercise": "习题 %s"}

# 其他 numfig 类型也可以同时配置
numfig_format = {
    "exercise": "练习 %s",
    "figure": "图 %s",
    "table": "表 %s",
}
```

### 编号分隔符

Sphinx 的 `numfig_secnum_depth` 控制是否包含章节号：

```python
numfig_secnum_depth = 1  # 编号格式如 "1.1"（章节.序号）
numfig_secnum_depth = 0  # 全局连续编号 "1", "2", "3"
```

## 国际化（i18n）

sphinx-exercise 内置翻译支持：

```python
# 消息目录名
MESSAGE_CATALOG_NAME = "exercise"
```

翻译文件位于 `sphinx_exercise/translations/locales/` 目录，通过 `app.add_message_catalog()` 注册。

### 可翻译文本

- "Exercise" → 练习/Exercise等
- "Solution to" → 解答/Solution to等
- "Solution" → 解答/Solution等（solution_follow_exercise模式）

翻译使用 `sphinx.locale.get_translation()` 获取，通过 `_(text)` 或 `translate(text)` 调用。

### 自定义翻译

可以通过 Sphinx 的 `locale_dirs` 配置添加或覆盖翻译：

```python
locale_dirs = ['locale/']  # 项目自定义翻译目录
gettext_compact = False
```

在 `locale/zh_CN/LC_MESSAGES/exercise.po` 中提供中文翻译。

## CSS 自定义

sphinx-exercise 自动加载 `exercise.css`。要自定义样式：

1. **完全替换**：在 `html_static_path` 中提供自定义 `exercise.css`（优先级更高）
2. **追加样式**：在自定义 CSS 文件中覆盖 `.exercise`、`.solution` 相关类

关键 CSS 类：

| 类名 | 元素 |
|------|------|
| `.exercise` | 练习容器 |
| `.exercise-header` | 练习标题栏 |
| `.exercise-number` | 练习编号 |
| `.exercise-title` | 练习副标题 |
| `.exercise-content` | 练习内容区 |
| `.solution` | 解答容器 |
| `.solution-header` | 解答标题栏 |

## LaTeX 配置

sphinx-exercise 注册了 LaTeX builder 的 visit/depart 方法，LaTeX 输出使用 `exercise_latex_number_reference` 节点处理编号引用。LaTeX 样式通过 `latex.py` 中的方法定义。

## 并行构建

sphinx-exercise 声明 `parallel_read_safe: True, parallel_write_safe: True`，正确实现了：

- `env-purge-doc` 事件清理当前文档的注册表条目
- `env-merge-info` 事件合并并行进程的注册表数据
- `doctree-read` 事件跟踪节点顺序

## 相关概念

- [练习指令详解](/concepts/02-exercise-directive.md)
- [解答指令详解](/concepts/03-solution-directive.md)
- [教师版/学生版示例](/examples/hide-solutions.md)
