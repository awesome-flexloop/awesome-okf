---
type: Concept
title: 输出格式系统
description: nbviewer格式字典字段定义、三种内置格式详解、format_handlers路由复制和运行时格式过滤
tags:
  - jupyter
  - nbviewer
  - format
  - exporter
  - nbconvert
generated:
  by: "reference_agent/trae-cn"
  at: "2026-08-22T10:00:00Z"
status: stable
stale_after: 2027-08-22
sources:
  - ../../../../../external/libs/jupyter/nbviewer/nbviewer/formats.py
  - ../../../../../external/libs/jupyter/nbviewer/nbviewer/handlers.py
---

# 输出格式系统

格式系统定义Notebook可以被转换为哪些输出类型，每种类型对应一个nbconvert Exporter。

## 格式字典字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `exporter` | class/instance | 是 | nbconvert Exporter类或实例（configure_formats填充） |
| `nbconvert_template` | str | 否 | nbconvert模板名 |
| `label` | str | 是 | 显示名称（格式切换菜单） |
| `icon` | str | 是 | CSS图标类名 |
| `content_type` | str | 否 | Content-Type，默认text/html |
| `test` | function | 否 | 条件可用性检查函数(nb, json)→bool |
| `postprocess` | function | 否 | 渲染后处理钩子 |

## 三种内置格式

### html（默认）
- Exporter：HTMLExporter（lab模板）
- Content-Type：text/html; charset=UTF-8
- 始终可用，无test函数
- 图标：book，标签：Notebook

### slides
- Exporter：SlidesExporter（Reveal.js幻灯片）
- Content-Type：text/html; charset=UTF-8
- **条件可用**：test_slides检查cell.metadata.slideshow.slide_type是否存在非"-"值
- 图标：gift，标签：Slides

### script
- Exporter：ScriptExporter（可执行脚本）
- Content-Type：text/plain; charset=UTF-8
- 始终可用
- 图标：code，标签：Code

## configure_formats() 初始化

应用启动时执行：
1. 调用default_formats()获取格式定义
2. 配置nbconvert额外模板路径（templates/nbconvert/）
3. 通过get_exporter(key)获取Exporter类
4. 线程模式：创建Exporter实例（单例复用）
5. 进程模式：存储Exporter类（实例不可pickle，子进程延迟实例化）

## format_handlers() 路由复制

为每种格式复制所有Provider路由：

```python
(prefix + url, handler, {"format": format, "format_prefix": prefix})
# prefix = "/format/html", "/format/slides", "/format/script"
```

通过format参数注入Handler.initialize()，决定使用哪个Exporter渲染。原始路由使用default_format（html）。

## filter_formats() 运行时过滤

渲染Notebook时确定格式菜单中显示哪些格式：无test的始终通过，test返回True的通过，异常时跳过。例如没有slideshow元数据的Notebook只显示Notebook和Code选项。

## 相关文档

- [Notebook渲染管线](06-render-pipeline.md)
- [Handler继承体系](04-handler-hierarchy.md)
