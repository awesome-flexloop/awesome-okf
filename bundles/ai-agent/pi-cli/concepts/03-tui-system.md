---
type: Concept
title: "TUI 系统（packages/tui）"
description: "@earendil-works/pi-tui 是带差分渲染的终端 UI 库，核心为 Component 接口、TuiBase 16ms 节流渲染引擎、overlay 栈焦点管理、fuzzy 模糊搜索、LaTeX 渲染和 Kitty 键盘协议支持。"
tags: [pi-cli, tui, terminal, rendering, component, keyboard]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# TUI 系统（packages/tui）

`@earendil-works/pi-tui` 是 Pi 的终端 UI 组件库，提供差分渲染引擎、组件系统、overlay 焦点管理、模糊搜索、LaTeX 渲染和键盘输入处理。它是 coding-agent 交互式界面的基础。

## Component 接口

所有 TUI 组件必须实现 `Component` 接口：

```ts
export interface Component {
  render(width: number): string[];
  handleInput?(data: string): void;
  wantsKeyRelease?: boolean;
  invalidate(): void;
}
```

- `render(width)`：接收当前视口宽度，返回字符串数组，每行一个元素。
- `handleInput?(data)`：可选，组件获得焦点时接收键盘输入。
- `wantsKeyRelease?`：为 `true` 时接收 Kitty 协议的按键释放事件，默认 `false`。
- `invalidate()`：清除缓存渲染状态，在主题变更或需要从头重渲染时调用。

## 内置组件

`src/index.ts` 导出完整组件集：

| 组件 | 用途 |
|------|------|
| `Box` | 通用容器 |
| `VStack` / `HStack` | 垂直/水平栈布局 |
| `Text` / `TruncatedText` | 文本显示 |
| `Markdown` | Markdown 渲染 |
| `Input` / `Editor` | 单行输入 / 多行编辑器 |
| `ScrollView` | 可滚动视图 |
| `SelectList` / `SettingsList` | 选择列表 / 设置列表 |
| `Loader` / `CancellableLoader` | 加载指示器 |
| `Image` | 终端图片 |
| `Spacer` | 弹性间距 |

## 差分渲染引擎

`TuiBase` 抽象类实现差分渲染，核心常量为最小渲染间隔 16ms（约 60fps）：

```ts
private static readonly MIN_RENDER_INTERVAL_MS = 16;
```

渲染调度分两条路径：

**节流渲染**（`requestRender`）：通过 `process.nextTick` 调度 `scheduleRender()`，后者用 `setTimeout` 保证距上次渲染至少 16ms：

```ts
requestRender(force = false): void {
  if (force) {
    this.resetRenderState();
    this.requestImmediateRender();
    return;
  }
  if (this.renderRequested) return;
  this.renderRequested = true;
  process.nextTick(() => this.scheduleRender());
}

private scheduleRender(): void {
  if (this.stopped || this.renderTimer || !this.renderRequested) return;
  const elapsed = performance.now() - this.lastRenderAt;
  const delay = Math.max(0, TuiBase.MIN_RENDER_INTERVAL_MS - elapsed);
  this.renderTimer = setTimeout(() => {
    this.renderTimer = undefined;
    if (this.stopped || !this.renderRequested) return;
    this.renderRequested = false;
    this.lastRenderAt = performance.now();
    this.doRender();
    if (this.renderRequested) this.scheduleRender();
  }, delay);
}
```

**即时渲染**（`requestImmediateRender`）：键盘输入后调用，通过 `process.nextTick` 绕过 setTimeout 节流，取消任何待处理的节流定时器：

```ts
private requestImmediateRender(): void {
  this.cancelRenderTimer();
  this.renderRequested = true;
  if (this.immediateRenderScheduled) return;
  this.immediateRenderScheduled = true;
  process.nextTick(() => {
    this.immediateRenderScheduled = false;
    if (this.stopped || !this.renderRequested) return;
    this.cancelRenderTimer();
    this.renderRequested = false;
    this.lastRenderAt = performance.now();
    this.doRender();
  });
}
```

这在 Windows 上尤其重要，因为 `setTimeout(0)` 可能消耗完整 16ms tick。自定义组件的 `handleInput()` 后无需手动调用渲染，框架自动触发即时渲染。

`requestRender(true)` 强制重置渲染状态并立即重绘。

## Overlay 栈与焦点管理

`TuiBase` 维护 overlay 栈用于模态组件，`showOverlay()` 返回 `OverlayHandle`：

