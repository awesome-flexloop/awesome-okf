---
type: reference
title: wecom-unified 源码事实登记（R 阶段）
description: 企业微信套件 Skill wecom-unified 固定基线的零推测源码事实，F-001 起共 108 条
tags: [wecom, wecom-unified, skill, references, facts]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
phase: R（事实采集）
baseline: cae8a5befac67d96bfe573b1675c5faab474758e
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-unified/
---

# wecom-unified 源码事实登记

基线为 `vendor/WecomTeam/wecom-unified` 仓库，commit `cae8a5befac67d96bfe573b1675c5faab474758e`，受控文件 197 个（仓库内文件 198 个，其中 `.git` 为 1 个 gitlink 文件），许可证 MIT。仓库根目录没有 `SKILL.md`；技能主体位于 `skills/wecom-unified/` 这一层，其下含 `SKILL.md`、`references/`（133 篇）、`scripts/`（6 个脚本）、`assets/templates/`（9 套模板，53 个文件）；同级另有 `skills/wecom-unified.zip` 归档。

证据列约定：行号类事实写 `相对路径:行号` 或 `相对路径:起-止`（相对仓库根，正斜杠）；目录级计数事实的取证位置写该目录（无行号），并在「取证命令」列给出可复跑的实测命令。归档文件 `.zip` 为二进制，无行号。

## 一、仓库结构

| 编号 | 事实陈述 | 证据位置 | 取证命令 |
|---|---|---|---|
| F-001 | 仓库根目录含 5 个条目：`.git`、`.gitignore`、`LICENSE`、`README.md`、`skills` | 仓库根目录（目录级） | `Get-ChildItem -Force \| Select-Object Mode,Name` |
| F-002 | 仓库内文件总数 198 个，去掉 `.git` 后为 197 个 | 仓库根目录（目录级） | `(Get-ChildItem -Recurse -File -Force).Count`；`... \| Where-Object {$_.FullName -notlike "*\.git\*"}` |
| F-003 | 仓库根目录没有 `SKILL.md` 文件 | 仓库根目录（目录级） | `Get-ChildItem -Filter SKILL.md`（0 项） |
| F-004 | `skills/` 下 2 个条目：`wecom-unified/` 目录与 `wecom-unified.zip` 文件 | skills/（目录级） | `Get-ChildItem skills -Force` |
| F-005 | `skills/wecom-unified.zip` 大小 423870 字节 | skills/wecom-unified.zip（二进制） | `(Get-Item skills/wecom-unified.zip).Length` |
| F-006 | `skills/wecom-unified.zip` 的归档条目 198 个，其中文件条目 195 个、目录条目 3 个，首条 FullName 为 `wecom-unified/`，另含 `__MACOSX/` 前缀条目 | skills/wecom-unified.zip（二进制） | `[IO.Compression.ZipFile]::OpenRead(...).Entries` 计数并按 `Name -eq ""` 区分目录 |
| F-007 | `skills/wecom-unified/` 下 4 个条目：`SKILL.md`、`assets`、`references`、`scripts` | skills/wecom-unified/（目录级） | `Get-ChildItem skills/wecom-unified -Force` |
| F-008 | `skills/wecom-unified/` 递归文件 193 个 | skills/wecom-unified/（目录级） | `(Get-ChildItem skills/wecom-unified -Recurse -File).Count` |
| F-009 | `references/` 下 133 个 `.md` 文件，全部位于该层，无子目录 | skills/wecom-unified/references/（目录级） | `(Get-ChildItem references -File).Count`；`(Get-ChildItem references -Directory).Count`（0） |
| F-010 | `scripts/` 下 6 个 `.py` 文件及字节数：`build_docx.py` 46942、`build_page.py` 153447、`collect.py` 36750、`doc_image_extractor.py` 16669、`pptx2image.py` 10048、`recalc.py` 14621 | skills/wecom-unified/scripts/（目录级） | `Get-ChildItem scripts -File \| ForEach-Object {"{0}={1}" -f $_.Name,$_.Length}` |
| F-011 | `assets/templates/` 递归文件 53 个 | skills/wecom-unified/assets/templates/（目录级） | `(Get-ChildItem assets/templates -Recurse -File).Count` |
| F-012 | `LICENSE` 大小 1062 字节，第 1 行为 `MIT License`，第 3 行为 `Copyright (c) 2026 WeCom` | LICENSE:1-3 | `Get-Content LICENSE -TotalCount 3` |
| F-013 | `.gitignore` 共 1 行，内容为 `.DS_Store` | .gitignore:1 | `Get-Content .gitignore` |
| F-014 | `.git` 是 1 行 gitlink 文件，内容为 `gitdir: ../../../.git/modules/vendor/WecomTeam/wecom-unified` | .git:1 | `Get-Content .git` |
| F-015 | `README.md` 第 1 行为 `# 企业微信套件 Skill (WeCom-Unified)` | README.md:1 | `Get-Content README.md -TotalCount 1` |
| F-016 | `README.md` 第 15-29 行是一张 13 行的功能范围表，行首品类依次为 💬 消息、📧 邮件、📄 文档、🗂️ 文档管理、📊 在线表格、🧮 智能表格、📰 智能文档、📽️ 在线PPT、✅ 待办、📅 日程、🎥 会议、💾 微盘、👤 通讯录 | README.md:15-29 | `Get-Content README.md \| Select-Object -Skip 14 -First 15` |
| F-017 | `README.md` 第 57-71 行是项目结构代码块，第 63 行标 `SKILL.md`，第 64 行标 `references/` 并注明「扁平」 | README.md:57-71 | 同上，`-Skip 56 -First 16` |
| F-018 | `README.md` 第 65 行与第 67 行给出 references 的两级命名：域入口 `wecomcli-<域>.md`、域内细则 `wecomcli-<域>-<主题>.md` | README.md:65-67 | `Get-Content README.md \| Select-Object -Skip 64 -First 4` |

