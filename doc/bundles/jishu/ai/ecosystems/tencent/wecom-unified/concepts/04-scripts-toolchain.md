---
type: concept
title: 脚本工具链
description: 逐一说明 6 个 Python 脚本的输入输出、第三方依赖、防护机制与最小部署环境。
tags: [wecom, wecom-unified, scripts]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-unified/
  - resource: /references/facts.md
---

# 脚本工具链

`scripts/` 只有 6 个 Python 文件，却覆盖了四类完全不同的任务：生成 DOCX、装配 HTML 页面、采集表格数据、抽取文档图片、PPTX 转预览图、重算 Excel 公式。它们不是 API 封装层——6 个脚本都不导入企业微信 SDK，只有 `build_page.py` 存在一处对外部 CLI 的子进程调用（F-108）。把它们理解为「物料生成器」更准确：输入本地文件或规格，输出可继续投喂给 `wecom-cli` 的素材。

## 一、总览

| 脚本 | 角色 | 关键输入 | 关键输出 | 第三方依赖 | 证据 |
|---|---|---|---|---|---|
| `build_docx.py` | 按 JSONL 规格生成 DOCX | `spec.jsonl` | 同目录 `docx/` 下的 `.docx` | `python-docx` | F-064～F-067 |
| `build_page.py` | 从固定 shell 组装幻灯片页面 | shell / body / vars / 模板集 | `.jsx` 页面、预览与校验结果 | 无（仅标准库） | F-068～F-072 |
| `collect.py` | 表格结构化采集 | Excel/CSV/TSV | stdout 紧凑 JSON | `openpyxl` | F-073～F-076 |
| `doc_image_extractor.py` | 抽取 DOCX/PPTX/XLSX 内图片 | 本地文档 | 图片文件目录 | `python-pptx`、`python-docx`、`openpyxl` | F-077～F-080 |
| `pptx2image.py` | PPTX → PDF → PNG 预览 | `.pptx` | `slide-NN.png` + 宫格联系表 | `pypdfium2` + LibreOffice | F-081～F-084 |
| `recalc.py` | 用 LibreOffice 宏重算并保存 | `.xlsx` | 原地覆盖的 `.xlsx` + stdout JSON | `openpyxl` + LibreOffice | F-085～F-092 |

一个容易忽略的部署事实是：**只有 `build_page.py` 是零第三方依赖的**（仅 `argparse`、`json`、`re`、`sys`），其余 5 个脚本各自需要 `python-docx`、`openpyxl`、`python-pptx`、`pypdfium2` 或 LibreOffice（F-068、F-066、F-074、F-078、F-081、F-092）。脚本内部不做依赖存在性检测，也不执行 `pip install`（F-078），缺依赖时直接以 `ImportError` 失败。

## 二、build_page.py：纯标准库的页面装配器

它有 10 个子命令：`init`、`template`、`buildall`、`build`、`check`、`recolor`、`contrast`、`fit`、`imgfit`、`images`（F-069）。核心机制是「固定 shell + 占位符填充」：shell 复制自 `templates/<slug>/shell/content.jsx`，页面上只有 `〔标题〕` 与 `〔B区内容〕` 两类占位符，后者定义为常量 `BODY`；值按原样插入，因此可以携带 `<br />` 或 `<span>`（F-070）。传入空字符串表示「有意留空」，而不是漏填。

`build` 的防护集中在三处，全部是「拒绝写文件」而不是警告：

| 防护 | 触发条件 | 行为 | 证据 |
|---|---|---|---|
| 缺值 | shell 中的占位符在 vars 中找不到对应键 | 列出缺失键与该 shell 的完整键集后退出 | `build_page.py:34-48`（源码） |
| 模板图未上传 | 页面仍含 `tpl_assets/` 且无 `tpl_urls.json` 映射 | 报出未上传资源，提示先执行 `template --docid` | `build_page.py:52-59`（源码） |
| 图片被压扁 | 页面含 `<Image>` 但未提供 manifest，或尺寸与真实比例不符 | 拒绝写页，提示用 `imgfit` 取得正确尺寸 | `build_page.py:60-63`（源码） |

