---
type: Reference
title: "版本转换converter源码"
description: "converter.py中convert()递归逐步转换逻辑，版本升级/降级路径与错误检测"
tags: [converter, convert, upgrade, downgrade, version-migration]
sources:
  - id: converter-py
    resource: "../../../../../external/libs/jupyter/nbformat/nbformat/converter.py"
    title: "nbformat/converter.py"
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T10:00:00Z" }
status: stable
stale_after: 2027-12-31
---

# 版本转换converter源码

## convert() 核心逻辑

```python
def convert(nb, to_version):
```

convert() 实现**递归逐步版本转换**，核心逻辑如下：

### 升级路径（to_version > 当前版本）

```python
if to_version > from_version:
    step_version = from_version + 1
    convert_function = versions[step_version].upgrade
```

逐级调用 `versions[v+1].upgrade(nb)`，每步将版本号+1，直到达到目标版本。

### 降级路径（to_version < 当前版本）

```python
elif to_version < from_version:
    step_version = from_version - 1
    convert_function = versions[from_version].downgrade
```

逐级调用 `versions[v].downgrade(nb)`，每步将版本号-1，直到达到目标版本。

### 转换后验证

每步转换后检查版本号确实变化了：

```python
converted = convert_function(nb)
if converted.get("nbformat", 1) == version:
    raise ValueError("Failed to convert notebook from v%d to v%d." % (version, step_version))
```

如果版本号未变化，说明upgrade/downgrade函数有bug，抛出ValueError。

[F-055]

### 递归终止条件

当版本号等于目标版本时返回：

```python
elif to_version == from_version:
    return nb
```

## 转换链路示例

| 源版本 | 目标版本 | 转换路径 |
|--------|---------|---------|
| v1 | v4 | v1.upgrade→v2 → v2.upgrade→v3 → v3.upgrade→v4 |
| v4 | v1 | v4.downgrade→v3 → v3.downgrade→v2 → v2.downgrade→v1 |
| v2 | v4 | v2.upgrade→v3 → v3.upgrade→v4 |
| v3 | v4 | v3.upgrade→v4（由v4.convert.upgrade处理） |

每个版本模块（v1/v2/v3/v4）在 `__init__.py` 中导出 `upgrades`（该版本能升级到哪些版本）和 `downgrade`（该版本能降级到哪些版本）。

## 版本模块接口契约

每个版本模块（v1-v4）必须提供：

| 接口 | 说明 |
|------|------|
| `nbformat` / `nbformat_minor` | 版本号常量 |
| `upgrades` | 该版本支持升级到的版本列表（通常为下一个主版本） |
| `upgrade(nb)` | 升级到下一主版本，返回新Notebook |
| `downgrade(nb)` | 降级到上一主版本，返回新Notebook（v1无downgrade） |
| `to_notebook_json(d, minor)` | dict→NotebookNode |
| `reads_json(s)` / `writes_json(nb)` | JSON序列化 |
| `new_notebook()` 等 | 工厂函数 |

## 相关信源

- [包入口公共API](init-api.md)
- [版本系统与转换概念](../concepts/05-version-system.md)
- [v4构造API](v4-nbbase-source.md)