## 二、SKILL.md 前置检查与路由

| 编号 | 事实陈述 | 证据位置 | 取证命令 |
|---|---|---|---|
| F-019 | `SKILL.md` 大小 15233 字节，frontmatter 位于第 1-5 行，第 1 行为 `---`，第 5 行为 `---` | skills/wecom-unified/SKILL.md:1-5 | `(Get-Item SKILL.md).Length`；`Get-Content SKILL.md -TotalCount 5` |
| F-020 | frontmatter 第 2 行为 `name: wecom-unified` | skills/wecom-unified/SKILL.md:2 | `Select-String -Path SKILL.md -Pattern '^name:'` |
| F-021 | frontmatter 第 3 行为单行 `description:`，取值为双引号包裹的中文触发描述，含「链接包含 doc.weixin.qq.com 或 page.weixin.qq.com 必触发」与「链接包含 drive.weixin.qq.com 必触发」 | skills/wecom-unified/SKILL.md:3 | `Select-String -Path SKILL.md -Pattern '^description:'` |
| F-022 | frontmatter 第 4 行为 `allowed-tools: Bash, Read` | skills/wecom-unified/SKILL.md:4 | `Select-String -Path SKILL.md -Pattern '^allowed-tools:'` |
| F-023 | 第 9 行写路由规则：判断意图所属业务域 → 读取该域 reference 文件 → 按其中参数规范构造命令；句末为「严禁凭路由表描述或自身记忆猜测拼参数」 | skills/wecom-unified/SKILL.md:9 | `Get-Content SKILL.md \| Select-Object -Skip 8 -First 1` |
| F-024 | 第 11 行为 `## ⚠️ 前置检查 — 使用任何命令前必须执行` | skills/wecom-unified/SKILL.md:11 | `Select-String -Pattern '前置检查'` |
| F-025 | 第 13 行为 Step 1 标题，写「检查 CLI 是否安装和版本号是否为 1.2.1 或更高版本」 | skills/wecom-unified/SKILL.md:13 | 同上，`-Skip 12 -First 1` |
| F-026 | 第 16 行代码块内容为 `wecom-cli --version` | skills/wecom-unified/SKILL.md:15-17 | `Get-Content SKILL.md \| Select-Object -Skip 14 -First 3` |
| F-027 | 第 22 行代码块内容为 `npm install -g @wecom/cli` | skills/wecom-unified/SKILL.md:21-23 | 同上，`-Skip 20 -First 3` |
| F-028 | 第 25 行写：安装后重跑 `wecom-cli --version`；仍失败或版本仍低于 `1.2.1` 时停止业务操作并把错误告知用户 | skills/wecom-unified/SKILL.md:25 | `-Skip 24 -First 1` |
| F-029 | 第 27 行为 `### Step 2: 检查凭证是否配置`，第 30 行命令为 `wecom-cli auth show --status` | skills/wecom-unified/SKILL.md:27-31 | `-Skip 26 -First 6` |
| F-030 | 第 33-35 行列出三种 `auth show --status` 输出分支：`authorized` 继续、`unauthorized` 转 Step 3、报错或非上述状态则停止 | skills/wecom-unified/SKILL.md:33-35 | `-Skip 32 -First 3` |
| F-031 | 第 37 行为 `### Step 3: 配置凭证（仅未授权时执行）`，第 40 行命令为 `wecom-cli auth init --noninteractive` | skills/wecom-unified/SKILL.md:37-41 | `-Skip 36 -First 5` |
| F-032 | 第 43 行记录该命令输出授权链接与二维码并阻塞等待扫码，授权成功后自动退出，仅需执行一次；第 45 行要求在初始化后重跑 `auth show --status`，仅在 `authorized` 时继续 | skills/wecom-unified/SKILL.md:43-45 | `-Skip 42 -First 4` |
| F-033 | 第 49 行为 `## 获取个人身份`，第 51 行给出 `wecom-cli identity whoami` | skills/wecom-unified/SKILL.md:49-51 | `-Skip 48 -First 4` |
| F-034 | 第 54 行为 `## 通用输出约束：ID 类字段禁止外露`，第 56 行写该约束对所有 `wecomcli-*` 技能生效且不因用户主动索要而放宽 | skills/wecom-unified/SKILL.md:54-56 | `-Skip 53 -First 3` |
| F-035 | 第 58 行「禁止」条目列举 `userid` / `open_vid` / `department_id` / `chat_id`，并把 `mail_id` / `media_id` / `file_id` / `space_id` / `folder_id` / `docid` / `content_id` / `msg_id` / `cursor` / `next_cursor` 纳入同一范围 | skills/wecom-unified/SKILL.md:58 | `-Skip 57 -First 1` |
| F-036 | 第 59 行「必须」条目列举可读名称字段：`name` / `username` / `external_username` / 部门名 / 邮箱 / `subject` / `doc_name` / `chat_name` / `title` | skills/wecom-unified/SKILL.md:59 | `-Skip 58 -First 1` |
| F-037 | 第 60 行写接口只返回 ID 时先读对应业务域 reference（示例指向 `references/wecomcli-contact.md`）换取可读名称，无法换取时用自然语言描述对象 | skills/wecom-unified/SKILL.md:60 | `-Skip 59 -First 1` |
| F-038 | 第 62 行写用户直接索要 ID 时按内部字段不便提供处理；第 63 行写可读链接（`doc_url`、微盘分享链接）不在该约束范围内 | skills/wecom-unified/SKILL.md:62-63 | `-Skip 61 -First 2` |
| F-039 | 第 67 行为 `## 业务域概览`，其后 14 个 `###` 小节依序为 contact、doc、doc-manage、sheet、smartsheet、smartpage、pptx、calendar、meeting、todo、disk、email、message、media | skills/wecom-unified/SKILL.md:67-151 | `Select-String -Pattern '^### '`（共 17 处，含 Step 1/2/3 三处） |
| F-040 | 14 个业务域小节各以一行 `→ 详见 [references/wecomcli-<域>.md](references/wecomcli-<域>.md)` 结束，所在行号为 73、79、85、91、97、103、109、115、121、127、133、139、145、151（第 60 行另有一处同类链接） | skills/wecom-unified/SKILL.md:73-151 | `Select-String -Pattern 'references/wecomcli-' \| Select-Object -ExpandProperty LineNumber -Unique`（15 行） |
| F-041 | 第 105 行为 `### 📽️ PPT 演示文稿 (pptx)`；第 107 行写交付形态只有在线文档链接、不支持编辑本地 `.ppt` / `.pptx`、且「没有任何导出能力」；第 109 行为该域 `→ 详见` 链接 | skills/wecom-unified/SKILL.md:105-109 | `-Skip 104 -First 5` |
| F-042 | 第 95 行的 smartsheet 段落含「新增或更新记录返回 `851003` / `no authority` 时按本域流程改用 Webhook 兜底」 | skills/wecom-unified/SKILL.md:95 | `Select-String -Pattern '851003'` |
| F-043 | 第 89 行给出在线表格与智能表格的路由判据：明确说「在线表格」或链接含 `/sheet/` 走 sheet；说「智能表格 / 导入成智能表格」、链接含 `/smartsheet/` 或 `s3_` 前缀走 smartsheet；泛称「表格」默认智能表格 | skills/wecom-unified/SKILL.md:89 | `-Skip 88 -First 1` |
| F-044 | 第 77 行写 doc 域的新建流程为「生成 `.docx` → 导入」，第 83 行写 doc-manage 域「不负责正文读写」 | skills/wecom-unified/SKILL.md:77-83 | `-Skip 76 -First 8` |

