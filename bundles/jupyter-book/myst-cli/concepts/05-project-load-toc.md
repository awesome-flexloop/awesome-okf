---
type: concept
title: "项目加载与TOC"
description: "myst-cli的项目发现、TOC解析（三种来源）、页面收集与Bibliography加载机制"
tags: [myst-cli, project, toc, configuration, bibliography]
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

# 项目加载与 TOC

项目加载是 myst-cli 构建和启动的前提，负责从磁盘发现文件结构、解析目录（TOC）、加载配置和引用数据。

## 项目加载流程

`loadProjectFromDisk()` 是核心加载函数：

```
1. 缓存检查 → 已加载且未设置 reloadProject → 直接返回
2. loadConfig() → 加载 myst.yml 配置文件
3. 确定 TOC 来源（三级优先级）
4. writeTOC 选项 → 写回 myst.yml
5. 收集并加载 BibTeX 文件
6. dispatch projects.actions.receive() → 存入 Redux
7. combineProjectCitationRenderers() → 合并引用渲染器
```

## TOC 三种来源

myst-cli 支持三种 TOC 定义方式，按优先级依次尝试：

### 优先级 1：myst.yml 中的 project.toc

```yaml
project:
  toc:
    - file: index.md
    - title: 第一章
      children:
        - file: chapter1.md
        - file: chapter2.md
    - title: 参考
      children:
        - url: https://example.com
          title: 外部链接
```

这是 MyST 推荐的新式 TOC 格式，支持：
- `file`：页面文件路径
- `title`：目录显示标题
- `children`：子页面嵌套
- `url`：外部链接
- `level`：层级控制（part/chapter/section 等）

### 优先级 2：Legacy Jupyter Book _toc.yml

```yaml
format: jb-book
root: index
chapters:
- file: chapter1
- file: chapter2
```

传统 Jupyter Book 格式，自动检测并解析。支持通过 `myst init --write-toc` 升级为新式 TOC。

### 优先级 3：文件系统自动发现

如果没有任何 TOC 定义，myst-cli 递归扫描项目目录：
- 发现 `.md`、`.ipynb`、`.myst.md` 等有效文件
- 排除 `_build`、隐藏文件、配置文件
- 遇到子目录中的 myst.yml 或 _toc.yml 时停止递归（子项目边界）
- 按文件名排序生成隐式 TOC
- 隐式页面标记 `implicit: true`

## 页面层级

```ts
type PageLevels = -1 | 0 | 1 | 2 | 3 | 4 | 5 | 6;
// -1 = part（部分）
//  0 = chapter（章）
//  1-6 = 对应 Markdown 标题级别 h1-h6
```

## LocalProject 数据结构

```ts
type LocalProject = {
  path: string;                    // 项目根目录绝对路径
  file: string;                    // 首页/索引文件路径
  index: string;                   // 首页的 URL slug
  implicitIndex?: boolean;         // 首页是否为隐式发现
  bibliography: string[];          // BibTeX 文件路径列表
  pages: (LocalProjectPage | LocalProjectFolder | ExternalURL)[];
};
```

pages 数组是三种类型的联合：
- **LocalProjectPage**：实际文件页面，含 file/slug/level/title/implicit
- **LocalProjectFolder**：文件夹/分组节点，含 title/level
- **ExternalURL**：外部链接，含 url/title/level

## Bibliography 加载

引用文件（.bib）有两个来源：

1. **自动发现**：`getAllBibTexFilesOnPath()` 扫描项目目录下所有 .bib 文件
2. **配置声明**：`project.bibliography` 数组中显式列出的文件

如果配置中声明了 bibliography：
- 验证每个文件存在（或为 URL）
- 不存在的文件产生警告
- 自动发现但未配置的文件输出 debug 日志

如果未声明 bibliography：使用所有自动发现的 .bib 文件。

所有 .bib 文件通过 `loadFile()` 加载，后续由引用转换器解析。

## 多项目支持

- `findProjectsOnPath()`：递归扫描目录树，查找所有包含 myst.yml 且有 project 配置的子目录
- `getProjectPaths()`：收集当前站点关联的所有项目路径（主项目 + site.projects 中声明的子项目）
- 多项目站点中，每个项目独立加载和缓存

## 缓存机制

已加载的项目通过 Redux store 缓存（key 为绝对路径）。设置 `reloadProject: true` 可以强制重新加载。

## TOC 写回

`--write-toc` 选项（在 init 命令中使用）会将解析后的 TOC 结构写回 myst.yml 配置文件：
- Legacy TOC 存在时：显示升级提示信息
- 无 TOC 时：从文件系统结构生成并写入

## 相关概念

- [Init 项目初始化](03-init-project.md) — init 命令如何触发 TOC 生成
- [Store 状态管理](09-store-state.md) — Redux 中项目状态的存储
- [会话与缓存](08-session-cache.md) — Session 级别的项目缓存
