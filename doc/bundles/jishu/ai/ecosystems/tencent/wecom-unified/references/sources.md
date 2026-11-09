---
type: reference
title: wecom-unified 信源登记
description: wecom-unified Skill 套件的上游仓库、固定基线、规模口径与关键信源文件登记
tags: [wecom, wecom-unified, skill, sources]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
phase: S（信源登记）
baseline: cae8a5befac67d96bfe573b1675c5faab474758e
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-unified/
  - resource: /references/facts.md
---

# wecom-unified 信源登记

> 本知识束的事实（F-001~F-108）全部派生自下述公开开源仓库，内容为公开级别；未引入仓库外的二手材料。

## 上游与基线

| 项目 | 值 |
|------|-----|
| 上游仓库 | `git@github.com:WecomTeam/wecom-unified.git` |
| 固定基线 commit | `cae8a5befac67d96bfe573b1675c5faab474758e` |
| 本地路径 | `vendor/WecomTeam/wecom-unified/`（git submodule，只读引用） |
| 独立版本号 | 无（`SKILL.md` frontmatter 仅 `name` / `description` / `allowed-tools`，无 `version` 字段，版本以 commit 基线为准） |
| 受控文件数 | 197 个（仓库内文件 198 个，扣除 `.git` gitlink 文件 1 个） |
| 许可证 | MIT（`LICENSE`，1062 字节，Copyright (c) 2026 WeCom） |
| 核验日期 | 2026-11-09 |
| 核验结论 | `git rev-parse HEAD` 返回 `cae8a5b…758e`，与基线一致；受控文件 197 个、`references/` 133 篇，与事实登记一致 |

## 版本与规模核对命令

以下命令均在仓库根（`vendor/WecomTeam/wecom-unified/`）或其子目录执行，可复跑核验。

```powershell
$repo = 'vendor/WecomTeam/wecom-unified'

# 1. 基线 commit
git -C $repo rev-parse HEAD

# 2. 受控文件数（HEAD 口径，不含 .git）
(git -C $repo ls-tree -r --name-only HEAD | Measure-Object -Line).Lines

# 3. references 总篇数
(Get-ChildItem "$repo/skills/wecom-unified/references" -Recurse -Filter *.md |
  Measure-Object).Count

# 4. references 逐域篇数（doc 域需排除 doc-manage 前缀）
$ref = "$repo/skills/wecom-unified/references"
(Get-ChildItem $ref -Filter 'wecomcli-contact*.md' | Measure-Object).Count
(Get-ChildItem $ref -Filter 'wecomcli-disk*.md' | Measure-Object).Count
(Get-ChildItem $ref -Filter 'wecomcli-media*.md' | Measure-Object).Count
(Get-ChildItem $ref -Filter 'wecomcli-message*.md' | Measure-Object).Count
(Get-ChildItem $ref -Filter 'wecomcli-doc*.md' |
  Where-Object { $_.Name -notlike 'wecomcli-doc-manage*' } | Measure-Object).Count
(Get-ChildItem $ref -Filter 'wecomcli-doc-manage*.md' | Measure-Object).Count
(Get-ChildItem $ref -Filter 'wecomcli-calendar*.md' | Measure-Object).Count
(Get-ChildItem $ref -Filter 'wecomcli-meeting*.md' | Measure-Object).Count
(Get-ChildItem $ref -Filter 'wecomcli-todo*.md' | Measure-Object).Count
(Get-ChildItem $ref -Filter 'wecomcli-sheet*.md' | Measure-Object).Count
(Get-ChildItem $ref -Filter 'wecomcli-smartsheet*.md' | Measure-Object).Count
(Get-ChildItem $ref -Filter 'wecomcli-smartpage*.md' | Measure-Object).Count
(Get-ChildItem $ref -Filter 'wecomcli-pptx*.md' | Measure-Object).Count
(Get-ChildItem $ref -Filter 'wecomcli-email*.md' | Measure-Object).Count
```

实测值（2026-11-09）：commit `cae8a5befac67d96bfe573b1675c5faab474758e`；受控文件 197；references 合计 133。逐域计数与 `facts.md` 第三节逐条事实（F-047~F-062）一致。

## 关键信源文件清单

