---
type: Example
title: 基本CLI使用
description: jcache CLI的基本操作流程：初始化、添加Notebook、执行、查看缓存和匹配状态
tags: [jupyter, cache, cli, example, basic-usage]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T04:50:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: jc-source
    resource: /references/cache-source.md
    title: jupyter-cache 源码路径映射
---

# 基本CLI使用

## 完整工作流示例

以下是使用 jupyter-cache 的典型CLI工作流。

### 步骤1：初始化缓存

```bash
# 查看项目信息（首次运行自动创建缓存）
jcache project info
```

输出：
```
Cache path: /myproject/.jupyter_cache
Cache version: 1.0.1
Project notebooks: 0
Cached notebooks: 0
```

### 步骤2：添加Notebook到项目

假设项目有以下Notebook：

```
notebooks/
├── 01_intro.ipynb
├── 02_data_analysis.ipynb
└── 03_visualization.ipynb
```

```bash
# 添加所有Notebook
jcache notebook add notebooks/*.ipynb
```

输出：
```
Adding: notebooks/01_intro.ipynb
Adding: notebooks/02_data_analysis.ipynb
Adding: notebooks/03_visualization.ipynb
```

### 步骤3：查看项目Notebook状态

```bash
jcache notebook list
```

输出：
```
ID  URI                     Reader      Added           Status  Assets
1   notebooks/01_intro.ipynb filesystem  2026-08-23 12:00  -      0
2   notebooks/02_data_...   filesystem  2026-08-23 12:00  -      0
3   notebooks/03_visua...   filesystem  2026-08-23 12:00  -      0
```

Status列显示"-"表示尚未执行/缓存。

### 步骤4：执行Notebook

```bash
# 执行所有未缓存的Notebook
jcache notebook execute-all
```

首次执行会启动Jupyter Kernel，逐Notebook执行。执行完成后：

```
Executing: notebooks/01_intro.ipynb ✓
Executing: notebooks/02_data_analysis.ipynb ✓
Executing: notebooks/03_visualization.ipynb ✓
Successfully executed: 3/3
```

### 步骤5：再次查看状态

```bash
jcache notebook list
```

```
ID  URI                     Reader      Added           Status   Assets
1   notebooks/01_intro.ipynb filesystem  2026-08-23 12:00  ✅ [1]   0
2   notebooks/02_data_...   filesystem  2026-08-23 12:00  ✅ [2]   0
3   notebooks/03_visua...   filesystem  2026-08-23 12:00  ✅ [3]   0
```

Status列显示"✅ [ID]"表示已缓存，括号内是缓存记录ID。

### 步骤6：查看缓存列表

```bash
jcache cache list
```

```
ID  Origin URI              Created           Accessed
1   notebooks/01_intro....  2026-08-23 12:05  2026-08-23 12:05
2   notebooks/02_data....  2026-08-23 12:06  2026-08-23 12:06
3   notebooks/03_visua...  2026-08-23 12:08  2026-08-23 12:08
```

### 步骤7：增量构建——缓存命中

修改 `02_data_analysis.ipynb` 中的代码后再次执行：

```bash
jcache notebook execute-all
```

```
Executing: notebooks/01_intro.ipynb (cached, skipped)
Executing: notebooks/02_data_analysis.ipynb (changed, executing...) ✓
Executing: notebooks/03_visualization.ipynb (cached, skipped)
Successfully executed: 1/3 (2 from cache)
```

未修改的Notebook直接从缓存读取，只有修改的Notebook重新执行。

### 步骤8：查看缓存详情

```bash
jcache cache show 2
```

显示缓存记录详情：hashkey、数据字段、创建时间、访问时间。

### 步骤9：清理

```bash
# 删除特定缓存
jcache cache remove 1

# 清空所有缓存（保留项目记录）
jcache cache clear

# 清空项目记录（保留缓存）
jcache project clear
```

## 添加带关联资源的Notebook

```bash
# 添加需要数据文件的Notebook（assets通过API指定，CLI需在Notebook中引用）
jcache notebook add notebooks/analysis.ipynb
```

## 指定缓存路径

```bash
# 使用全局路径（如CI缓存目录）
jcache -p ~/.cache/jupyter-cache notebook add *.ipynb
jcache -p ~/.cache/jupyter-cache notebook execute-all
```

## 设置缓存大小限制

```bash
# 限制最多缓存100个Notebook
jcache cache limit 100
```

## 错误处理场景

### 执行失败

```bash
jcache notebook execute-all
```

如果某个Notebook执行失败：

```
ID  URI                Status
1   notebooks/good.ipynb  ✅ [1]
2   notebooks/bad.ipynb   ❌
```

查看详情后修复Notebook，然后：

```bash
# 清除错误状态并重新执行
jcache notebook remove 2
jcache notebook add notebooks/bad.ipynb
jcache notebook execute-all
```

## 相关示例

- [Python API编程](/examples/python-api.md)
- [CI集成与缓存策略](/examples/ci-integration.md)

## 相关概念

- [CLI命令详解](/concepts/05-cli-reference.md)
- [快速开始](/concepts/01-getting-started.md)
- [缓存架构设计](/concepts/02-architecture.md)
