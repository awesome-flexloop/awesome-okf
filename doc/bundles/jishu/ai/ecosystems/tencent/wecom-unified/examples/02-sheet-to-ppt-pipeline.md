---
type: example
title: 从表格数据到在线 PPT
description: 用 collect.py 采集本地工作簿数据，再经 pptx 域创建并填充在线幻灯片的跨域流程演示。
tags: [wecom, wecom-unified, example, sheet, pptx]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-unified/
  - resource: /references/facts.md
---

# 从表格数据到在线 PPT

> **声明**：本示例为基于源码阅读整理的用法演示，**未在本机实跑**。所有命令输出、返回结构与文档链接均为格式「示意」，不代表真实运行结果；具体字段以对应 reference 与本机命令为准。

## 适用场景

手头有一份销售或运营工作簿，需要整理成一份在线汇报 PPT 发给同事。流程跨两个业务域：先用 `sheet` 域的 `collect.py` 把宽表压成结构化 JSON，再按 `pptx` 域契约创建在线文档、逐页写入 JSX 并上传图片。适合「数据在本地、交付物在线上」的周报/季度复盘场景。

## 前置条件

| 条件 | 要求 | 证据 |
|---|---|---|
| 环境 | 已完成版本检查与授权（`authorized`） | F-024～F-032 |
| Python | 可运行 `collect.py`，已安装 `openpyxl` | F-074 |
| 输入文件 | `.xlsx` 或 `.xlsm`；`.xls` 需先转换 | F-074 |
| 领域知识 | 已读取 `wecomcli-pptx.md` 与 `wecomcli-pptx-create-from-material.md` | F-040、F-061 |

## 分步命令

**Step 1：采集表格数据**

```bash
python scripts/collect.py data/销售数据.xlsx --sheet 销售 --range A1:F40 > facts.json
```

`--sheet`、`--range`、`--column` 用于定向采集，缺省采集所有子表；结果为 stdout 上的紧凑 JSON（F-073）。单值会被截断到 60 字符，宽表默认只展示前 60 列（F-075）。

**Step 2：读取 pptx 域契约**

先读域入口，再按其中路由表下钻到「从素材创建」的细则，确认页数、画布尺寸与图片机制。此步不可跳过——参数必须来自 reference，而不是记忆（F-023、F-040）。

**Step 3：创建在线 PPT**

```bash
wecom-cli doc create --json '{"doc_type": "ppt", "doc_name": "Q3 销售复盘"}'
```

`doc_type` 固定为 `"ppt"`；新建文档自带一页空白首页，需按契约删除（`wecomcli-pptx-pptx-api.md:69-73`）。

**Step 4：持久化设计契约**

```bash
wecom-cli slide designs update --json '{...}'
```

`design_md` 与 `story_md` 必须在同一次调用中一起提交，只传一个会失败；这是写类操作的前置门，跳过则后续全部失败（`wecomcli-pptx-pptx-api.md:60`）。

**Step 5：逐页写入内容**

```bash
wecom-cli slide pages addjsx --json '{...}'
```

`addjsx` 是单页命令，N 页需 N 次调用，且为异步任务，返回 `task_id` 与 `slide_id`；写 JSX 内容页不要误用 `slide pages add`（后者是按版式建空页）（`wecomcli-pptx-pptx-api.md:62-65`）。

**Step 6：上传并引用图片**

```bash
wecom-cli smartpage images upload --json '{"docid": "<DOCID>", "file_path": "/abs/chart.png"}'
```

把返回的 `url` 直接写进 JSX 的 `<Image src="...">`，服务端编译时下载渲染（`wecomcli-pptx-pptx-api.md:100-104`）。

**Step 7：核对结构并交付链接**

```bash
wecom-cli slide get --json '{...}'
```

核对页数、页序与画布尺寸后，把在线文档链接发给用户。pptx 域**没有任何导出能力**，不要承诺 `.pptx` 文件（F-041）。

## 预期结果（示意）

| 阶段 | 产物 | 示意 |
|---|---|---|
| Step 1 | `facts.json` | 含子表名、行列数、列类型与截断后的样例值 |
| Step 3 | `docid` | 形如 `s3_xxxxxxxx` 的文档标识（仅内部使用） |
| Step 4 | 设计契约 | 返回更新成功标志 |
| Step 5 | 页面任务 | 每页返回 `task_id`、`slide_id` |
| Step 6 | 图片 URL | 上传口返回的 `url` 填入 `src` |
| Step 7 | 交付物 | 在线 PPT 链接（可读链接，可对外） |

对用户只呈现文档名与链接，不展示 `docid`、`media_id` 等内部标识（F-035、F-038）。

## 失败排查

| 现象 | 可能原因 | 处置 | 证据 |
|---|---|---|---|
| `ModuleNotFoundError: openpyxl` | 未安装采集依赖 | 安装 `openpyxl` 后重跑 | F-074 |
| 提示 `.xls` 不支持 | 旧版二进制格式 | 先另存为 `.xlsx` 再采集 | F-074 |
| `doc create` 建成非 PPT | 未传或传错 `doc_type` | 固定传 `"ppt"`，重建文档 | `wecomcli-pptx-pptx-api.md:73` |
| 设计契约更新失败 | `design_md` 与 `story_md` 分开提交 | 合并到同一次调用 | `wecomcli-pptx-pptx-api.md:60` |
| 页面为空或版式不对 | 误用 `pages add` 而非 `addjsx` | 改用 `slide pages addjsx` | `wecomcli-pptx-pptx-api.md:62-65` |
| 图片不显示 | `src` 写了本地路径而非上传 `url` | 先上传，再把 `url` 填入 `src` | `wecomcli-pptx-pptx-api.md:75-82` |
| 用户索要 `.pptx` 文件 | 误判能力边界 | 明确说明仅在线链接，无导出 | F-041 |

## 延伸阅读

- [意图路由](../concepts/02-intent-routing.md)：sheet 与 pptx 两域的分流判据。
- [PPT 模板系统](../concepts/05-ppt-template-system.md)：若改用本地模板装配，需要读哪些文件。
- [脚本工具链](../concepts/04-scripts-toolchain.md)：`collect.py` 的展示上限与兼容补丁。
- [pptx 预览与重算](03-pptx-preview-and-recalc.md)：本地预览与公式重算的配套流程。