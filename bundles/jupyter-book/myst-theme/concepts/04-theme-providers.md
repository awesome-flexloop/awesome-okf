---
type: concept
title: "React Context Provider 分层系统"
description: "myst-theme 的 Provider 架构——从主题到文档的多层上下文桥接与按需组合"
tags: [myst-theme, react, context, provider, state-management]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "packages/providers/src/index.tsx"
    facts: [F-006, F-035, F-036, F-037, F-038, F-039, F-040, F-041, F-042, F-043, F-044]
---

# React Context Provider 分层系统

## 设计原则

myst-theme 不使用单一巨型 Context 传递所有状态，而是按功能域拆分为多个独立的 React Context Provider。每个 Provider 管理一个内聚的状态域，组件按需消费。

## Provider 层次

典型的 Book 主题中，Provider 从外到内嵌套如下：

```tsx
<ThemeProvider>          {/* 主题、渲染器、链接组件 */}
  <UIProvider>           {/* UI 状态（暗色/亮色、侧边栏开关） */}
    <SiteProvider>       {/* 站点导航、多项目配置 */}
      <ProjectProvider>  {/* 当前项目上下文 */}
        <BaseurlProvider>{/* 部署子路径 */}
          <XrefProvider> {/* 跨项目引用解析 */}
            <LinkProvider>{/* 自定义链接组件 */}
              <BannerProvider>{/* 顶部公告横幅 */}
                <SearchProvider>{/* 搜索功能 */}
                  <GridProvider>{/* 网格布局状态 */}
                    <TabStateProvider>{/* 标签页同步 */}
                      <ArticleProvider> {/* 文档级上下文 */}
                        <Outlet />       {/* 页面内容 */}
                      </ArticleProvider>
                    </TabStateProvider>
                  </GridProvider>
                </SearchProvider>
              </BannerProvider>
            </LinkProvider>
          </XrefProvider>
        </BaseurlProvider>
      </ProjectProvider>
    </SiteProvider>
  </UIProvider>
</ThemeProvider>
```

## 核心 Provider 详解

### ThemeProvider

最外层 Provider，提供：

| 属性/方法 | 类型 | 说明 |
|-----------|------|------|
| `theme` | `'light' \| 'dark'` | 当前主题 |
| `setTheme` | `(theme) => void` | 切换主题 |
| `renderers` | `Renderers` | 节点渲染器映射（覆盖默认） |
| `Link` | `ComponentType` | 自定义链接组件 |
| `loadLinkProvider` | - | 异步加载链接 Provider |

```tsx
<ThemeProvider
  theme="light"
  setTheme={(t) => setCookie('theme', t)}
  renderers={customRenderers}
  Link={CustomLink}
>
```

### ArticleProvider

文档级上下文，提供当前页面的数据：

| 属性 | 类型 | 说明 |
|------|------|------|
| `kind` | `'article' \| 'notebook'` | 文档类型 |
| `frontmatter` | `PageFrontmatter` | 页面元数据（标题、作者、日期等） |
| `references` | `References` | 引用数据（文献、交叉引用） |
| `headings` | `Heading[]` | 标题树（用于 TOC 生成） |
| `references` | `GenericParent` | 引用文章的 MDAST |

### SiteProvider / ProjectProvider

站点和项目导航上下文：

- **SiteProvider**：提供站点级配置（导航栏、footer、项目列表、域名等）
- **ProjectProvider**：提供当前项目信息（项目 slug、TOC、页面索引、跨页引用解析器）
- 两者配合实现多项目文档站（如一个站点包含 "guide"、"api"、"tutorial" 多个项目）

### TabStateProvider

管理 sync-tab 状态：当多个 Tab 组件使用相同的 `sync` key 时，切换一个会同步切换所有同 key 的 Tab。状态提升到 Provider 层级，使得不同位置的 Tab 可以跨组件同步。

### SearchProvider

集成全文搜索功能，管理：
- 搜索索引（MiniSearch 或外部搜索服务）
- 搜索框状态
- 搜索结果导航

### GridProvider

网格布局上下文，让组件感知当前断点和可用空间。例如在小屏上隐藏边注、将侧边内容内联化。

### BannerProvider

管理顶部横幅（公告、通知、警告），支持多条横幅堆叠和可关闭状态。

## 按需组合：jupyterlab-myst 的精简 Provider 树

jupyterlab-myst 不是站点环境，只需要文档渲染能力，因此其 Provider 树大幅精简：

```tsx
// jupyterlab-myst 中只需：
<ThemeProvider renderers={jupyterRenderers} Link={JupyterLink}>
  <ArticleProvider frontmatter={fm} references={refs}>
    <MyST ast={mdast} />
  </ArticleProvider>
</ThemeProvider>
```

不需要 SiteProvider、ProjectProvider、SearchProvider、BannerProvider——这些是站点级关注点。这种按需组合验证了 Provider 分层设计的有效性。

## 自定义 Link 组件

LinkProvider 和 ThemeProvider 的 `Link` 属性允许框架注入路由链接组件：

- **Remix 主题**：使用 Remix 的 `<Link>` 组件（客户端导航）
- **JupyterLab**：使用 JupyterLab 的链接处理
- **独立使用**：默认使用原生 `<a>` 标签

这使得 myst-to-react 的链接渲染不绑定任何特定路由框架。

## 性能考量

- 每个 Provider 独立 memoization，一个 Provider 的状态变化只触发消费该 Context 的组件重渲染
- ArticleProvider 的 frontmatter/references 通常不变，避免不必要的重渲染
- 高频变化的状态（如 TabState、Grid 断点）隔离在独立 Provider 中
