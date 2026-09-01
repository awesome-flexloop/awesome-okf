---
type: concept
title: 配置系统（myst-config）
description: myst-config 包提供三级配置体系——项目配置、站点配置和错误规则，通过 myst.yml 文件定义，支持插件注册、导航菜单、错误级别覆盖等。
tags: [mystmd, config, myst.yml, project, site, error-rules]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/myst-config-source.md"
    facts: [F-084, F-085, F-086, F-087, F-088, F-089, F-090, F-091, F-092, F-093]
  - path: "/references/simple-validators-source.md"
    facts: []
---

## 配置体系概述

MyST 的配置通过项目根目录的 `myst.yml` 文件定义，包含三个层级：

```yaml
version: 1              # 配置版本（必须为 1）
extend:                 # 继承其他配置文件（可选）
  - ./common.yml

project:                # 项目级配置
  title: 我的项目
  # ... ProjectFrontmatter + 项目特有字段

site:                   # 站点级配置
  title: 我的站点
  # ... SiteFrontmatter + 站点特有字段
```

## 配置版本

```ts
const VERSION = 1;

type Config = {
  version: 1;
  extend?: string[];
  project?: ProjectConfig;
  site?: SiteConfig;
};
```

当前配置版本为 1。`extend` 字段支持继承多个配置文件（数组形式），后者覆盖前者。

## ProjectConfig（项目配置）

```ts
type ProjectConfig = ProjectFrontmatter & {
  remote?: string;           // 远程项目 Git URL
  index?: string;            // 首页文件路径（默认 index.md）
  exclude?: string[];        // 排除的文件 glob 模式
  plugins?: PluginInfo[];    // 插件列表
  error_rules?: ErrorRule[]; // 错误级别覆盖规则
};
```

ProjectConfig 继承 ProjectFrontmatter（来自 myst-frontmatter），因此同时支持所有 frontmatter 字段（title/authors/bibliography/math/numbering 等）。

### PluginInfo（插件信息）

```ts
type PluginInfo = {
  type: PluginTypes;    // 插件类型
  path: string;         // 插件路径（本地路径或 npm 包名）
};

enum PluginTypes {
  javascript = 'javascript',  // JS/TS 插件（直接 import）
  executable = 'executable',  // 可执行插件（子进程调用）
}
```

插件加载流程：
1. 读取 myst.yml 中 plugins 数组
2. 根据 path 解析插件位置（相对路径→绝对路径，npm 包名→node_modules）
3. import/require 插件模块
4. 验证插件导出是否符合 MystPlugin 接口
5. 合并 directives/roles/transforms 到解析器配置
6. 记录插件路径到 ValidatedMystPlugin.paths

### exclude 模式

```yaml
project:
  exclude:
    - 'drafts/**'       # 排除 drafts 目录
    - '*.tmp.md'        # 排除临时文件
    - 'README.md'       # 排除 README
```

## SiteConfig（站点配置）

```ts
type SiteConfig = SiteFrontmatter & {
  projects?: SiteProject[];    // 子项目（已 deprecated）
  nav?: SiteNavItem[];         // 导航菜单
  actions?: SiteAction[];      // 操作按钮
  domains?: string[];          // 域名绑定
  template?: string;           // 站点模板
};
```

### SiteNavItem（导航菜单项）

```ts
type SiteNavItem = {
  title: string;
  url?: string;                // 链接 URL（叶子节点必须有）
  internal?: boolean;          // 是否内部链接
  children?: SiteNavItem[];    // 子菜单（嵌套导航）
  static?: boolean;            // 是否静态资源
};
```

导航菜单支持无限层级嵌套，构建时自动展开为树形结构。

### SiteAction（操作按钮）

```ts
type SiteAction = {
  title: string;               // 按钮文本
  url: string;                 // 链接 URL
  filename?: string;           // 下载文件名
  format?: ExportFormats;      // 导出格式（pdf/docx/tex 等）
  internal?: boolean;
  static?: boolean;
};
```

操作按钮通常用于下载 PDF/源文件、外部链接等。format 字段用于标识导出格式，影响图标和行为。

### SiteProject（子项目引用）

```ts
type SiteProject = {
  slug?: string;               // URL 路径前缀
  remote?: string;             // 远程 Git URL
  path?: string;               // 本地路径
};
```