## 三、references 分类学

| 编号 | 事实陈述 | 证据位置 | 取证命令 |
|---|---|---|---|
| F-045 | `references/` 下 `.md` 文件总数 133 篇 | skills/wecom-unified/references/（目录级） | `(Get-ChildItem references -File).Count` |
| F-046 | 133 篇中 14 篇为域入口，文件名逐一为 `wecomcli-contact.md`、`wecomcli-disk.md`、`wecomcli-media.md`、`wecomcli-message.md`、`wecomcli-doc.md`、`wecomcli-doc-manage.md`、`wecomcli-calendar.md`、`wecomcli-meeting.md`、`wecomcli-todo.md`、`wecomcli-sheet.md`、`wecomcli-smartsheet.md`、`wecomcli-smartpage.md`、`wecomcli-pptx.md`、`wecomcli-email.md`；其余 119 篇为域内文档 `wecomcli-<域>-<主题>.md` | skills/wecom-unified/references/（目录级） | `Get-ChildItem -Filter "wecomcli-*.md" \| Where-Object { $_.BaseName -notmatch '^wecomcli-[a-z]+-' }` 得 13 项，另计 `wecomcli-doc-manage.md` |
| F-047 | contact 域 1 篇：`wecomcli-contact.md` | skills/wecom-unified/references/（目录级） | `(Get-ChildItem -Filter "wecomcli-contact*.md").Count` |
| F-048 | disk 域 1 篇：`wecomcli-disk.md` | skills/wecom-unified/references/（目录级） | `(Get-ChildItem -Filter "wecomcli-disk*.md").Count` |
| F-049 | media 域 1 篇：`wecomcli-media.md` | skills/wecom-unified/references/（目录级） | `(Get-ChildItem -Filter "wecomcli-media*.md").Count` |
| F-050 | message 域 1 篇：`wecomcli-message.md` | skills/wecom-unified/references/（目录级） | `(Get-ChildItem -Filter "wecomcli-message*.md").Count` |
| F-051 | doc 域 4 篇：`wecomcli-doc.md`、`wecomcli-doc-create.md`、`wecomcli-doc-contents-append.md`、`wecomcli-doc-contents-overwrite.md` | skills/wecom-unified/references/（目录级） | `(Get-ChildItem -Filter "wecomcli-doc*.md" \| Where-Object { $_.Name -notlike "wecomcli-doc-manage*" }).Count` |
| F-052 | doc-manage 域 4 篇：`wecomcli-doc-manage.md`、`wecomcli-doc-manage-doc-members-update.md`、`wecomcli-doc-manage-doc-names-update.md`、`wecomcli-doc-manage-doc-rules-update.md` | skills/wecom-unified/references/（目录级） | `(Get-ChildItem -Filter "wecomcli-doc-manage*.md").Count` |
| F-053 | calendar 域 8 篇：入口 1 + `-agenda`、`-cancel`、`-create`、`-freebusy`、`-meeting-room`、`-search`、`-update` | skills/wecom-unified/references/（目录级） | `(Get-ChildItem -Filter "wecomcli-calendar*.md").Count` |
| F-054 | meeting 域 7 篇：入口 1 + `-cancel`、`-create`、`-list`、`-original-get`、`-search`、`-update` | skills/wecom-unified/references/（目录级） | `(Get-ChildItem -Filter "wecomcli-meeting*.md").Count` |
| F-055 | todo 域 7 篇：入口 1 + `-create`、`-delete`、`-finish`、`-get`、`-list`、`-update` | skills/wecom-unified/references/（目录级） | `(Get-ChildItem -Filter "wecomcli-todo*.md").Count` |
| F-056 | sheet 域 18 篇：入口 1 + 17 篇 `wecomcli-sheet-*.md`（含 `conditional-formatting`、`filter`、`float-image`、`formulas`、`history`、`protection`、`range-operations`、`read-data`、`search-replace`、`structure-operations`、`style`、`table-style`、`validation`、`visual-standards`、`workbook`、`write-cells`、`xlsx-process`） | skills/wecom-unified/references/（目录级） | `(Get-ChildItem -Filter "wecomcli-sheet*.md").Count`；`-Filter "wecomcli-sheet-*.md"` 得 17 |
| F-057 | smartsheet 域 32 篇：入口 1 + 11 篇领域文档（`chart-types`、`common`、`edit`、`field-types`、`formula`、`read`、`record-values`、`templates`、`view-types`、`webhook`、`webhook-examples`）+ 20 篇 `-template-*` 模板文档 | skills/wecom-unified/references/（目录级） | `(Get-ChildItem -Filter "wecomcli-smartsheet*.md").Count` 得 32；`-Filter "wecomcli-smartsheet-template-*.md"` 得 20 |
| F-058 | smartsheet 的 20 篇模板文档取值：`ai_efficiency`、`connect_to_app`、`financial_accounting`、`hr_and_administration`、`ledger_records`、`manufacturing`、`marketing`、`office_essentials`、`personal_efficiency`、`procurement_logistics`、`project_management`、`rd_process_customer`、`rd_process_ops`、`rd_process_project`、`rd_process_research`、`sales_and_operations`、`store_management`、`team_tasks`、`wechat_customer`、`work_report` | skills/wecom-unified/references/（目录级） | `Get-ChildItem -Filter "wecomcli-smartsheet-template-*.md" \| ForEach-Object {$_.Name}` |
| F-059 | 上述 20 篇模板文件名在模板名部分使用下划线（如 `wecomcli-smartsheet-template-rd_process_ops.md`），与其余文档的连字符命名不同 | skills/wecom-unified/references/（目录级） | 同 F-058 |
| F-060 | smartpage 域 14 篇：入口 1 + `-data-driven-pages`、`-edit`、`-mdx-syntax` + 10 篇 `-formula-*`（`arraylist`、`datetime`、`logic`、`math`、`operators`、`pageblock`、`reference`、`templates`、`text`、`user`） | skills/wecom-unified/references/（目录级） | `(Get-ChildItem -Filter "wecomcli-smartpage*.md").Count` 得 14；`-Filter "wecomcli-smartpage-formula-*.md"` 得 10 |
| F-061 | pptx 域 27 篇：入口 1 + 12 篇非组件文档（后缀 `content-contract`、`create-from-material`、`create-from-scratch`、`create-from-template`、`design-principle`、`government-contract`、`human-alignment`、`pptx-api`、`pptx-edit`、`story-principle`、`templates-anti-ai-slop`、`templates-README`，其中 `pptx-api`、`pptx-edit` 的全名为 `wecomcli-pptx-pptx-api.md`、`wecomcli-pptx-pptx-edit.md`）+ 14 篇 `wecomcli-pptx-component-*`（`animation`、`box`、`chart`、`codeblock`、`diagram`、`faicon`、`hyperlink`、`image`、`math`、`qrcode`、`slide`、`svg`、`table`、`text`） | skills/wecom-unified/references/（目录级） | `(Get-ChildItem -Filter "wecomcli-pptx*.md").Count` 得 27；`-Filter "wecomcli-pptx-component-*.md"` 得 14 |
| F-062 | email 域 8 篇：入口 1 + `forward-mail`、`get-mail`、`reply-mail`、`search-mail`、`security`、`send-mail`、`send-schedule` 七个主题（全名如 `wecomcli-email-forward-mail.md`、`wecomcli-email-security.md`） | skills/wecom-unified/references/（目录级） | `(Get-ChildItem -Filter "wecomcli-email*.md").Count` 得 8；`Get-ChildItem -Filter "wecomcli-email-*.md" \| ForEach-Object {$_.BaseName}` |
| F-063 | 含 doc-manage 在内的 15 个域逐域计数为 1+1+1+1+4+4+4+8+7+7+18+32+14+27+8，合计 133 篇，与目录实测的 133 篇相等 | skills/wecom-unified/references/（目录级） | 复用 F-047～F-062 命令，求和与 `(Get-ChildItem references -File).Count` 比对 |

