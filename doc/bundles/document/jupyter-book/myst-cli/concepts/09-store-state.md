---
type: concept
title: "Store 状态管理"
description: "myst-cli基于Redux的全局状态管理：Slice设计、Selectors查询与构建状态追踪"
tags: [myst-cli, store, redux, state-management, selectors]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/store/reducers.ts"
    facts: [F-047, F-048, F-049]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/store/types.ts"
    facts: [F-050, F-051]
---

# Store 状态管理

myst-cli 使用 Redux（通过 Redux Toolkit）管理全局状态，包括项目配置、构建警告、文件监视等。这为 CLI 工具提供了可预测的状态管理和时间旅行调试能力。

## 架构选择

与大多数 CLI 工具使用简单对象或事件发射器不同，myst-cli 选择 Redux 的原因：
1. **长生命周期**：`myst start` 开发服务器是长时间运行的进程，需要可预测的状态管理
2. **多项目支持**：站点构建涉及多个子项目，状态需要按路径隔离
3. **可调试性**：Redux DevTools 可用于调试复杂的构建链路
4. **Selectors 模式**：提供派生状态的计算和缓存点

## Slice 结构

使用 Redux Toolkit 的 `createSlice` 创建三个核心 slice：

### projects slice

```ts
export const projects = createSlice({
  name: 'projects',
  initialState: {} as Record<string, LocalProject>,
  reducers: {
    receive(state, action: PayloadAction<LocalProject>) {
      state[resolve(action.payload.path)] = action.payload;
    },
  },
});
```

管理已加载的项目，按绝对路径索引。每个项目加载完成后通过 `projects.actions.receive(project)` dispatch 存入 store。

### affiliations slice

```ts
export const affiliations = createSlice({
  name: 'affiliations',
  initialState: {} as Record<string, string>,
  reducers: {
    receive(state, action) {
      action.payload.affiliations.forEach((aff) => {
        state[aff.id] = aff.text;
      });
    },
  },
});
```

管理作者机构信息（ID → 机构名称映射），用于引用和参考文献中的机构名解析。

### config slice

最复杂的 slice，管理配置相关的所有状态：

```ts
initialState: {
  currentProjectPath: string | undefined;  // 当前活动项目路径
  currentSitePath: string | undefined;     // 当前站点路径
  rawConfigs: Record<string, {             // 原始YAML配置（按路径）
    raw: Record<string, any>;
    validated: ValidatedRawConfig;
  }>;
  projects: Record<string, Record<string, any>>;  // 验证后的项目配置
  projectParts: Record<string, string[]>; // 项目分块文件列表
  fileParts: Record<string, string[]>;    // 文件分块列表
  sites: Record<string, Record<string, any>>;      // 站点配置
  filenames: Record<string, string>;      // 配置文件名（按路径）
  configExtensions?: string[];            // 扩展配置文件
}
```

Actions 包括：
- `receiveCurrentProjectPath` / `receiveCurrentSitePath`：设置当前路径
- `receiveRawConfig`：存储原始和验证后的配置
- `receiveSiteConfig` / `receiveProjectConfig`：存储验证后的配置
- `receiveConfigExtension`：注册扩展配置
- `receiveProjectPart` / `receiveFilePart`：记录文档分块

### watchedFiles slice（部分）

store/reducers.ts 还包含文件监视状态（从代码截断处可见 `WatchedFile` 类型），用于 `myst start` 的热重载功能。

## RootState 和 Reducer

```ts
const rootReducer = combineReducers({
  projects: projects.reducer,
  affiliations: affiliations.reducer,
  config: config.reducer,
  // ... 其他 slice
});

export type RootState = ReturnType<typeof rootReducer>;
```

Session 创建时通过 `createStore(rootReducer)` 初始化 store。

## Selectors 查询

通过 `selectors` 对象（store/selectors.ts）提供只读查询接口：

```ts
// 查询示例
selectors.selectCurrentSiteConfig(state)       // 当前站点配置
selectors.selectCurrentProjectConfig(state)    // 当前项目配置
selectors.selectCurrentProjectPath(state)      // 当前项目路径
selectors.selectLocalProject(state, path)      // 按路径获取已加载项目
selectors.selectFileWarningsByRule(state, ruleId)  // 按规则ID获取文件警告
```

Selectors 封装了状态查询逻辑，调用方不需要知道 state 的内部结构。

## 警告系统

### BuildWarning 类型

```ts
type BuildWarning = {
  message: string;
  kind: 'error' | 'warn' | 'info' | 'debug';
  note?: string | null;
  url?: string | null;
  position?: VFileMessage['position'];  // 源码位置
  ruleId?: string | null;              // 规则ID（来自myst-common）
};
```

警告按 RuleId 分类，便于：
- `--strict` 模式下将警告升级为错误
- 按类型过滤和汇总警告
- Clone 会话间去重聚合

### ExternalLinkResult

```ts
type ExternalLinkResult = {
  url: string;
  ok?: boolean;
  skipped?: boolean;
  status?: number;
  statusText?: string;
};
```

`--check-links` 选项使用此类型记录外部链接检查结果。

## 状态流转示例

以 build 命令为例的状态流转：

```
1. new Session() → createStore(rootReducer) → 初始空状态
2. reload()/findCurrentProjectAndLoad()
   ├─ loadConfig() → dispatch receiveRawConfig/receiveProjectConfig
   └─ 设置 currentProjectPath
3. loadProjectFromDisk()
   ├─ 读取文件系统
   ├─ 解析TOC
   └─ dispatch projects.actions.receive()
4. build()
   ├─ selectors.selectCurrentSiteConfig() 查询站点配置
   ├─ selectors.selectLocalProject() 查询已加载项目
   ├─ 解析过程中产生的警告写入 store
   └─ localArticleExport() / buildSite()
5. getAllWarnings() 聚合所有警告
6. session.dispose() → store 随 Session 销毁
```

## 相关概念

- [会话与缓存](08-session-cache.md) — Session 如何创建和持有 Store
- [项目加载与TOC](05-project-load-toc.md) — 项目加载时的状态 dispatch
- [Build 管线](01-build-pipeline.md) — Build 过程中的状态查询