> 注意：`projects` 字段已 deprecated，推荐使用 monorepo 结构或直接在 path 中引用子目录。

### SiteExport（导出项）

```ts
type SiteExport = {
  url: string;                 // 导出文件 URL
  filename: string;            // 文件名
  format?: ExportFormats;      // 格式
};
```

### SiteManifest（构建后清单）

```ts
type SiteManifest = {
  version: number;             // 清单版本
  myst: string;                // mystmd 版本
  id?: string;                 // 站点 ID
  projects?: SiteProject[];
  nav?: SiteNavItem[];
  actions?: SiteAction[];
  domains?: string[];
  favicon?: string;
  template?: string;
  parts?: Record<string, any>;
};
```

SiteManifest 在构建后生成，部署到站点根目录，用于运行时导航和资源查找。

## ErrorRule（错误规则）

```ts
type ErrorRule = {
  id: string;                          // RuleId 枚举值
  severity: 'ignore' | 'warn' | 'error';  // 覆盖后的严重级别
  key?: string;                        // 可选的键匹配
} & Record<string, any>;               // 允许额外的过滤条件
```

ErrorRule 允许用户覆盖特定规则的默认严重级别：

```yaml
project:
  error_rules:
    # 忽略未知指令错误
    - id: unknownDirective
      severity: ignore
    
    # 将图片缺少alt文本升级为错误
    - id: imageAltText
      severity: error
    
    # 仅忽略特定key的重复标识符
    - id: duplicateIdentifier
      key: my-section
      severity: warn
    
    # 忽略外部链接检查
    - id: externalLinkNotFound
      severity: ignore
```

规则匹配逻辑：
1. 遍历 error_rules 数组
2. 第一条 id 匹配且 key 匹配（或无 key）的规则生效
3. 无匹配规则使用默认严重级别

## 配置验证

每个配置类型都有对应的验证器（使用 simple-validators 包）：

- `validateProjectConfig` — 验证项目配置
- `validateSiteConfig` — 验证站点配置
- `validateErrorRule` — 验证错误规则

验证器检查：
- 必填字段是否存在
- 字段类型是否正确
- 枚举值是否有效
- URL/域名/邮箱格式是否合法
- 互斥字段是否冲突

验证错误/警告通过 VFile messages 上报。

## 配置加载流程

```
myst.yml 读取
     │
     ▼
YAML 解析
     │
     ▼
extend 继承合并
     │ (递归加载 extend 中的文件，后定义的覆盖先定义的)
     ▼
版本验证（version 必须为 1）
     │
     ▼
project 验证 + site 验证
     │
     ▼
项目级 Frontmatter 与默认值合并
     │ (fillProjectFrontmatter)
     ▼
error_rules 注册
     │
     ▼
插件加载与验证
     │ (读取 plugins 数组，import 模块，验证 MystPlugin 接口)
     ▼
有效配置对象 → 传递给 build/start 命令
```

## 配置文件示例

### 最小配置

```yaml
version: 1
project:
  title: 我的文档
site:
  title: 我的文档站点
```

### 完整配置

```yaml
version: 1
project:
  title: MyST 文档指南
  description: 使用 MyST Markdown 编写技术文档
  authors:
    - name: 作者名
      email: author@example.com
  license: CC-BY-4.0
  bibliography: references.bib
  math:
    '\R': '\mathbb{R}'
  numbering:
    figure: true
    table: true
    equation: true
  plugins:
    - type: javascript
      path: ./plugins/exercise.mjs
  error_rules:
    - id: unknownDirective
      severity: ignore
  exclude:
    - drafts/**

site:
  title: MyST 文档指南
  logo: logo.png
  favicon: favicon.ico
  domains:
    - docs.example.com
  nav:
    - title: 首页
      url: /
    - title: 指南
      children:
        - title: 快速开始
          url: /quickstart
        - title: 语法参考
          url: /syntax
    - title: API
      url: /api
  actions:
    - title: GitHub
      url: https://github.com/example/repo
    - title: 下载 PDF
      url: /book.pdf
      format: pdf
  template: book-theme
```

## 相关概念

- [Frontmatter 元数据系统](08-frontmatter.md)
- [错误处理与规则 ID](05-error-handling.md)
- [统一插件架构](01-unified-plugin-architecture.md)
- [CLI 工具链](11-cli-toolchain.md)