| 文件（相对 `skills/wecom-unified/`，特别注明者除外） | 关键内容 | 关联 F 编号 |
|---|---|---|
| `SKILL.md` | frontmatter 三字段（`name`/`description`/`allowed-tools`）；三步前置检查；ID 类字段禁止外露；14 个业务域概览与 `→ 详见` 路由 | F-019~F-044、F-106 |
| `README.md`（仓库根） | 13 行功能范围表；项目结构代码块与两级命名；安装命令；平台与 Node.js 要求；首次使用自动安装声明 | F-015~F-018、F-102~F-105 |
| `LICENSE`（仓库根） | MIT 许可证、版权行 | F-012 |
| `references/wecomcli-contact.md` | contact 域入口（该域唯一一篇），同时是 ID 换可读名称的示例指向 | F-037、F-047 |
| `references/wecomcli-disk.md` | disk 域入口（该域唯一一篇） | F-048 |
| `references/wecomcli-media.md` | media 域入口（该域唯一一篇） | F-049 |
| `references/wecomcli-message.md` | message 域入口（该域唯一一篇） | F-050 |
| `references/wecomcli-doc.md` 及 `-create`/`-contents-append`/`-contents-overwrite` | doc 域入口与 3 篇正文创建/追加/覆盖细则 | F-051 |
| `references/wecomcli-doc-manage*.md` | doc-manage 域入口与成员/名称/权限 3 篇细则 | F-052 |
| `references/wecomcli-calendar*.md` | calendar 域入口与 agenda/cancel/create/freebusy/meeting-room/search/update 7 篇细则 | F-053 |
| `references/wecomcli-meeting*.md` | meeting 域入口与 cancel/create/list/original-get/search/update 6 篇细则 | F-054 |
| `references/wecomcli-todo*.md` | todo 域入口与 create/delete/finish/get/list/update 6 篇细则 | F-055 |
| `references/wecomcli-sheet*.md` | sheet 域入口与 17 篇主题细则（workbook/read-data/write-cells/formulas/style/filter/validation 等） | F-056 |
| `references/wecomcli-smartsheet*.md` | smartsheet 域入口、11 篇领域文档与 20 篇 `-template-*` 模板文档 | F-057~F-059 |
| `references/wecomcli-smartpage*.md` | smartpage 域入口、edit/mdx-syntax/data-driven-pages 与 10 篇 `-formula-*` 文档 | F-060 |
| `references/wecomcli-pptx*.md` | pptx 域入口、12 篇流程/契约文档（含 `government-contract`）与 14 篇 `-component-*` 组件文档 | F-061、F-100、F-041 |
| `references/wecomcli-email*.md` | email 域入口与 forward/get/reply/search/security/send/send-schedule 7 篇细则 | F-062 |
| `scripts/build_page.py` | 纯标准库；10 个 CLI 子命令；`〔标题〕`/`〔B区内容〕` 占位符；图片上传子进程；`--cli` 默认值 `wecom-cli` | F-068~F-072、F-107 |
| `scripts/build_docx.py` | JSONL 规格驱动；`docx` 包导入；action 白名单校验；默认输出路径与重名策略 | F-064~F-067 |
| `scripts/collect.py` | 表格定向采集；openpyxl 依赖；显示上限常量；空 `<fill/>` 兼容补丁 | F-073~F-076 |
| `scripts/doc_image_extractor.py` | PPTX/DOCX/XLSX 图片抽取；尺寸阈值；单文件与 `--dir` 批量形态 | F-077~F-080 |
| `scripts/pptx2image.py` | PPTX→PDF→PNG 三段管线；`--grid` 6/9；soffice 查找链 | F-081~F-084 |
| `scripts/recalc.py` | LibreOffice 宏 `RecalculateAndSave` 重算；外链闸门；`LD_PRELOAD` shim；Excel 错误值表；stdout JSON 与退出码 | F-085~F-092 |
| `assets/templates/index.json` | `usage`/`gate`/`sets` 三键注册与选择协议（naming/then/gate/sets 字段） | F-097~F-101 |
| `assets/templates/<set>/DESIGN.preset.md` | 9 套模板的设计约束（每套 1 个，共 9 个） | F-093~F-095 |
| `assets/templates/<set>/shell/*.jsx` | 渲染壳（共 11 个；`grove`、`signal` 各 2 个，其余 7 套各 1 个） | F-095 |
| `assets/templates/<set>/slides/*.slide` | 内容实例（共 32 个；每套 3~4 页） | F-094、F-096 |
| `skills/wecom-unified.zip`（仓库根 `skills/` 下） | 归档分发形态；423870 字节；198 个条目，含 `__MACOSX/` 前缀噪声 | F-005、F-006 |

## 口径说明

- 「受控文件数」指 Git HEAD 跟踪的文件数（`git ls-tree -r`），排除了 `.git` gitlink 文件；工作区直接计数（含 `.git`）为 198 个。
- `references/` 为扁平目录，无子目录；`doc` 域与 `doc-manage` 域前缀重叠，逐域计数时 `doc` 必须排除 `wecomcli-doc-manage*`。
- 归档 `.zip` 为二进制，无行号证据；其条目数与字节数为归档元数据事实。