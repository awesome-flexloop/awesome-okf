---
type: Concept
title: Node.js CLI 入口
description: >
  codex-cli 是 npm 包 @openai/codex 的 Node.js 启动器，仅负责平台检测、
  原生二进制定位、信号转发和退出码镜像。本文详解 bin/codex.js 的工作原理
  及其与 Rust 核心的桥接方式。
tags: [openai-codex, nodejs, npm, cli, launcher, bridge]
generated:
  by: "reference_agent/trae-cn"
  at: 2026-08-23T10:00:00+08:00
verified:
  by: "process:grep-verification"
  at: 2026-08-23T10:00:00+08:00
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# Node.js CLI 入口

`codex-cli/` 目录是 npm 包 `@openai/codex` 的源码。它是一个极薄的 Node.js 启动器（shim），唯一职责是定位并启动平台对应的 Rust 原生二进制，不包含任何 agent 业务逻辑。

## 包配置

```json
{
  "name": "@openai/codex",
  "version": "0.0.0-dev",
  "bin": {
    "codex": "bin/codex.js"
  },
  "type": "module",
  "engines": {
    "node": ">=16"
  },
  "files": [
    "bin/codex.js"
  ]
}
```

关键点：
- 包名 `@openai/codex`，注册 `codex` 命令到 `bin/codex.js`
- ES 模块（`"type": "module"`）
- 仅要求 Node.js >=16（比根 monorepo 的 >=22 宽松，因为启动器逻辑简单）
- 发布时只包含 `bin/codex.js` 一个文件

## 平台检测与二进制定位

`bin/codex.js` 首先根据 `process.platform` 和 `process.arch` 确定 Rust target triple：

```javascript
const PLATFORM_PACKAGE_BY_TARGET = {
  "x86_64-unknown-linux-musl": "@openai/codex-linux-x64",
  "aarch64-unknown-linux-musl": "@openai/codex-linux-arm64",
  "x86_64-apple-darwin": "@openai/codex-darwin-x64",
  "aarch64-apple-darwin": "@openai/codex-darwin-arm64",
  "x86_64-pc-windows-msvc": "@openai/codex-win32-x64",
  "aarch64-pc-windows-msvc": "@openai/codex-win32-arm64",
};
```

支持的平台：
- **Linux**：x64 和 arm64，静态链接 musl
- **macOS**：x64（Intel）和 arm64（Apple Silicon）
- **Windows**：x64 和 arm64，MSVC ABI

平台二进制通过 npm optionalDependencies 分发。启动器按以下顺序查找：

1. 尝试 `require.resolve('@openai/codex-<platform>/package.json')`，从该包的 `vendor/<triple>/bin/` 定位
2. 回退到启动器旁边的 `../vendor/<triple>/bin/` 目录
3. Windows 下查找 `codex.exe`，其他平台查找 `codex`

如果找不到二进制，抛出错误并根据检测到的包管理器给出重装命令：

```javascript
throw new Error(
  `Missing optional dependency ${platformPackage}. Reinstall Codex: ${updateCommand}`,
);
```

## 包管理器检测

启动器通过启发式方法检测安装方式，以提供准确的更新提示：

1. **pnpm**：向上遍历目录树，查找包含 `.modules.yaml` 的 `node_modules`，并验证 `@openai/codex` 的 realpath 匹配
2. **Bun**：检查 `npm_config_user_agent`、`npm_execpath` 是否包含 "bun"，以及路径是否包含 `.bun/install/global`
3. **npm**：默认回退

检测结果通过环境变量传递给 Rust 二进制：

```javascript
env.CODEX_MANAGED_BY_PNPM = "1";
// 或 CODEX_MANAGED_BY_BUN / CODEX_MANAGED_BY_NPM
```

同时设置 `CODEX_MANAGED_PACKAGE_ROOT` 指向包根目录。

## 异步子进程生成

启动器使用 `spawn`（异步）而非 `spawnSync`，原因在代码注释中明确说明：

> Use an asynchronous spawn instead of spawnSync so that Node is able to respond to signals (e.g. Ctrl-C / SIGINT) while the native binary is executing.

```javascript
const child = spawn(binaryPath, process.argv.slice(2), {
  stdio: "inherit",
  env,
});
```

- `stdio: "inherit"` 使子进程直接使用父进程的 stdin/stdout/stderr
- `process.argv.slice(2)` 透传所有命令行参数给 Rust 二进制
- 自定义 `env` 包含包管理器标记

## 信号转发

启动器转发三个终止信号到子进程：

```javascript
["SIGINT", "SIGTERM", "SIGHUP"].forEach((sig) => {
  process.on(sig, () => forwardSignal(sig));
});
```

`forwardSignal` 检查子进程是否已被杀死，然后调用 `child.kill(signal)`。这确保了 Ctrl-C 能优雅地终止 Rust 进程及其子进程树。

## 退出码镜像

子进程退出后，启动器镜像其终止原因：

```javascript
if (childResult.type === "signal") {
  // 重新发出相同信号，使父进程以 128+signal 退出
  process.kill(process.pid, childResult.signal);
} else {
  process.exit(childResult.exitCode);
}
```

这保证了 shell 脚本和 CI 系统能观察到正确的退出状态。

## 与 Rust 核心的桥接

Node.js 启动器与 Rust 二进制之间没有 IPC 或 API 调用——桥接完全通过：

1. **命令行参数**：`process.argv.slice(2)` 直接透传
2. **环境变量**：`CODEX_MANAGED_BY_*`、`CODEX_MANAGED_PACKAGE_ROOT`
3. **stdio 继承**：所有输入输出直接通过终端
4. **退出码/信号**：完整镜像

Rust 二进制的 `codex-rs/cli/src/main.rs` 使用 `clap` 解析所有参数，不知道也不关心自己是被 Node.js 启动器还是直接调用的。

## 发布架构

npm 包的发布策略是"瘦主包 + 胖平台包"：

- `@openai/codex`（主包）：只含 249 行 JS，体积小
- `@openai/codex-linux-x64` 等（6 个平台包）：各含对应平台的 Rust 二进制
- npm 在安装时自动选择匹配当前平台的 optionalDependency

这种设计的优势：
- 跨平台支持通过单个 `npm install -g @openai/codex` 实现
- 用户只下载当前平台的二进制，不浪费带宽
- Rust 二进制独立构建和测试，不经过 Node.js 工具链

## 相关概念

- [Rust 核心与 TUI](./02-rust-core-tui.md)
- [工作区架构](./01-workspace-architecture.md)
- [简介](./00-introduction.md)
- [Python SDK](./06-python-sdk.md)
