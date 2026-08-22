---
type: Concept
title: TUI 终端 UI 系统
description: @earendil-works/pi-tui 是带差分渲染的终端 UI 库，提供组件系统、模糊搜索、LaTeX 渲染、键绑定管理、终端图片协议和 overlay 焦点管理。
tags: [pi-cli, tui, terminal, 组件, 差分渲染, fuzzy, latex, keybindings]
generated: 2026-08-23
verified: 2026-08-23
status: stable
stale_after: 2026-11-23
sources:
  - packages/tui/src/index.ts:1-147
  - packages/tui/src/tui.ts:23-1263
---

# TUI 终端 UI 系统

`@earendil-works/pi-tui` 是一个最小化终端 UI 实现，核心特性是差分渲染（differential rendering）。它不依赖 ncurses 或类似的全功能终端库，而是直接操作 ANSI 转义序列。

## 组件接口

所有 TUI 组件必须实现 `Component` 接口：

```typescript
interface Component {
  render(width: number): string[];
  handleInput?(data: string): void;
  wantsKeyRelease?: boolean;
  invalidate(): void;
}
```

- `render(width)`：将组件渲染为字符串行数组
- `handleInput(data)`：可选，组件获得焦点时处理键盘输入
- `wantsKeyRelease`：是否接收 Kitty 协议的按键释放事件（默认 false）
- `invalidate()`：使缓存渲染状态失效

`Focusable` 接口扩展 Component，增加 `focused: boolean` 属性。获得焦点时组件应在光标位置发出 `CURSOR_MARKER`（一个零宽 APC 序列），TUI 会找到该标记并定位硬件光标，用于 IME 候选窗口定位。

## 导出组件

`packages/tui/src/index.ts` 导出以下组件：

| 组件 | 用途 |
|------|------|
| `Box` | 通用容器/边框 |
| `Editor` | 多行文本编辑器 |
| `HStack` / `VStack` | 水平/垂直栈布局 |
| `Image` | 终端图片显示 |
| `Input` | 单行输入 |
| `Loader` / `CancellableLoader` | 加载指示器 |
| `Markdown` | Markdown 渲染（基于 marked） |
| `ScrollView` | 可滚动视图 |
| `SelectList` | 选择列表 |
| `SettingsList` | 设置项列表 |
| `Spacer` | 弹性间距 |
| `Text` / `TruncatedText` | 文本显示 |

## 差分渲染引擎

`TuiBase` 抽象类实现核心渲染逻辑：

- **最小渲染间隔**：16ms（约60fps），通过 `requestRender()` 调度
- **即时渲染路径**：键盘输入后调用 `requestImmediateRender()`，通过 `process.nextTick` 绕过 setTimeout 节流（Windows 上 `setTimeout(0)` 可能消耗完整16ms tick）
- **全屏重绘计数**：`fullRedraws` 属性跟踪全屏重绘次数
- **收缩清除**：`clearOnShrink` 选项控制内容缩小时是否清空空行（由 `PI_CLEAR_ON_SHRINK` 环境变量控制）
- **硬件光标**：由 `PI_HARDWARE_CURSOR` 环境变量控制

## Overlay 系统

TUI 维护一个 overlay 栈，用于模态组件：

- `showOverlay(component, options?)`：显示 overlay，返回 `OverlayHandle`
- `hideOverlay()`：隐藏最顶层 overlay
- overlay 支持锚点定位（9种锚点：center、top-left、top-right 等）、绝对/百分比定位、边距配置
- 焦点恢复有三种状态：`inactive`、`eligible`（可恢复）、`blocked`（被其他组件遮挡）
- overlay 可标记为 `nonCapturing`，显示时不捕获键盘焦点

## 模糊搜索 (`fuzzy.ts`)

导出 `fuzzyFilter` 和 `fuzzyMatch` 函数及 `FuzzyMatch` 类型，用于 SelectList、Autocomplete 等组件的模糊匹配。

## LaTeX 渲染 (`latex.ts`)

导出 `renderLatex` 函数和 `RenderLatexOptions` 类型，支持在终端中渲染 LaTeX 数学公式。

## 键绑定系统 (`keybindings.ts`)

导出完整的键绑定管理：

- `KeybindingsManager`：键绑定管理器类
- `getKeybindings()` / `setKeybindings()`：获取/设置键绑定配置
- `Keybinding`、`KeybindingDefinition`、`KeybindingConflict` 等类型
- `TUI_KEYBINDINGS`：默认 TUI 键绑定常量

## 键盘处理 (`keys.ts`)

- `Key` 常量：键标识符
- `parseKey(data)`：解析原始输入为键事件
- `matchesKey(data, keyId)`：匹配键组合（AGENTS.md 规定禁止硬编码键检查，必须使用默认键绑定配置）
- `isKeyRelease()` / `isKeyRepeat()`：Kitty 协议事件判断
- Kitty 键盘协议支持：`isKittyProtocolActive()`、`setKittyProtocolActive()`、`decodeKittyPrintable()`

## 终端图片 (`terminal-image.ts`)

支持多种终端图片协议：

- Kitty 图形协议（`encodeKitty`、`allocateImageId`、`deleteKittyImage`）
- iTerm2 图片协议（`encodeITerm2`）
- 终端能力检测（`detectCapabilities`、`getCapabilities`、`setCapabilities`）
- 多种图片格式尺寸获取：PNG、JPEG、GIF、WebP
- 单元格尺寸查询和图片行数计算

## 终端颜色 (`terminal-colors.ts`)

- OSC 11 背景色查询（`parseOsc11BackgroundColor`）
- 配色方案报告解析（`parseTerminalColorSchemeReport`）：深色/浅色模式检测
- `RgbColor` 和 `TerminalColorScheme` 类型

## 其他功能

- **Autocomplete**：`AutocompleteProvider`、`CombinedAutocompleteProvider`、`SlashCommand` 类型
- **StdinBuffer**：输入缓冲，用于批量分割
- **工具函数**：`visibleWidth`、`truncateToWidth`、`wrapTextWithAnsi`、`stripTerminalSequences`、`sliceByColumn`、`getOsc8LinkAtColumn`
- **TuiAltScreen / TuiMainScreen**：备用屏幕和主屏幕渲染模式

## 相关概念

- [项目简介](/concepts/00-introduction.md)
- [AI 包详解](/concepts/02-ai-package.md)
- [Monorepo 架构](/concepts/01-monorepo-architecture.md)