## 四、scripts 工具链

| 编号 | 事实陈述 | 证据位置 | 取证命令 |
|---|---|---|---|
| F-064 | `build_docx.py` 的输入是 JSONL 规格文件，每行形如 `{"action": "<function_name>", "params": {...}}`，调用形式为 `python build_docx.py <spec.jsonl>` | skills/wecom-unified/scripts/build_docx.py:5-18 | `Get-Content build_docx.py -TotalCount 18` |
| F-065 | `build_docx.py` 的默认输出路径是 JSONL 同目录下的 `docx/` 子目录，文件名取 spec 主名，冲突时追加毫秒时间戳与 PID | skills/wecom-unified/scripts/build_docx.py:1219-1243 | `Select-String -Pattern '_pick_output_path' -Context 0,24` |
| F-066 | `build_docx.py` 从 `docx` 包导入 `Document` 及 `WD_TABLE_ALIGNMENT`、`WD_ALIGN_PARAGRAPH`、`OxmlElement`、`nsdecls`、`qn`、`Cm`、`Emu`、`Pt`、`RGBColor` | skills/wecom-unified/scripts/build_docx.py:33-38 | `Select-String -Pattern '^from docx'` |
| F-067 | `build_docx.py` 的 action 白名单含 `add_paragraph`、`add_heading`、`add_table`、`add_page_break`，逐条校验 `action` 字符串类型、`params` 为对象、未知字段报错 | skills/wecom-unified/scripts/build_docx.py:287-458 | `Select-String -Pattern '_spec_validate_(add_\|command)'` |
| F-068 | `build_page.py` 仅导入标准库 `argparse`、`json`、`re`、`sys` | skills/wecom-unified/scripts/build_page.py:22 | `Get-Content build_page.py -TotalCount 22` |
| F-069 | `build_page.py` 的 CLI 子命令为 `init`、`template`、`buildall`、`build`、`check`、`recolor`、`contrast`、`fit`、`imgfit`、`images` | skills/wecom-unified/scripts/build_page.py:4-16 | `Select-String -Pattern '^  (init\|template\|buildall\|build\|check\|recolor\|contrast\|fit\|imgfit\|images):'` |
| F-070 | `build_page.py` 的占位符为 `〔标题〕` 与 `〔B区内容〕`，后者定义为常量 `BODY`；值按原样插入，可含 `<br />` 或 `<span>` | skills/wecom-unified/scripts/build_page.py:18-24 | `Select-String -Pattern 'BODY =\|〔B区内容〕'` |
| F-071 | `build_page.py` 的 `template --docid` 分支以 subprocess 调用 `[cli, 'smartpage', 'images', 'upload', '--json', {...}]` | skills/wecom-unified/scripts/build_page.py:2403 | `Select-String -Pattern 'images.*upload' -Context 0,1` |
| F-072 | `build_page.py` 的 `template` 子命令参数含 `pptx`、`--dir`（默认 `.`）、`--docid`、`--urls`、`--cli`（默认 `wecom-cli`） | skills/wecom-unified/scripts/build_page.py:2445 | `Select-String -Pattern "add_parser\('template'\)"` |
| F-073 | `collect.py` 的输入为表格文件，输出为打到 stdout 的紧凑 JSON；参数 `--sheet`、`--range`、`--column` 做定向采集，缺省采所有子表 | skills/wecom-unified/scripts/collect.py:9-12 | `Get-Content collect.py -TotalCount 12` |
| F-074 | `collect.py` 第 19 行写：支持 `.xlsx` / `.xlsm`（全事实）、`.csv` / `.tsv`（无合并与样式，给类型剖面）、`.xls` 提示先转换；第 21 行写依赖 openpyxl | skills/wecom-unified/scripts/collect.py:19-21 | `Get-Content collect.py \| Select-Object -Skip 18 -First 3` |
| F-075 | `collect.py` 的展示上限常量：`MAX_COLS_DISPLAY=60`、`CELL_VALUE_TRUNC=60`、`MAX_CSV_BYTES=200*1024*1024`、`MERGE_DISPLAY_CAP=50`、`IMAGE_DETAIL_CAP=10`、`ROW_RUNS_CAP=15` | skills/wecom-unified/scripts/collect.py:35-41 | `Select-String -Pattern '^MAX_\|^CELL_VALUE_TRUNC\|^MERGE_\|^IMAGE_\|^ROW_'` |
| F-076 | `collect.py` 对 openpyxl 空 `<fill/>` 的解析异常做临时兼容：替换解析器、退出时恢复，并在返回中加 `message` 键 | skills/wecom-unified/scripts/collect.py:49-111 | `Select-String -Pattern 'already_patched\|不兼容的空 fill'` |
| F-077 | `doc_image_extractor.py` 读取 PPTX、DOCX、XLSX 三种格式；分派字典 `SUPPORTED_FORMATS` 的三项为 `.pptx` → `extract_images_from_pptx`、`.docx` → `extract_images_from_docx`、`.xlsx` → `extract_images_from_xlsx` | skills/wecom-unified/scripts/doc_image_extractor.py:6、276-280 | `Get-Content doc_image_extractor.py \| Select-Object -Skip 275 -First 6` |
| F-078 | `doc_image_extractor.py` 直接使用 python-pptx / python-docx / openpyxl，脚本内不做存在性检测、不运行 pip install | skills/wecom-unified/scripts/doc_image_extractor.py:8-9 | `Get-Content doc_image_extractor.py \| Select-Object -Skip 7 -First 2` |
| F-079 | `doc_image_extractor.py` 的图片尺寸阈值：`MIN_IMAGE_SIZE=10*1024`、`MIN_IMAGE_WIDTH=320`、`MIN_IMAGE_HEIGHT=180`、`MIN_IMAGE_AREA=80000`、`MIN_IMAGE_LONG_EDGE=480`、`MIN_IMAGE_SHORT_EDGE=64` | skills/wecom-unified/scripts/doc_image_extractor.py:30-35 | `Select-String -Pattern '^MIN_IMAGE_'` |
| F-080 | `doc_image_extractor.py` 的命令行形态为 `python doc_image_extractor.py <文档路径> [输出目录]`，批量目录扫描用 `--dir` / `-d` | skills/wecom-unified/scripts/doc_image_extractor.py:11-20 | `Get-Content doc_image_extractor.py \| Select-Object -Skip 10 -First 10` |
| F-081 | `pptx2image.py` 的三段管线为：`convert_pptx_to_pdf` 执行 `[soffice, "--headless", "--convert-to", "pdf", "--outdir", ...]` → `render_pdf_to_pngs` 用 pypdfium2 把 PDF 各页渲染为 `slide-NN.png` → `make_contact_sheets` 拼宫格联系表 | skills/wecom-unified/scripts/pptx2image.py:86-89、111-128、132-141 | `Select-String -Pattern 'convert_pptx_to_pdf\|render_pdf_to_pngs\|make_contact_sheets'` |
| F-082 | `pptx2image.py` 的宫格取值为 `--grid` 只接受 6 或 9，默认 9；单页缩略图框 360×203 像素（16:9） | skills/wecom-unified/scripts/pptx2image.py:216、143 | `Select-String -Pattern 'thumb_w\|"grid"'` |
| F-083 | `pptx2image.py` 的参数为 `--outdir`（默认 `style_preview`）、`--grid`（6/9，默认 9）、`--dpi`（默认 120）、`--soffice`（默认取环境变量 `SOFFICE`） | skills/wecom-unified/scripts/pptx2image.py:215-218 | `Select-String -Pattern 'add_argument\("--(outdir\|grid\|dpi\|soffice)'` |
| F-084 | `pptx2image.py` 的 soffice 查找顺序为 `--soffice` 值、`SOFFICE` 环境变量、`soffice`、`/Applications/LibreOffice.app/Contents/MacOS/soffice`、`/opt/libreoffice/program/soffice` | skills/wecom-unified/scripts/pptx2image.py:230-242 | `Select-String -Pattern 'soffice' -Context 1,1` |
| F-085 | `recalc.py` 的调用形态为 `recalc.py <file.xlsx> [timeout_seconds] [--skip-external-link-check]`，宏 `store()` 原地覆盖文件 | skills/wecom-unified/scripts/recalc.py:8、21-22 | `Get-Content recalc.py -TotalCount 28` |
| F-086 | `recalc.py` 写入的 LibreOffice 宏为 `RecalculateAndSave`，函数体依次 `calculateAll()`、`store()`、`close(True)`；宏目录取 macOS 与 Linux 两个路径常量，文件名 `Module1.xba` | skills/wecom-unified/scripts/recalc.py:43-57 | `Select-String -Pattern 'MACRO_DIR\|RECALCULATE_MACRO'` |
| F-087 | `recalc.py` 的外链闸门在 `_has_external_links` 命中时直接返回 `{"error": "检测到外链(externalLinks)；先把外链单元格值拷出再重算"}` | skills/wecom-unified/scripts/recalc.py:265-269、296-297 | `Select-String -Pattern '_has_external_links\|externalLinks'` |
| F-088 | `recalc.py` 的 `--skip-external-link-check` 参数把 `check_external_links` 置为 `not args.skip_external_link_check` | skills/wecom-unified/scripts/recalc.py:391-397 | `Select-String -Pattern 'skip_external_link'` |
| F-089 | `recalc.py` 在 AF_UNIX socket 不可创建时编译 `lo_socket_shim.c` 为 `lo_socket_shim.so` 并挂到 `LD_PRELOAD`；编译命令为 `gcc -shared -fPIC -o <so> <src> -ldl`；env 另设 `SAL_USE_VCLPLUGIN=svp` | skills/wecom-unified/scripts/recalc.py:68-110 | `Select-String -Pattern 'LD_PRELOAD\|gcc\|SAL_USE_VCLPLUGIN'` |
| F-090 | `recalc.py` 的 `EXCEL_ERRORS` 列表含 7 个值：`#VALUE!`、`#DIV/0!`、`#REF!`、`#NAME?`、`#NULL!`、`#NUM!`、`#N/A` | skills/wecom-unified/scripts/recalc.py:59-61 | `Select-String -Pattern 'EXCEL_ERRORS' -Context 0,3` |
| F-091 | `recalc.py` 输出 JSON 到 stdout；结果含 `error` 键时退出码 1，否则 0 | skills/wecom-unified/scripts/recalc.py:27 | `Get-Content recalc.py \| Select-Object -Skip 26 -First 1` |
| F-092 | `recalc.py` 第 30-41 行的导入共 11 条：标准库 10 条（`argparse`、`json`、`os`、`platform`、`socket`、`subprocess`、`sys`、`tempfile`、`zipfile`、`from pathlib import Path`）加第三方 1 条 `from openpyxl import load_workbook` | skills/wecom-unified/scripts/recalc.py:30-41 | `Select-String -Pattern '^(import\|from) '` |

