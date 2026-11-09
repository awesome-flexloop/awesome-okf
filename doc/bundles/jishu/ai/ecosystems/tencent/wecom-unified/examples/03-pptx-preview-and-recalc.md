---
type: example
title: 本地 PPT 预览与公式重算
description: 用 pptx2image.py 生成幻灯片宫格预览，用 recalc.py 在 LibreOffice 中重算并原地保存工作簿的演示。
tags: [wecom, wecom-unified, example, pptx, recalc]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-unified/
  - resource: /references/facts.md
---

# 本地 PPT 预览与公式重算

> **声明**：本示例为基于源码阅读整理的用法演示，**未在本机实跑**。下文命令、输出 JSON 与生成的图片名称均为格式「示意」，不代表真实运行结果；请以本机脚本输出为准。

## 适用场景

两个彼此独立、但经常前后出现的本地任务。其一，拿到一份 `.pptx`（用户模板或本地装配结果）后，需要快速看清每页版式，决定是否沿用其风格；此时用 `pptx2image.py` 生成逐页 PNG 与宫格联系表。其二，收到一份公式工作簿，打开时公式未重算或显示为 0，需要在无 Excel 的环境中强制重算并保存；此时用 `recalc.py`。

## 前置条件

| 条件 | pptx2image.py | recalc.py | 证据 |
|---|---|---|---|
| Python | 需要 | 需要 | F-081、F-092 |
| 第三方库 | `pypdfium2` | `openpyxl` | F-081、F-092 |
| 外部程序 | LibreOffice（`soffice`） | LibreOffice | F-084、F-086 |
| 编译工具 | 不需要 | 仅在 AF_UNIX 不可用时需要 `gcc` | F-089 |
| 文件格式 | `.pptx` | `.xlsx` | F-081、F-085 |

## 分步命令

### 一、生成 PPT 预览

**Step 1：转换并渲染**

```bash
python scripts/pptx2image.py deck.pptx --outdir style_preview --grid 9 --dpi 120
```

管线固定为「soffice 转 PDF → pypdfium2 渲染 PNG → 拼宫格联系表」，逐页文件名为 `slide-NN.png`（F-081）。`--grid` 只接受 6 或 9，默认 9；`--dpi` 默认 120（F-082、F-083）。

**Step 2：检查预览**

```bash
ls style_preview
```

应能看到逐页 PNG 与联系表。先看联系表判断整体风格，再放大单页核对文字与图片。

**Step 3：soffice 不在默认路径时显式指定**

```bash
python scripts/pptx2image.py deck.pptx --soffice /path/to/soffice
```

查找顺序为 `--soffice` 值 → `SOFFICE` 环境变量 → `soffice` → macOS 与 Linux 的默认安装路径（F-084）。

### 二、重算并保存工作簿

**Step 1：先备份原件**

`recalc.py` 的宏 `store()` 会**原地覆盖**输入文件，演示前应先复制一份（F-085）。

**Step 2：执行重算**

```bash
python scripts/recalc.py book.xlsx 120
```

第二个位置参数是超时秒数；脚本写入 LibreOffice 宏 `RecalculateAndSave`，依次执行 `calculateAll()`、`store()`、`close(True)`（F-085、F-086）。

**Step 3：按退出码判定结果**

```bash
echo $?
```

stdout 输出 JSON；结果含 `error` 键时退出码为 1，否则为 0（F-091）。

**Step 4：外链文件的处置**

默认命中外部链接会直接拒绝并返回错误，提示「先把外链单元格值拷出再重算」（F-087）。若确认要保留外链并继续，可显式关闭检查：

```bash
python scripts/recalc.py book.xlsx 120 --skip-external-link-check
```

该参数把 `check_external_links` 置为 `not args.skip_external_link_check`，属于有意的风险接受（F-088）。

## 预期结果（示意）

```text
$ python scripts/pptx2image.py deck.pptx --outdir style_preview --grid 9 --dpi 120
style_preview/slide-01.png
style_preview/slide-02.png
...
style_preview/contact-sheet.png      # 示意

$ python scripts/recalc.py book.xlsx 120
{"status": "ok", "errors": []}        # 示意

$ echo $?
0
```

若工作簿存在公式错误，预期 JSON 的 `errors` 中出现 `#VALUE!`、`#DIV/0!`、`#REF!`、`#NAME?`、`#NULL!`、`#NUM!`、`#N/A` 七类值之一，且退出码为 1（F-090、F-091）。

## 失败排查

| 现象 | 可能原因 | 处置 | 证据 |
|---|---|---|---|
| 找不到 `soffice` | 未安装 LibreOffice 或不在默认路径 | 安装后用 `--soffice` 或 `SOFFICE` 指定 | F-084 |
| `--grid` 报错 | 传了 6/9 以外的值 | 改为 6 或 9 | F-082 |
| 预览为空白页 | 源 PPT 页面本身为空或转换失败 | 用 PowerPoint/WPS 打开核对原文件 | F-081 |
| 重算返回外链错误 | 工作簿含 `externalLinks` | 先拷出外链单元格值；或确认风险后加 `--skip-external-link-check` | F-087、F-088 |
| 重算时报 socket 错误 | 运行环境无法创建 AF_UNIX socket | 脚本会尝试编译 `lo_socket_shim.so` 并挂 `LD_PRELOAD`，需本机有 `gcc` | F-089 |
| 退出码为 1 但有输出 | 公式结果含错误值 | 读 `errors` 列表逐项修复源公式 | F-090、F-091 |
| 原文件被改写 | `store()` 原地保存 | 从备份恢复；后续先复制再重算 | F-085 |

## 延伸阅读

- [脚本工具链](../concepts/04-scripts-toolchain.md)：两个脚本的完整参数、依赖与防护机制。
- [PPT 模板系统](../concepts/05-ppt-template-system.md)：预览结果如何用于判断模板风格。
- [从表格数据到在线 PPT](02-sheet-to-ppt-pipeline.md)：数据采集与在线交付的完整链路。