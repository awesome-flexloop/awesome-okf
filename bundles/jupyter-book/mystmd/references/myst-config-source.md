---
type: Reference
title: myst-config 配置系统源码信源
description: myst-config 包的配置类型定义（Config/ProjectConfig/SiteConfig/ErrorRule）、验证器以及站点清单类型的源码登记。
tags: [mystmd, config, project, site, error-rules, validation]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "myst-config/src/index.ts"
    facts: [F-084]
  - path: "myst-config/src/project/types.ts"
    facts: [F-085, F-086, F-087]
  - path: "myst-config/src/site/types.ts"
    facts: [F-088, F-089, F-090, F-091, F-093]
  - path: "myst-config/src/errorRules/types.ts"
    facts: [F-092]
---

## 源码位置

- `myst-config/src/index.ts` — 包入口与 Config 类型
- `myst-config/src/project/types.ts` — ProjectConfig、PluginInfo、PluginTypes、VERSION
- `myst-config/src/project/validators.ts` — 项目配置验证器
- `myst-config/src/project/index.ts` — 项目配置模块导出
- `myst-config/src/site/types.ts` — SiteConfig、SiteNavItem、SiteAction、SiteProject、SiteManifest、SiteExport
- `myst-config/src/site/validators.ts` — 站点配置验证器
- `myst-config/src/site/index.ts` — 站点配置模块导出
- `myst-config/src/errorRules/types.ts` — ErrorRule 类型
- `myst-config/src/errorRules/validators.ts` — 错误规则验证器
- `myst-config/src/errorRules/index.ts` — 错误规则模块导出

## 核心类型

### 顶层配置

| 类型 | 定义 | 说明 |
|------|------|------|
| `Config` | `{ version: 1; extend?: string[]; project?: ProjectConfig; site?: SiteConfig }` | myst.yml 顶层配置结构 |
| `VERSION` | `= 1` | 配置版本常量 |

### 项目配置

| 类型 | 定义 | 说明 |
|------|------|------|
| `ProjectConfig` | `ProjectFrontmatter & { remote?; index?; exclude?; plugins?: PluginInfo[]; error_rules?: ErrorRule[] }` | 项目级配置，扩展 ProjectFrontmatter |
| `PluginInfo` | `{ type: PluginTypes; path: string }` | 插件信息 |
| `PluginTypes` | `enum { javascript = 'javascript', executable = 'executable' }` | 插件类型枚举 |

ProjectConfig 继承自 myst-frontmatter 的 ProjectFrontmatter，后者包含：title、description、authors、affiliations、funding、license、bibliography、math、numbering、exports、downloads、requirements、thebe、kernelspec 等字段。

### 站点配置

| 类型 | 定义 | 说明 |
|------|------|------|
| `SiteConfig` | `SiteFrontmatter & { projects?: SiteProject[]; nav?: SiteNavItem[]; actions?: SiteAction[]; domains?: string[]; template?: string }` | 站点级配置 |
| `SiteProject` | `{ slug?; remote?; path? }` | 站点项目引用（projects 已 deprecated） |
| `SiteNavItem` | `{ title: string; url?; internal?; children?: SiteNavItem[]; static? }` | 导航菜单项（支持嵌套） |
| `SiteAction` | `{ title: string; url: string; filename?; format?: ExportFormats; internal?; static? }` | 操作按钮（如下载链接） |
| `SiteExport` | `{ url: string; filename: string; format?: ExportFormats }` | 导出项 |
| `SiteManifest` | `{ version: number; myst: string; id?; projects?; nav?; actions?; domains?; favicon?; template?; parts? }` | 构建后的站点清单 |

SiteConfig 继承自 myst-frontmatter 的 SiteFrontmatter，后者包含：title、description、logo、favicon、domains 等字段。

### 错误规则

| 类型 | 定义 | 说明 |
|------|------|------|
| `ErrorRule` | `{ id: string; severity: 'ignore'\|'warn'\|'error'; key?: string } & Record<string, any>` | 规则严重级别覆盖 |

ErrorRule 通过 id 匹配 RuleId，severity 覆盖默认严重级别。id 对应 myst-common 中 RuleId 枚举值（80+ 种规则）。

## 配置文件结构（myst.yml）

```yaml
version: 1
project:
  title: 项目标题
  # ... 其他 ProjectFrontmatter 字段
  plugins:
    - type: javascript
      path: ./plugins/my-plugin.mjs
  error_rules:
    - id: directive-known
      severity: ignore
site:
  title: 站点标题
  nav:
    - title: 首页
      url: /
    - title: 文档
      children:
        - title: 指南
          url: /guide
  actions:
    - title: 下载 PDF
      url: /docs/book.pdf
      format: pdf
  domains:
    - example.com
```