```ts
showOverlay(component: Component, options?: OverlayOptions): OverlayHandle {
  const entry: OverlayStackEntry = {
    component,
    preFocus: this.focusedComponent,
    hidden: false,
    focusOrder: ++this.focusOrderCounter,
  };
  this.overlayStack.push(entry);
  if (!options?.nonCapturing && this.isOverlayVisible(entry)) {
    this.setFocus(component);
  }
  this.terminal.hideCursor();
  this.requestRender();
  return {
    hide: () => { /* 移除 overlay 并恢复焦点 */ },
    setHidden: (hidden: boolean) => { /* 隐藏/显示，切换焦点 */ },
    isHidden: () => entry.hidden,
    focus: () => { /* 聚焦此 overlay */ },
    unfocus: (unfocusOptions?) => { /* 移焦，支持 blocked 恢复 */ },
    isFocused: () => this.focusedComponent === component,
  };
}
```

焦点恢复不是简单的栈弹出，而是三态机制：

- **`eligible`**：overlay 可见且拥有焦点，可被恢复。
- **`blocked`**：焦点被非 overlay 组件临时占据，记住被遮挡的目标，当该组件释放焦点时恢复到 overlay。
- **`inactive`**：无待恢复的 overlay 焦点。

这处理了"overlay 弹出自动补全列表 → 用户焦点移到输入框 → 补全关闭后焦点应回到 overlay"等复杂场景。

## 终端能力检测

### 背景色与配色方案

TUI 支持 OSC 11 背景色查询和 DSR 配色方案通知：

- 查询终端背景色：OSC `11` 响应被解析为 RGB。
- 配色方案通知：DSR `CSI ? 996 n`，终端回复深色 `CSI ? 997 ; 1 n` 或浅色 `CSI ? 997 ; 2 n`。

### Kitty 键盘协议

支持 Kitty 键盘协议以获得增强的按键识别（修饰键、按键释放等）。协议状态为全局：

```ts
export function setKittyProtocolActive(active: boolean): void;
export function isKittyProtocolActive(): boolean;
```

## fuzzy.ts：模糊搜索

`fuzzyMatch()` 实现子序列模糊匹配——查询字符按序出现即可，不必连续。分数越低匹配越好：

```ts
export interface FuzzyMatch {
  matches: boolean;
  score: number;
}

export function fuzzyMatch(query: string, text: string): FuzzyMatch {
  // 连续匹配加分（score -= consecutiveMatches * 5）
  // 词边界匹配加分（score -= 10）
  // 间隙惩罚（score += gap * 2）
  // 完全相等额外加分（score -= 100）
}
```

`fuzzyFilter()` 过滤集合并按分数排序。还支持字母-数字交换匹配（如 `"openai3"` 匹配 `"3openai"`）。

## latex.ts：LaTeX 渲染

`renderLatex()` 将 LaTeX 命令转换为 Unicode 符号。内置希腊字母表映射：

```ts
const SYMBOLS: Readonly<Record<string, string>> = {
  alpha: "α", beta: "β", gamma: "γ", delta: "δ",
  epsilon: "ϵ", varepsilon: "ε", pi: "π",
  Gamma: "Γ", Delta: "Δ", Theta: "Θ", Lambda: "Λ",
  Pi: "Π", Sigma: "Σ",
  // ... 完整希腊字母及数学符号
};
```

## keys.ts：键盘处理

`keys.ts` 同时支持传统终端转义序列和 Kitty 键盘协议，导出：

- `Key`：类型安全的键标识符辅助对象。
- `matchesKey(data, keyId)`：检查输入数据是否匹配键标识符。
- `parseKey(data)`：解析输入并返回键标识符。
- `isKeyRelease(data)` / `isKeyRepeat(data)`：判断事件类型。
- `decodeKittyPrintable(data)`：解码 Kitty 协议的可打印字符。

部分 Ctrl+符号组合与 ASCII 码重叠（如 `Ctrl+[` = ESC），Kitty 协议可区分 Ctrl+Shift 组合。

## KeybindingsManager

键绑定管理器支持配置自定义快捷键、冲突检测：

```ts
export {
  getKeybindings,
  setKeybindings,
  KeybindingsManager,
  TUI_KEYBINDINGS,
  type Keybinding,
  type KeybindingConflict,
  type KeybindingDefinition,
} from "./keybindings.ts";
```

## 终端图片

支持 Kitty 图形协议和 iTerm2 图片协议，自动检测终端能力并提供回退：

```ts
export {
  detectCapabilities,
  encodeKitty,
  encodeITerm2,
  renderImage,
  imageFallback,
  getImageDimensions,
  type TerminalCapabilities,
  type ImageProtocol,
} from "./terminal-image.ts";
```

## 相关概念

- [AI 包（packages/ai）](./02-ai-package.md)
- [Monorepo 架构](./01-monorepo-architecture.md)
- [内置 Prompts](./04-builtin-prompts.md)
