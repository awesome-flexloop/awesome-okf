---
type: spec
scope: pi-cli
name: insights
version: "0.1.0"
source: local
description: 基于源码事实提炼的 pi-cli 核心洞察
---

# Insights — pi-cli

## 洞察一：Provider 是运行时具体单元，Models 是编排集合

**陈述**：`Provider<TApi>` 接口拥有 id/name/auth/model 列表和 stream 行为，而 `Models` 接口负责解析认证、刷新动态模型目录、将请求委派给拥有该模型的 provider。两者通过 `createModels()` 和 `createProvider()` 工厂组合。

**证据**：F-020、F-021、F-022、F-023

**反常识**：模型不是全局静态目录查找的。动态 provider 的模型列表在首次 `refreshModels()` 前为空，且 `getModels()` 是同步的"最后已知"快照。认证失败不会阻止模型列出，只影响 `getAvailable()` 过滤。

**行动**：使用 pi-ai 时，先 `createModels()` 再 `setProvider()`，对动态 provider 调用 `refresh({ allowNetwork: true })` 后再查询模型。不要假设 `getModel()` 返回非空。

---

## 洞察二：compat.ts 是正在消亡的全局 API 垫片

**陈述**：`@earendil-works/pi-ai/compat` 保留了旧的全局 `stream()`/`complete()` API、api-registry 和环境变量 API key 注入，模块加载时自动注册10个内置 API。文件头注释明确声明该模块将在 coding-agent ModelManager 迁移完成后删除。

**证据**：F-030、F-031、F-018

**反常识**：新代码不应从 `@earendil-works/pi-ai` 根入口导入 provider 工厂或 OAuth 实现。根入口（`index.ts`）刻意保持无副作用，provider factories 位于 `@earendil-works/pi-ai/providers/*` 子路径。compat 入口则相反——它在导入时即注册全局状态。

**行动**：新代码使用 `createModels()` + provider factories 模式，避免导入 compat。现有迁移中的应用可暂时使用 compat，但应跟踪删除计划。

---

## 洞察三：TUI 差分渲染以16ms为帧间隔，键盘输入走即时路径绕过节流

**陈述**：`TuiBase` 使用 `requestRender()` 调度节流渲染（最小间隔16ms），但键盘输入通过 `requestImmediateRender()` 走 `process.nextTick` 路径，绕过 setTimeout 节流。overlay 栈支持焦点恢复策略（eligible/blocked/inactive 三态）。

**证据**：F-036、F-035、F-037

**反常识**：虽然渲染节流到约60fps，但键盘输入后不等待定时器——这在 Windows 上尤其重要，因为 `setTimeout(0)` 可能消耗完整16ms tick。overlay 的焦点恢复不是简单的栈弹出，而是有 blocked 状态记住被遮挡的目标。

**行动**：自定义 TUI 组件的 `handleInput()` 后无需手动调用渲染，框架会触发即时渲染。处理 overlay 时使用返回的 `OverlayHandle` 控制焦点，不要直接操作内部栈。

---

## 洞察四：内置 prompt 构成了一套自我维护的开发工作流

**陈述**：`.pi/prompts/` 下5个 prompt（cl/is/pr/sa/wr）覆盖了 changelog 审计、issue 分析、PR 审查、安全公告更新、任务收尾提交的完整开发周期。每个 prompt 都有严格的流程约束和安全规则。

**证据**：F-045、F-046、F-047、F-048、F-049

**反常识**：`/wr` prompt 在非 main 分支上跳过 changelog，且如果工作来自 `/is` 或 `/pr`，它假设 issue/PR 上下文已从对话历史中获知，不重新询问。`/sa` 明确禁止使用浏览器 cookie 获取公告评论——这是一个安全边界，不是功能缺失。

**行动**：使用这些 prompt 时，按顺序组合：`/is` 分析 → 实现 → `/pr` 审查 → `/cl` 审计 changelog → `/wr` 收尾。不要在 `/sa` 中期望获取评论，需用户手动粘贴。

---

## 洞察五：供应链安全是架构级关注点，不是事后加固

**陈述**：直接外部依赖固定到精确版本，`.npmrc` 设置 `save-exact=true` 和 `min-release-age=2`，pre-commit 阻止锁文件提交，发布包包含 `npm-shrinkwrap.json` 固定传递依赖，CI 使用 `npm ci --ignore-scripts`。AGENTS.md 规定更新 undici 时必须阅读 changelog。

**证据**：F-013、F-015、F-007

**反常识**：`--ignore-scripts` 不是可选的安全建议，而是开发/CI/发布的默认操作模式。生命周期脚本依赖有显式 allowlist，新依赖的生命周期脚本会导致检查失败直到人工审查。

**行动**：添加依赖时固定精确版本，避免引入有生命周期脚本的包。本地安装始终使用 `npm install --ignore-scripts`，仅在用户明确要求时运行生命周期脚本。