## 五、模板系统

| 编号 | 事实陈述 | 证据位置 | 取证命令 |
|---|---|---|---|
| F-093 | `assets/templates/` 下 9 套模板目录：`broadside`、`cartesian`、`cobalt-grid`、`editorial-forest`、`emerald-editorial`、`grove`、`long-table`、`sakura-chroma`、`signal` | skills/wecom-unified/assets/templates/（目录级） | `Get-ChildItem assets/templates -Directory \| ForEach-Object {$_.Name}` |
| F-094 | `assets/templates/` 递归 53 个文件 = 9 个 `DESIGN.preset.md` + 11 个 `.jsx` + 32 个 `.slide` + 1 个 `index.json` | skills/wecom-unified/assets/templates/（目录级） | 分别 `-Filter "DESIGN.preset.md"`、`"*.jsx"`、`"*.slide"` 计数加 `index.json` |
| F-095 | 每套目录结构为 `DESIGN.preset.md` + `shell/*.jsx` + `slides/*.slide`；`grove` 与 `signal` 各 2 个 `.jsx`（其他 7 套各 1 个） | skills/wecom-unified/assets/templates/（目录级） | `Get-ChildItem -Recurse -Filter *.jsx \| Group-Object DirectoryName` |
| F-096 | `slides/` 页数为 3 的 4 套（`cartesian`、`cobalt-grid`、`grove`、`signal`），为 4 的 5 套（`broadside`、`editorial-forest`、`emerald-editorial`、`long-table`、`sakura-chroma`） | skills/wecom-unified/assets/templates/（目录级） | 逐套 `(Get-ChildItem <set>/slides -Filter *.slide).Count` |
| F-097 | `index.json` 顶层 3 个键：`usage`（第 2-8 行）、`gate`（第 9-18 行）、`sets`（第 19 行起） | skills/wecom-unified/assets/templates/index.json:2-19 | `Get-Content index.json -TotalCount 19` |
| F-098 | `usage` 的 5 个子键为 `shape`、`select`、`gate`、`naming`、`then`（第 3、4、5、6、7 行） | skills/wecom-unified/assets/templates/index.json:3-7 | 同上 |
| F-099 | `usage.naming` 写 `name` 是给用户看的风格名，`slug` 只是目录名，对用户的话里不出现 slug；`usage.then` 写用户选定后只读该套 `DESIGN.preset.md`、`shell/`、`slides/`，路径照抄 preset/shell/slides 字段 | skills/wecom-unified/assets/templates/index.json:6-7 | `Select-String -Pattern '"naming"\|"then"' -Context 0,1` |
| F-100 | `gate` 段 `id=government`、`name=政务`、`sets=[broadside, long-table]`、`contract=../government-contract.md`，`trigger_zh` 含党政机关/事业单位/国企央企/街道社区等主体条件与公文体判据 | skills/wecom-unified/assets/templates/index.json:9-18 | `Get-Content index.json \| Select-Object -Skip 8 -First 10` |
| F-101 | `sets` 每项的字段为 `slug`、`name`、`scenes_zh`、`tags{formality, formality_rank, density, tone, character}`、`gate`、`best_for_zh`、`avoid_for_zh`、`preset`、`shell`、`slides`；首项 `slug=sakura-chroma`、`name=活动策划`、`gate=null` | skills/wecom-unified/assets/templates/index.json:20-46 | `Get-Content index.json \| Select-Object -Skip 19 -First 28` |

