---
type: concept
title: "主题架构：三层分离与组件组合"
description: "myst-theme �?monorepo 架构——样式基础层、组件库层、主题应用层的职责划分与组合方式"
bundle: myst-theme
sources:
  - /references/structure-styles-src.md
  - /references/myst-to-react-providers-src.md
  - /references/themes-book-article-src.md
related:
  - 01-css-variables-theming.md
  - 02-grid-layout-system.md
  - 03-myst-rendering.md
  - 04-theme-providers.md
  - 05-thebe-interactive.md
tags: [myst-theme, concept]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
---

# 主题架构：三层分离与组件组合

## 核心理念

myst-theme 采用**三层分离**�?monorepo 架构，每一层有明确的职责边界和依赖方向。底层为上层提供能力，上层组合下层组件，各层独立发布和版本管理�?
## 三层架构

```
┌─────────────────────────────────────────────────────�?�? 主题应用层（themes/�?                              �?�? Book 主题  �? Article 主题                         �?�? - Remix SSR 路由                                   �?�? - 站点级布局（导�?侧边�?页脚�?                    �?�? - 服务器端数据加载                                  �?�? - 组合 packages 中的组件                           �?├─────────────────────────────────────────────────────�?�? 组件库层（packages/�?                              �?�? myst-to-react �?providers �?site �?frontmatter     �?�? jupyter �?diagrams �?search �?icons �?...          �?�? - 可复�?React 组件                                �?�? - MDAST→React 渲染�?                              �?�? - Context Provider 系统                            �?�? - Jupyter/thebe 交互组件                           �?�? - 独立 npm 包（@myst-theme/*�?                     �?├─────────────────────────────────────────────────────�?�? 样式基础层（styles/�?                              �?�? CSS Variables �?Tailwind 配置 �?CSS 模块           �?�? - 颜色系统�?-myst-color-*�?                      �?�? - 网格模板（gridTemplateColumns�?                  �?�? - Typography 覆盖                                  �?�? - 组件样式（admonition/code/proof/...�?            �?�? - 无框架依赖（�?CSS�?                             �?└─────────────────────────────────────────────────────�?```

### 依赖方向

```
themes/ �?packages/ �?styles/
```

- themes 依赖 packages �?styles
- packages 依赖 styles（通过 CSS 变量�?Tailwind 类）
- packages 之间通过 peer 依赖互相引用（如 jupyter 依赖 providers�?- styles 不依赖任�?React 组件

## 包（packages）划分策�?
14 个包�?*功能�?*划分，每个包对外暴露一个明确的 API 面：

| �?| 职责 | 被谁使用 |
|----|------|---------|
| myst-to-react | AST→React 渲染 | themes、jupyterlab-myst、外部应�?|
| providers | React Context 基础设施 | 所有需要渲�?MyST 的组�?|
| site | 站点级组�?Remix loader | themes/book、themes/article |
| frontmatter | 元数据渲染（作�?日期/下载�?| themes、myst-to-react |
| jupyter | Jupyter/thebe 交互执行 | themes、jupyterlab-myst |
| diagrams | 图表渲染（Mermaid�?| myst-to-react |
| icons | Logo 图标 | themes |
| search / search-minisearch | 全文搜索 | themes/site |
| common | 工具函数和类�?| 所�?packages |
| landing-pages | 着陆页营销组件 | 外部站点 |
| anywidget | Jupyter Widget 支持 | jupyter |
| myst-demo | 演示用组�?| 文档/示例 |

**划分原则**�?- **单一职责**：每个包专注一个功能域
- **依赖最小化**：包之间通过显式导入依赖，避免循环依�?- **独立发布**：@myst-theme/* 包发布到 npm，可被外部项目独立使�?- **可裁�?*：不需�?Jupyter 功能时，不引�?jupyter 包即�?
## 主题应用组合模式

�?Book 主题为例，展示三层如何组合：

```tsx
// themes/book/app/routes/$.tsx 简�?import { ThemeProvider } from '@myst-theme/providers';
import { Navigation, ContentBlocks } from '@myst-theme/site';
import { FrontmatterBlock } from '@myst-theme/frontmatter';
import { MyST } from '@myst-theme/myst-to-react';
import { BinderBadge, Outputs } from '@myst-theme/jupyter';
import 'myst-theme/styles/app.css';           // 引入 styles �?import '../styles/app.css';                  // 主题级样�?
export default function BookPage() {
  const { data } = useLoaderData();
  return (
    <ThemeProvider renderers={jupyterRenderers}>
      <Navigation config={data.config} />
      <article className="col-body">
        <FrontmatterBlock frontmatter={data.frontmatter}>
          <BinderBadge />
        </FrontmatterBlock>
        <ContentBlocks>
          <MyST ast={data.mdast} />
        </ContentBlocks>
      </article>
    </ThemeProvider>
  );
}
```

## �?jupyterlab-myst 的组�?
jupyterlab-myst 不需�?themes 层（不是站点），直接使用 packages 层：

```tsx
// jupyterlab-myst 只引入需要的�?import { ThemeProvider, ArticleProvider } from '@myst-theme/providers';
import { MyST } from '@myst-theme/myst-to-react';
import { FrontmatterBlock } from '@myst-theme/frontmatter';
// 不引�?@myst-theme/site（不需要站点导航）
// 不引�?themes/book �?themes/article
```

这证明了分层设计的有效性——jupyterlab-myst �?JupyterLab 环境中复用了 myst-theme 的核心渲染能力，同时完全绕过站点级组件�?
## 可扩展�?
### 新增主题

创建新的 Remix 应用，复�?packages/ �?styles/，即可快速构建新主题（如 "docs" 主题�?slide" 主题）。只需要在 themes/ 下创建新目录，配�?Remix 路由和布局�?
### 自定义渲染器

通过 ThemeProvider �?`renderers` prop 覆盖默认渲染器，无需修改 myst-to-react 源码�?
```tsx
<ThemeProvider renderers={{
  code: { base: MyCustomCodeBlock },
  admonition: {
    base: DefaultAdmonition,
    'admonition[kind=warning]': CustomWarningAdmonition,
  },
}}>
  <MyST ast={mdast} />
</ThemeProvider>
```

### 主题色定�?
通过覆盖 CSS 变量即可定制品牌色，无需修改组件�?
```css
:root {
  --myst-color-link: #0066cc;
  --myst-color-primary: #ff6600;
}
```

## 关键设计决策

1. **Remix 作为主题框架**：SSR + 文件路由 + 渐进增强，适合文档站点
2. **Tailwind CSS**：原子化 CSS + CSS 变量驱动主题，支�?JIT 按需编译
3. **CSS 变量命名空间**：`--myst-*` 前缀避免与其他库冲突
4. **unist-util-select 匹配**：CSS 选择器语法在 AST 节点上做渲染器匹配，表达力强
5. **Provider 分层**：上下文按需组合，避免单一巨型 Context
