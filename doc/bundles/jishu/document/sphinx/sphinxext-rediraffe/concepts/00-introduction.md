---
type: Concept
title: sphinxext-rediraffe 简介
description: Sphinx 重定向扩展——自动为已删除/重命名页面生成重定向HTML，支持链式压缩、Git diff检查、自定义模板
tags: [sphinxext-rediraffe, introduction, redirect, sphinx-extension]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T16:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: rediraffe-source
    resource: /references/rediraffe-source.md
    title: sphinxext-rediraffe 源码信源登记
---

# sphinxext-rediraffe 简介

## 什么是 sphinxext-rediraffe

**sphinxext-rediraffe**（简称 rediraffe）是 Sphinx 官方生态中的页面重定向扩展，能够在文档构建完成后自动为已删除、重命名或移动的页面生成重定向 HTML 文件。当用户访问旧URL时，浏览器会自动跳转到新页面，避免出现 404 错误。

rediraffe 的核心价值体现在文档持续迭代场景中：

1. **页面移动/重命名后保持链接有效**：当文档重构导致文件路径变化时，旧链接不会断裂
2. **链式重定向自动压缩**：如果配置了多跳重定向链（A→B→C→D），rediraffe 会自动压缩为 A→D，用户最多经历一次跳转
3. **Git 集成检查**：通过 Git diff 自动检测被删除或重命名的文件，CI 中可强制要求所有变更文件都有重定向配置
4. **URL 参数保留**：重定向时保留查询参数（`?query=value`）和片段标识符（`#section`），不丢失用户导航状态

## 核心特性

| 特性 | 说明 |
|------|------|
| 多构建器支持 | 支持 `html`（StandaloneHTMLBuilder）和 `dirhtml`（DirectoryHTMLBuilder）两种构建器 |
| ReadTheDocs 兼容 | 支持 `readthedocs` 和 `readthedocsdirhtml` 构建器 |
| 两种配置方式 | 支持在 `conf.py` 中使用 dict 直接配置，或使用外部文本文件 |
| 链式重定向压缩 | 自动解析重定向链，所有路径直接指向叶子节点 |
| 循环检测 | 自动检测循环重定向（A→B→A），构建时报错终止 |
| 自定义模板 | 支持 Jinja2 模板自定义重定向页面内容 |
| Git diff 检查 | `rediraffecheckdiff` 构建器检查删除/重命名文件是否有重定向 |
| 自动写入重定向 | `rediraffewritediff` 构建器自动将高相似度重命名追加到重定向文件 |
| 增量构建 | 通过 `_rediraffe_redirected.json` 记录已生成重定向，支持增量更新 |
| 跨平台路径 | 自动处理 Windows 反斜杠和 POSIX 正斜杠路径差异 |

## 安装方法

sphinxext-rediraffe 通过 pip 安装：

```bash
pip install sphinxext-rediraffe
```

要求 Python >= 3.9，Sphinx >= 6.0。

验证安装：

```bash
pip show sphinxext-rediraffe
# Name: sphinxext-rediraffe
# Version: 0.3.0
```

## 与其他方案的对比

### vs 手动创建重定向HTML

手动为每个移动的页面写一个含 `<meta http-equiv="refresh">` 的HTML文件是最朴素的做法，但存在以下问题：

| 特性 | rediraffe | 手动创建 |
|------|-----------|---------|
| 链式压缩 | ✅ 自动解析多跳链路 | ❌ 需手动计算最终目标 |
| 循环检测 | ✅ 自动检测并报错 | ❌ 可能导致无限重定向 |
| 批量管理 | ✅ 一个配置文件管理所有重定向 | ❌ 每个重定向一个文件 |
| dirhtml适配 | ✅ 自动处理目录URL格式 | ❌ 需手动调整路径 |
| CI检查 | ✅ Git diff自动检查遗漏 | ❌ 无自动化检查 |

### vs sphinx-reredirects

`sphinx-reredirects` 是另一个社区重定向扩展，rediraffe 的区别在于：

- rediraffe 提供 Git diff 集成检查和自动写入功能，更适合CI/CD流水线
- rediraffe 的链式重定向压缩确保用户只经历一次跳转
- rediraffe 支持 ReadTheDocs 构建器
- rediraffe 是 Sphinx 官方组织维护的项目

### vs Web服务器级重定向（Nginx/Apache）

在Web服务器层配置重定向（如 Nginx 的 `rewrite` 规则）是生产环境常见方案，但：

- 需要服务器配置权限，在 ReadTheDocs/GitHub Pages 等托管平台不可用
- 文档本地预览（`sphinx-build` 直接打开HTML）时不生效
- rediraffe 生成的纯HTML重定向文件可在任何静态托管环境工作

## 典型使用场景

- **文档重构**：大规模重组文档目录结构后，保持旧链接有效
- **版本迁移**：跨版本文档结构调整时提供平滑过渡
- **CI质量门禁**：在Pull Request中检查是否有未配置重定向的删除/重命名文件
- **ReadTheDocs项目**：在RTD托管的Sphinx文档中管理页面重定向
- **本地文档预览**：开发过程中移动文件后不破坏浏览器书签和内部引用

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [架构概览](02-architecture-overview.md)
- [重定向图模型](03-redirect-graph.md)
- [sphinxext-rediraffe 源码信源登记](../references/rediraffe-source.md)