## 六、安装与耦合

| 编号 | 事实陈述 | 证据位置 | 取证命令 |
|---|---|---|---|
| F-102 | `README.md` 第 46 行给出安装命令 `npx skills add WecomTeam/wecom-unified -y -g` | README.md:46 | `Select-String -Pattern 'npx skills add'` |
| F-103 | `README.md` 第 37 行列支持平台 macOS (x64/arm64)、Linux (x64/arm64)、Windows (x64)；第 38 行写 `Node.js >= 18` | README.md:37-38 | `Get-Content README.md \| Select-Object -Skip 36 -First 3` |
| F-104 | `README.md` 第 43 行写「支持 WorkBuddy、CodeBuddy、MiniMax Code、Kimi Work、Codex、Cursor 等平台，一行命令自动检测已安装的平台并完成安装」 | README.md:43 | `Get-Content README.md \| Select-Object -Skip 42 -First 1` |
| F-105 | `README.md` 第 49 行写首次使用时 Skill 自动检查并安装所需 CLI 工具，并引导完成凭证配置 | README.md:49 | `Get-Content README.md \| Select-Object -Skip 48 -First 1` |
| F-106 | `SKILL.md` 第 13、19、25 行三处写 CLI 版本下限 `1.2.1`；第 22 行的安装包名为 `@wecom/cli` | skills/wecom-unified/SKILL.md:13-25 | `Select-String -Pattern '1\.2\.1\|@wecom/cli'` |
| F-107 | `scripts/` 下的脚本中字符串 `wecom-cli` 只出现 1 处，位于 `build_page.py:2445` 的 `--cli` 默认值 | skills/wecom-unified/scripts/build_page.py:2445 | `Select-String -Path scripts\*.py -Pattern 'wecom-cli'` |
| F-108 | `scripts/` 的 6 个脚本都不导入企业微信 SDK 或 `wecom` 模块；对外部 CLI 的唯一子进程调用点在 `build_page.py:2403` | skills/wecom-unified/scripts/（目录级） | `Select-String -Path scripts\*.py -Pattern '^\s*(import\|from) '`；`Select-String -Pattern 'subprocess.run'` |

## 统计

本文档共 108 条事实，分布于 6 个主题节：一、仓库结构（F-001～F-018，18 条）；二、SKILL.md 前置检查与路由（F-019～F-044，26 条）；三、references 分类学（F-045～F-063，19 条）；四、scripts 工具链（F-064～F-092，29 条）；五、模板系统（F-093～F-101，9 条）；六、安装与耦合（F-102～F-108，7 条）。

references 总篇数 133 篇；逐域实测：contact 1、disk 1、media 1、message 1、doc 4、doc-manage 4、calendar 8、meeting 7、todo 7、sheet 18、smartsheet 32（含 `-template-*` 20）、smartpage 14（含 `-formula-*` 10）、pptx 27（含 `-component-*` 14）、email 8，合计 133。