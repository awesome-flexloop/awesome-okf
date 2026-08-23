---
type: Concept
title: "Monorepo 架构"
description: "pi-monorepo 包含 9 个 npm 包，按 tui→telemetry→ai→agent→sqlite-node→protocol→client→server→coding-agent 顺序构建，使用路径别名和锁步版本控制。"
tags: [pi-cli, architecture, monorepo, packages, build]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# Monorepo 架构

`pi-monorepo` 使用 npm workspaces 管理多包仓库。workspaces 配置在根 `package.json` 中：

```json
{
  "workspaces": [
    "packages/*",
    "packages/session-backends/*",
    "packages/coding-agent/examples/extensions/with-deps",
    "packages/coding-agent/examples/extensions/custom-provider-anthropic",
    "packages/coding-agent/examples/extensions/custom-provider-gitlab-duo",
    "packages/coding-agent/examples/extensions/sandbox",
    "packages/coding-agent/examples/extensions/gondolin"
  ]
}
```

## 九个包及其职责

| 包目录 | npm 包名 | 职责 |
|--------|----------|------|
| `packages/tui` | `@earendil-works/pi-tui` | 终端 UI 组件库，差分渲染引擎、overlay 焦点管理、模糊搜索、LaTeX 渲染、键盘处理 |
| `packages/telemetry` | `@earendil-works/pi-telemetry` | 厂商中立遥测契约、参考适配器、类型化 schema 与一致性测试 |
| `packages/ai` | `@earendil-works/pi-ai` | 统一多提供商 LLM API：Provider/Models 抽象、OAuth 认证、10 种 API 类型、40 个 provider、图片生成 |
| `packages/agent` | `@earendil-works/pi-agent-core` | 有状态代理运行时，支持工具调用（parallel/sequential）、事件流、会话管理、压缩 |
| `packages/session-backends/sqlite-node` | `@earendil-works/pi-session-backend-sqlite-node` | 基于 SQLite 的 Node.js 会话持久化后端 |
| `packages/protocol` | `@earendil-works/pi-protocol` | 长度前缀 CBOR 消息协议，用于 client/server 通信 |
| `packages/client` | `@earendil-works/pi-client` | 传输无关的远程 pi 会话客户端，支持 exclusive/shared 租约模式 |
| `packages/server` | `@earendil-works/pi-server` | 实验性会话服务器，通过 `PiServerListener` 组合传输监听器 |
| `packages/coding-agent` | `@earendil-works/pi-coding-agent` | 交互式编码代理 CLI，最终用户入口，包含扩展系统、技能、工具 |

此外 `packages/evals` 提供评估工具，但不在主构建链中。

## 构建顺序

根 `build` 脚本按严格依赖顺序链式构建 9 个包：

```bash
cd packages/tui && npm run build \
  && cd ../telemetry && npm run build \
  && cd ../ai && npm run build \
  && cd ../agent && npm run build \
  && cd ../session-backends/sqlite-node && npm run build \
  && cd ../../protocol && npm run build \
  && cd ../client && npm run build \
  && cd ../server && npm run build \
  && cd ../coding-agent && npm run build
```

顺序反映了依赖关系：tui 和 telemetry 是叶子包，ai 依赖 telemetry，agent 依赖 ai 和 tui，protocol 独立，client 依赖 protocol，server 依赖 protocol 和 agent，coding-agent 依赖以上全部。`build:offline` 变体使用已有模型数据，不发起网络请求刷新 provider 目录。

## 路径别名

`tsconfig.json` 为每个包配置了源码级路径别名，使开发时无需构建即可跨包导入：

```json
{
  "compilerOptions": {
    "paths": {
      "@earendil-works/pi-ai": ["./packages/ai/src/index.ts"],
      "@earendil-works/pi-ai/oauth": ["./packages/ai/src/oauth.ts"],
      "@earendil-works/pi-ai/*": ["./packages/ai/src/*.ts", "./packages/ai/src/providers/*.ts"],
      "@earendil-works/pi-tui": ["./packages/tui/src/index.ts"],
      "@earendil-works/pi-tui/*": ["./packages/tui/src/*"],
      "@earendil-works/pi-agent-core": ["./packages/agent/src/index.ts"],
      "@earendil-works/pi-coding-agent": ["./packages/coding-agent/src/index.ts"],
      "@earendil-works/pi-protocol": ["./packages/protocol/src/index.ts"],
      "@earendil-works/pi-client": ["./packages/client/src/index.ts"],
      "@earendil-works/pi-server": ["./packages/server/src/index.ts"],
      "@earendil-works/pi-telemetry": ["./packages/telemetry/src/index.ts"]
    }
  }
}
```

通配符别名（如 `@earendil-works/pi-ai/*`）允许直接导入子模块，包括 provider factories（`@earendil-works/pi-ai/providers/openai`）和 API 实现。

## 锁步版本控制

AGENTS.md 规定所有包共享一个版本号，每次发布同时更新全部包：

- **`patch`**：修复 + 新增功能（无破坏性变更）
- **`minor`**：破坏性变更
- **无 `major` 发布**

版本同步通过 `scripts/sync-versions.js` 完成：

```bash
npm run version:patch   # npm version patch --workspaces + sync-versions + lockfile 更新
npm run version:minor   # 破坏性变更
```

## 代码风格与检查

`check` 脚本执行 6 项流水线检查：

```bash
biome check --write --error-on-warnings .   # 1. lint + 格式化
npm run check:pinned-deps                   # 2. 验证直接依赖固定到精确版本
npm run check:ts-imports                    # 3. 验证原生 TS 相对导入兼容性
npm run check:shrinkwrap                    # 4. 验证 coding-agent shrinkwrap
npm run check:install-lock:coding-agent     # 5. 验证安装锁
tsgo --noEmit                               # 6. TypeScript 原生预览编译器类型检查
npm run check:browser-smoke                 # 7. 浏览器冒烟测试
```

AGENTS.md 规定的代码约束：

- 禁止 `any`（除非绝对必要）
- 禁止内联动态导入（`await import()`）
- 仅使用可擦除 TypeScript 语法（无 parameter properties、enum、namespace/module）
- 禁止直接修改 `packages/ai/src/models.generated.ts`，必须更新 `scripts/generate-models.ts` 后重新生成

## 相关概念

- [Pi AI CLI 简介](./00-introduction.md)
- [AI 包（packages/ai）](./02-ai-package.md)
- [TUI 系统](./03-tui-system.md)
- [基础使用示例](../examples/01-basic-usage.md)
