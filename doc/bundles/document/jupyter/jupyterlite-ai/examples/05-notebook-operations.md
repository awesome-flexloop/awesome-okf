---
type: Example
title: "AI 操作 Notebook"
description: "让 AI 直接操作 Jupyter Notebook：创建单元格、编写代码、运行分析、生成可视化"
tags: [jupyterlite-ai, notebook, code-execution, jupyter, cells]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-04-21T00:00:00+08:00" }
status: stable
stale_after: 2026-10-21
sources:
  - id: source
    resource: /references/source-code.md
    title: 源码结构与核心文件索引
  - id: tools
    resource: /references/built-in-tools.md
    title: 内置 AI 工具参考
---

# AI 操作 Notebook

JupyterLite AI 最强大的能力之一是直接操作 Notebook——创建单元格、插入代码、运行分析、生成可视化。本教程介绍如何利用这一能力。

## AI 能对 Notebook 做什么？

| 操作 | 说明 | 工具 |
|------|------|------|
| 读取 Notebook 内容 | 查看所有单元格的内容和输出 | 内置能力 |
| 插入单元格 | 在指定位置插入代码或 Markdown 单元格 | execute_command |
| 运行单元格 | 执行代码单元格 | execute_command |
| 运行所有单元格 | 按顺序执行整个 Notebook | execute_command |
| 删除单元格 | 移除指定单元格 | execute_command |
| 移动单元格 | 调整单元格顺序 | execute_command |

## 基础操作

### 插入并运行代码

直接告诉 AI 你想要什么：

```
在当前单元格下面插入一个代码单元格，写一个用 pandas 读取 CSV 文件的示例，然后运行它
```

AI 会：
1. 使用 `discover_commands` 找到可用的 Notebook 命令
2. 使用 `execute_command` 插入代码单元格
3. 代码内容是读取 CSV 的 pandas 示例
4. 你批准后执行插入命令

### Markdown 单元格

```
在 Notebook 顶部插入一个 Markdown 单元格，写标题"销售数据分析"和简要说明
```

### 运行现有代码

```
运行 Notebook 中所有单元格
```

```
运行当前选中的单元格下面的所有单元格
```

## 实战场景

### 场景1：数据加载与初步探索

**提问**：
```
我刚上传了一个 sales.csv 文件，请帮我：
1. 新建一个代码单元格读取这个 CSV 文件
2. 显示数据前5行
3. 打印数据基本信息（形状、列类型、缺失值）
```

### 场景2：数据可视化

**提问**：
```
基于已加载的数据，帮我：
1. 创建一个新的代码单元格
2. 画一个按月的销售额趋势折线图
3. 用 matplotlib，设置中文标题，加上数据标签
4. 运行并展示结果
```

### 场景3：数据清洗

**提问**：
```
请检查 df 中的缺失值和异常值，生成清洗代码：
1. 先统计每列的缺失值比例
2. 对数值列用中位数填充缺失值
3. 对分类列用众数填充
4. 删除重复行
5. 清洗完成后报告数据形状变化
```

### 场景4：完整分析流程

**提问**：
```
请帮我做一个完整的探索性数据分析（EDA），按以下步骤：
1. 数据概览（info, describe, head）
2. 缺失值处理
3. 数值列分布可视化（直方图+箱线图）
4. 相关性热力图
5. 关键发现总结

每个步骤创建一个单独的代码单元格并运行，中间用 Markdown 单元格添加步骤说明。
```

## 代码插入方式

AI 生成代码后，你可以选择：

1. **自动插入并运行**：AI 通过 execute_command 直接插入到 Notebook 并运行（需要审批）
2. **复制粘贴**：从聊天面板复制代码，手动粘贴到 Notebook
3. **插入到新单元格**：点击代码块旁的"插入到 Notebook"按钮

## 最佳实践

### 1. 分步操作，及时验证

不要一次性要求 AI 完成整个复杂分析，分步进行：

```
第一步：先读取数据并显示基本信息
（验证结果后）
第二步：现在帮我做数据清洗
（验证结果后）
第三步：接下来做可视化分析
```

### 2. 明确指定变量名

```
将读取的数据赋值给变量 df_taxi，不要用 df
```

### 3. 要求解释

```
写完代码后，请简要解释每一步做了什么
```

### 4. 错误处理

如果 AI 生成的代码运行出错，直接将错误信息反馈给 AI：

```
运行后报错了：TypeError: unsupported operand type(s) for +: 'int' and 'str'
请修复这个问题
```

### 5. 检查中间结果

关键步骤后检查结果是否符合预期，避免错误累积。

## 安全提示

⚠️ AI 操作 Notebook 是通过 JupyterLab 命令系统执行的：
- 命令执行需要你手动审批（除非已开启自动批准）
- AI 不能直接执行任意 shell 命令，只能调用 JupyterLab 注册的命令
- 删除单元格等破坏性操作建议先确认
- 建议在重要 Notebook 上操作前保存备份
