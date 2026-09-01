# Textualize Bundle 更新日志

## 2026-09-01 - 初始版本

### 新增

- 初始化 Textualize OKF Wiki Bundle 结构
- **references/** 信源登记（12 个仓库 + `index.md`）：
  - `rich.md` / `textual.md` / `frogmouth.md` / `toolong.md` / `trogon.md`
  - `rich-cli.md` / `textual-dev.md` / `textual-serve.md` / `textual-web.md`
  - `textual-demo.md` / `textual-key-recorder.md` / `github-org.md`
  - `index.md` — 信源索引
- **concepts/** 概念文档（27 个 + `index.md`）：
  - `00-ecosystem-overview.md` 生态总览
  - `01-rich-console-and-protocol.md` 至 `12-rich-render-pipeline-and-export.md`（rich 12 篇）
  - `13-textual-app-entry.md` 至 `19-textual-css-worker-driver.md`（textual 7 篇）
  - `20-rich-cli.md` 至 `26-textual-web.md`（卫星 7 篇）
  - `index.md` — 概念索引与学习路径
- **examples/** 示例文档（8 个 + `index.md`）：
  - `rich-console-markup.md` / `rich-table-panel.md` / `rich-progress-track.md`
  - `textual-minimal-app.md` / `textual-reactive-counter.md` / `textual-widget-messages.md`
  - `trogon-tui-decorator.md` / `textual-serve-hello.md`
  - `index.md` — 示例索引
- **根文件**：
  - `index.md` — Bundle 主页（含 okf_version + toctree）
  - `log.md` — 本更新日志

### 基于源码版本

- 信源根：`external/dao/action/Textualize/`（12 个仓库，commit hash 见 [references/index.md](references/index.md)）
- 事实文件：`.trae/specs/textualize-okf-wiki/facts-*.md`（F-xxx 共 377 条）
- 洞察与知识地图：`.trae/specs/textualize-okf-wiki/insights.md`
- 验证流程：Grep 级 API 真实性 + 计数断言 + toctree/链接完整性

## 2026-09-01 - 补充 textual 框架示例

### 新增

- **examples/** 新增 3 篇 textual 框架核心机制示例：
  - `textual-screen-modes.md` — MODES 多模式、push_screen/ModalScreen 模态对话框、dismiss(result) 回调
  - `textual-worker.md` — @work 装饰器（async 与 thread 两种 worker）、Worker.StateChanged 状态消息、cancel/异常
  - `textual-datatable.md` — DataTable add_column/add_row/update_cell/remove_row 与 RowSelected/CellSelected 消息
- examples/index.md 表格与 toctree 同步注册（示例总数 8 → 11）
- 根 index.md 示例计数同步（8 → 11）