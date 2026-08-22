---
type: reference
title: "myst-cli 项目加载源码"
description: "project/load.ts 中的项目发现、TOC解析、配置加载与页面收集逻辑"
tags: [myst-cli, project, load, toc, configuration]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/project/load.ts"
    facts: [F-030, F-031, F-032, F-033, F-034]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/project/types.ts"
    facts: [F-035, F-036, F-037]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/project/fromPath.ts"
    facts: [F-038]
---

# 项目加载源码分析

## loadProjectFromDisk() 核心流程

这是项目加载的主入口函数，负责从磁盘加载项目结构和配置。

```
1. 缓存检查：selectLocalProject() 检查是否已加载，未设置 reloadProject 时直接返回缓存
2. loadConfig()：加载 myst.yml 配置文件
3. 确定 TOC 来源（三级优先级）：
   a. projectConfig.toc 存在 → projectFromTOC() 解析新格式 TOC
   b. _toc.yml 存在 → projectFromSphinxTOC() 解析 legacy Jupyter Book TOC
   c. 均不存在 → projectFromPath() 文件系统遍历
4. writeTOC 选项：将 TOC 写回 myst.yml 配置文件
5. 收集 BibTeX 文件：getAllBibTexFilesOnPath() + 配置中声明的 bibliography
6. loadFile() 加载所有 .bib 文件
7. dispatch projects.actions.receive() 存入 Redux store
8. combineProjectCitationRenderers() 合并引用渲染器
```

## TOC 三种来源详解

### 1. myst.yml TOC（projectFromTOC）

在 myst.yml 中通过 `project.toc` 字段定义的新式 TOC：

```yaml
project:
  toc:
    - file: index.md
    - title: Chapter 1
      children:
        - file: chapter1.md
```

优先级最高，存在时忽略 legacy _toc.yml。

### 2. Legacy Jupyter Book _toc.yml

传统 Jupyter Book 格式的 `_toc.yml` 文件，通过 `validateSphinxTOC()` 验证，使用 `projectFromSphinxTOC()` 解析。支持 `--write-toc` 选项自动升级为新式 TOC。

### 3. 文件系统自动发现（projectFromPath）

当没有显式 TOC 定义时，递归扫描目录中的有效文件（.md/.ipynb/.myst.md 等），自动生成隐式 TOC。扫描规则：
- 排除 `_build` 目录、隐藏文件、配置文件
- 遇到子目录中的 myst.yml 或 _toc.yml 时停止递归（子项目边界）
- 按文件名排序生成页面列表

## 类型定义

```ts
type PageLevels = -1 | 0 | 1 | 2 | 3 | 4 | 5 | 6;
// -1 = part, 0 = chapter, 1-6 = heading levels

type LocalProjectPage = {
  file: string;       // 文件绝对路径
  slug: string;       // URL slug
  level: PageLevels;  // 层级
  title?: string;     // 可选短标题
  implicit?: boolean; // 是否从模式/目录隐式生成
};

type LocalProjectFolder = {
  title: string;
  level: PageLevels;
};

type ExternalURL = {
  url: string;
  title: string;
  level: PageLevels;
  open_in_same_tab?: boolean;
};

type LocalProject = {
  path: string;
  file: string;           // 索引文件路径
  index: string;          // 首页 slug
  implicitIndex?: boolean;
  bibliography: string[]; // BibTeX 文件路径列表
  pages: (LocalProjectPage | LocalProjectFolder | ExternalURL)[];
};
```

## 辅助函数

- `findProjectsOnPath()`：递归扫描目录树查找所有包含 myst.yml 且定义了 project 配置的子目录，返回项目路径列表。用于多项目站点的构建。
- `filterPages()`：从 LocalProject 中提取扁平的页面列表（首页 + 所有有 file 属性的页面），排除文件夹和外部 URL。用于遍历构建所有页面。

## Bibliography 处理

BibTeX 文件有两个来源：
1. 自动发现：`getAllBibTexFilesOnPath()` 扫描项目路径下所有 .bib 文件
2. 配置声明：`projectConfig.bibliography` 数组中显式列出的文件

如果配置中声明了 bibliography，则仅使用配置中的文件（并验证存在性），同时对未引用但存在的 .bib 文件输出 debug 日志。如果未声明，则使用所有自动发现的 .bib 文件。