`template` 子命令承担两类工作：对用户给定的 `.pptx` 先构建 shell，再在文档创建后用 `--docid` 把模板素材上传到智能文档并落盘 `tpl_urls.json`。上传动作以子进程调用 `[cli, 'smartpage', 'images', 'upload', '--json', {...}]`，`--cli` 默认 `wecom-cli`（F-071、F-072）。这也是 6 个脚本中唯一的外部 CLI 调用点（F-107、F-108）。

需要强调的是 `check` 的语义：它验证「每一页都是同一个 shell，且只填充了占位符」，即防止页面在手工编辑中悄悄偏离母版（`build_page.py:20`）。这类结构校验比逐页目检可靠，适合在 `buildall` 之后作为交付门禁。

## 三、build_docx.py：JSONL 规格驱动

输入是 JSONL，每行形如 `{"action": "<function_name>", "params": {...}}`，调用形式为 `python build_docx.py <spec.jsonl>`（F-064）。默认输出到 spec 同目录的 `docx/` 子目录，文件名取 spec 主名，冲突时追加毫秒时间戳与 PID，避免覆盖（F-065）。

安全边界由白名单与逐条校验构成：action 仅允许 `add_paragraph`、`add_heading`、`add_table`、`add_page_break`；每行校验 `action` 为字符串、`params` 为对象，未知字段直接报错（F-067）。实现基于 `python-docx` 的 `Document`、`WD_TABLE_ALIGNMENT`、`WD_ALIGN_PARAGRAPH`、`OxmlElement`、`Cm`、`Pt`、`RGBColor` 等（F-066）。这种设计的意图是让模型输出「数据」而不是「代码」：规格是声明式的，渲染逻辑固定在脚本里。

## 四、collect.py：表格采集与展示上限

输入为表格文件，输出打到 stdout 的紧凑 JSON；`--sheet`、`--range`、`--column` 用于定向采集，缺省采集所有子表（F-073）。格式支持分三档：`.xlsx`/`.xlsm` 采全量事实；`.csv`/`.tsv` 无合并与样式，只给类型剖面；`.xls` 提示先转换（F-074）。

为了避免把整张宽表灌进上下文，脚本内置 6 个展示上限：`MAX_COLS_DISPLAY=60`、`CELL_VALUE_TRUNC=60`、`MAX_CSV_BYTES=200*1024*1024`、`MERGE_DISPLAY_CAP=50`、`IMAGE_DETAIL_CAP=10`、`ROW_RUNS_CAP=15`（F-075）。另有针对 openpyxl 空 `<fill/>` 解析异常的临时兼容：替换解析器、退出时恢复，并在返回中加 `message` 键说明发生了补丁（F-076）。这不是通用修复，而是让采集在脏文件上仍能产出可解释结果。

## 五、doc_image_extractor.py：按阈值筛图

支持 PPTX、DOCX、XLSX 三种格式，分派字典 `SUPPORTED_FORMATS` 将 `.pptx`/`.docx`/`.xlsx` 分别指向三个抽取函数（F-077）。命令行形态为 `python doc_image_extractor.py <文档路径> [输出目录]`，批量目录扫描用 `--dir`/`-d`（F-080）。

筛选阈值有 6 个：`MIN_IMAGE_SIZE=10*1024`、`MIN_IMAGE_WIDTH=320`、`MIN_IMAGE_HEIGHT=180`、`MIN_IMAGE_AREA=80000`、`MIN_IMAGE_LONG_EDGE=480`、`MIN_IMAGE_SHORT_EDGE=64`（F-079）。它们共同过滤图标、分隔线与装饰性小图，只保留可用素材。依赖 python-pptx / python-docx / openpyxl，脚本内不做存在性检测（F-078）。

## 六、pptx2image.py：三段式预览

管线固定为三步：`convert_pptx_to_pdf` 执行 `[soffice, "--headless", "--convert-to", "pdf", "--outdir", ...]`；`render_pdf_to_pngs` 用 pypdfium2 把 PDF 各页渲染为 `slide-NN.png`；`make_contact_sheets` 拼宫格联系表（F-081）。参数为 `--outdir`（默认 `style_preview`）、`--grid`（只接受 6 或 9，默认 9）、`--dpi`（默认 120）、`--soffice`（默认取环境变量 `SOFFICE`）（F-082、F-083）。

soffice 的查找顺序是：`--soffice` 值 → `SOFFICE` 环境变量 → `soffice` → macOS 的 `/Applications/LibreOffice.app/Contents/MacOS/soffice` → Linux 的 `/opt/libreoffice/program/soffice`（F-084）。这意味着在未安装 LibreOffice 的机器上，脚本不会退化，而是直接找不到可执行文件。

## 七、recalc.py：带外链闸门的重算

调用形态为 `recalc.py <file.xlsx> [timeout_seconds] [--skip-external-link-check]`，宏 `store()` 原地覆盖文件（F-085）。它写入 LibreOffice 宏 `RecalculateAndSave`，函数体依次执行 `calculateAll()`、`store()`、`close(True)`，宏目录按 macOS 与 Linux 两个路径常量选择，文件名 `Module1.xba`（F-086）。

最重要的防护是外链闸门：`_has_external_links` 命中时直接返回 `{"error": "检测到外链(externalLinks)；先把外链单元格值拷出再重算"}`（F-087）。只有显式传 `--skip-external-link-check` 才会关闭检查（F-088）。这是一条「默认拒绝」策略：外链文件在无网或路径失效时会算出大片错误值，而错误值又会被当作真实数据继续流转。

运行环境还有两个细节。当 AF_UNIX socket 无法创建时，脚本会编译 `lo_socket_shim.c` 为 `lo_socket_shim.so` 并挂到 `LD_PRELOAD`，编译命令为 `gcc -shared -fPIC -o <so> <src> -ldl`，同时设置 `SAL_USE_VCLPLUGIN=svp`（F-089）。结果判定则依赖 `EXCEL_ERRORS` 的 7 个值——`#VALUE!`、`#DIV/0!`、`#REF!`、`#NAME?`、`#NULL!`、`#NUM!`、`#N/A`；输出 JSON 到 stdout，含 `error` 键时退出码为 1，否则为 0（F-090、F-091）。

## 八、部署矩阵

| 任务 | 脚本 | 最小环境 | 证据 |
|---|---|---|---|
| 生成 Word 文档 | `build_docx.py` | Python + `python-docx` | F-066 |
| 装配/校验页面 | `build_page.py` | Python 标准库 | F-068 |
| 读表取数 | `collect.py` | Python + `openpyxl` | F-074 |
| 抽取文档图片 | `doc_image_extractor.py` | Python + 三套文档库 | F-078 |
| 生成 PPT 预览 | `pptx2image.py` | Python + `pypdfium2` + LibreOffice | F-081、F-084 |
| 重算公式 | `recalc.py` | Python + `openpyxl` + LibreOffice（必要时 gcc） | F-089、F-092 |

## 延伸阅读

- [PPT 模板系统](05-ppt-template-system.md)：`build_page.py` 所服务的模板资产结构。
- [references 分类学](03-references-taxonomy.md)：脚本之外的 Markdown 知识层。
- [pptx 预览与重算示例](../examples/03-pptx-preview-and-recalc.md)：`pptx2image.py` 与 `recalc.py` 的用法演示。
- [套件定位与依赖](00-overview.md)：脚本在整个调用链中的旁路位置。