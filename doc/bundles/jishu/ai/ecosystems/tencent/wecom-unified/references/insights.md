---
type: reference
title: wecom-unified 架构洞察（I 阶段）
description: 基于 F-001–F-108 条源码事实提炼的 wecom-unified 路由层与工具链洞察及 concepts/ 知识地图
tags: [wecom, wecom-unified, skill, routing, insights]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
phase: I（架构洞察）
baseline: cae8a5befac67d96bfe573b1675c5faab474758e
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-unified/
  - resource: /references/facts.md
---

# wecom-unified 架构洞察（I 阶段）

> I 阶段分析。基于 R 阶段 108 条源码事实（F-001~F-108），基线 commit `cae8a5befac67d96bfe573b1675c5faab474758e`。
> 分析日期：2026-11-09。所有证据编号均在 `facts.md` 中可回查。

---

## 洞察一：本质是「路由表 + 参数规范库」——SKILL.md 只做意图分流，133 篇 references 才是契约

**陈述**：`SKILL.md` 全文 15233 字节，仅承担三项职责：识别用户意图所属业务域、给出该域 reference 的入口链接、声明通用约束；14 个业务域小节各以一行 `→ 详见 [references/wecomcli-<域>.md]` 收尾。真正的参数契约不在 `SKILL.md`，而在 `references/` 的 133 篇 `.md` 中：文件全部平铺于一层、无子目录，采用「域入口 `wecomcli-<域>.md` + 域内细则 `wecomcli-<域>-<主题>.md`」两级命名。因此该 Skill 的可执行性取决于「是否读取了对应 reference」，而非模型对接口的记忆。

**证据**：
- F-019：`SKILL.md` 仅 15233 字节，frontmatter 占第 1-5 行。
- F-023：第 9 行三步路由——判断业务域 → 读取该域 reference → 按其中参数规范构造命令，并明令「严禁凭路由表描述或自身记忆猜测拼参数」。
- F-039、F-040：14 个业务域小节，各以一行 `→ 详见 references/wecomcli-<域>.md` 结束（行号 73/79/85/…/151）。
- F-009、F-045：`references/` 下 133 篇 `.md` 全部位于该层，子目录数为 0。
- F-018、F-046：README 与目录实测共同确认两级命名（14 篇域入口 + 119 篇域内文档）。

**反常识**：通常把 `SKILL.md` 当「能力说明书」，以为读完即可调用；这里恰恰相反——`SKILL.md` 只做了约 15 KB 的分流与约束，参数知识外置到 133 篇文档中。更反常识的是「文件越多越难用」的直觉失效：平铺目录 + 严格前缀命名使 `wecomcli-<域>` 本身成为可检索的索引，域内细则靠文件名即可枚举，无需任何注册表文件。真正的失败模式不是「知识缺失」，而是「跳过读取直接拼参数」。

**行动**：
- 集成实现时把 `SKILL.md` 当作路由层：先构建「业务域 → 域入口 reference」映射，再在每次构造命令前强制加载对应域文档。
- 评测该 Skill 时增加过程指标「是否读取了目标域 reference」，而非只看最终命令是否成功。
- 新增能力时优先续写域内细则文件，不要膨胀 `SKILL.md`；域入口只保留清单与指向。

---

## 洞察二：前置检查三步是硬门禁——任一失败即停止业务，避免「半可用」态

**陈述**：`SKILL.md` 把前置检查写成「使用任何命令前必须执行」的三步：Step 1 检查 `wecom-cli` 是否安装且版本不低于 `1.2.1`；Step 2 用 `auth show --status` 判定授权态（`authorized` 继续、`unauthorized` 转 Step 3、其它情况停止）；Step 3 仅在未授权时执行 `auth init --noninteractive`，输出授权链接与二维码并阻塞等待扫码，成功后再次复验状态。三步都带明确的失败终止语义，而不是「尽力继续」。

**证据**：
- F-024：第 11 行标题即「⚠️ 前置检查 — 使用任何命令前必须执行」。
- F-025、F-026、F-106：Step 1 要求版本 ≥ `1.2.1`，检查命令为 `wecom-cli --version`，该版本下限在第 13、19、25 行三处重复。
- F-028：安装后重跑版本命令，仍失败或版本仍低于 `1.2.1` 时停止业务操作并把错误告知用户。
- F-029、F-030：Step 2 命令 `auth show --status`，三种输出分支分别对应继续 / 转 Step 3 / 停止。
- F-031、F-032：Step 3 用 `auth init --noninteractive` 阻塞扫码授权，初始化后必须重跑状态检查，仅 `authorized` 才继续。

**反常识**：README 承诺「首次使用时 Skill 自动检查并安装所需 CLI 工具」，容易让人以为开箱即用、无需关心环境；但 `SKILL.md` 反而保留最严格的门禁——安装动作只是修复手段，安装完仍要复验版本与授权态。这里的反常识在于：**自动化程度越高，越需要显式的失败短路**，否则「CLI 已装但版本旧」「凭证存在但过期」这类半可用态会让后续每条业务命令都以难以归因的方式失败。

**行动**：
- 在宿主 Agent 中实现一个 preflight 函数，把三步串成「检查 → 修复 → 复验」的幂等流程，任一步失败直接返回可执行的修复指令，不进入业务分支。
- 把版本下限 `1.2.1` 抽为常量并与 `@wecom/cli` 安装命令放在同一处，避免三处文案漂移。
- 授权只做一次：把 `auth init --noninteractive` 放在人工介入节点（扫码），不要放进无人值守的自动化循环。

---

## 洞察三：ID 外露禁令把「内部标识符」与「可读输出」分离——是交付质量的隐性约束，而非安全脱敏

**陈述**：`SKILL.md` 设「通用输出约束：ID 类字段禁止外露」，对所有 `wecomcli-*` 技能生效，且明确「不因用户主动索要而放宽」。禁止清单覆盖 `userid`、`open_vid`、`department_id`、`chat_id` 等人员/组织标识，以及 `mail_id`、`media_id`、`file_id`、`space_id`、`folder_id`、`docid`、`content_id`、`msg_id`、`cursor`、`next_cursor` 等资源与分页标识；对应要求输出 `name`、`username`、部门名、邮箱、`subject`、`doc_name`、`chat_name`、`title` 等可读字段。接口只返回 ID 时，须先读对应业务域 reference 换取可读名称，换不到则用自然语言描述对象；但 `doc_url`、微盘分享链接这类可读链接不受限制。

**证据**：
- F-034：第 54-56 行，约束对所有 `wecomcli-*` 生效且不因用户主动索要而放宽。
- F-035：第 58 行禁止清单，含 4 个人/组织标识与 11 个资源/分页标识。
- F-036：第 59 行「必须」字段清单，均为可读名称类字段。
- F-037：第 60 行要求只返回 ID 时读业务域 reference（示例指向 `references/wecomcli-contact.md`）换名，无法换取时用自然语言描述。
- F-038：第 62-63 行，用户直接索要 ID 按「内部字段不便提供」处理；可读链接不在约束范围。

**反常识**：直觉会把「禁止输出 ID」理解为安全或隐私脱敏，但同一段规则明确放行可读链接——说明目的不是隐藏信息，而是**保证交付物对人可读**：ID 是机器标识符，出现在报告、消息、总结里会降低可读性，也会把内部实现细节泄漏到用户视野。另一个反常识点是「用户主动索要也不放宽」：这把约束定位为输出形态规范（类似排版规范），而不是权限控制，因此不能按「用户授权」逻辑豁免。

**行动**：
- 在输出层做适配：缓存 `ID → 可读名称` 映射，渲染前统一替换；映射缺失时降级为「某位同事」「该文档」这类描述，而不是回退输出原始 ID。
- 把 F-035 的 15 个禁字段做成静态检查规则（对最终文本做正则扫描），在交付前拦截。
- 设计对外模板时区分「可读链接」与「内部 ID」两类，前者允许直出，后者一律替换。

---

## 洞察四：脚本工具链按「必须外部二进制」与「纯标准库」分层——决定部署面，而非按代码体量分层

**陈述**：`scripts/` 下 6 个脚本构成一条从文档生成到预览重算的工具链，其环境要求呈明显阶梯：`build_page.py`（153447 字节，全仓最大脚本）只依赖 Python 标准库；`build_docx.py` 依赖 `docx` 包并以 JSONL 规格驱动；`collect.py` 依赖 `openpyxl`；`doc_image_extractor.py` 直接使用 python-pptx / python-docx / openpyxl 且脚本内不做存在性检测；`pptx2image.py` 需外部 `soffice` 加 pypdfium2 完成 PPTX→PDF→PNG；`recalc.py` 需 LibreOffice 宏、`openpyxl`，在无法创建 AF_UNIX socket 时还要用 `gcc` 现场编译 `LD_PRELOAD` shim。同时 6 个脚本都不导入企业微信 SDK，对外部 CLI 的唯一子进程调用点只有 `build_page.py:2403`。

**证据**：
- F-010：6 个脚本及字节数（`build_page.py` 153447、`build_docx.py` 46942、`collect.py` 36750、`doc_image_extractor.py` 16669、`recalc.py` 14621、`pptx2image.py` 10048）。
- F-068、F-069、F-070：`build_page.py` 文件头仅导入 `argparse`/`json`/`re`/`sys`（均为标准库），含 10 个 CLI 子命令与两组占位符。
- F-066、F-064、F-067：`build_docx.py` 导入 `docx` 包，以 JSONL 每行 `{action, params}` 驱动，action 走白名单校验。
- F-074、F-078：`collect.py` 依赖 openpyxl；`doc_image_extractor.py` 直接用 python-pptx/docx/openpyxl 且不检测、不安装。
- F-081、F-084：`pptx2image.py` 以 `soffice` 转 PDF，再渲染 PNG；soffice 查找按参数、环境变量、PATH、两个固定路径依次回退。
- F-085~F-089：`recalc.py` 写入 LibreOffice 宏 `RecalculateAndSave`，并在 socket 不可用时编译 `lo_socket_shim.so` 挂 `LD_PRELOAD`。
- F-107、F-108：脚本内 `wecom-cli` 字符串仅 1 处（`build_page.py:2445` 的默认值）；6 个脚本均不导入企业微信 SDK。

**反常识**：一般会按代码体量推断依赖重量，认为 150 KB 的 `build_page.py` 最难部署；实际情况正好相反——它是纯标准库脚本，任何一个 Python 解释器都能跑，而体积最小的 `recalc.py` 反而要求最重（LibreOffice + 宏目录 + `openpyxl` + 必要时 `gcc` 与 `LD_PRELOAD`）。另一个反常识点是工具链与业务 API 的耦合极低：所有脚本里只有一处调用外部 CLI，说明这些脚本是「文档/演示物料生成器」，而不是企业微信接口封装层。

**行动**：
- 按脚本建部署矩阵：纯 HTML 页面生成只需 Python；DOCX/XLSX 生成需 Python 包；PPT 预览与表格重算需 LibreOffice，容器内另需 `gcc` 与宏目录写权限。
- CI 分阶段安装依赖，避免为「生成一个 HTML」拉入整套办公套件。
- 调用 `recalc.py` 前先判定是否存在外链（脚本内已有外链闸门），再决定是否加 `--skip-external-link-check`。

---

## 洞察五：PPT 模板系统以 `index.json` 注册 + shell/slides 分离——把视觉骨架与内容实例解耦

**陈述**：`assets/templates/` 提供 9 套模板，53 个文件由 9 个 `DESIGN.preset.md`、11 个 `.jsx`、32 个 `.slide` 与 1 个 `index.json` 构成；每套目录统一为 `DESIGN.preset.md` + `shell/*.jsx` + `slides/*.slide`。`index.json` 顶层三键 `usage`/`gate`/`sets` 构成选择协议：`usage.naming` 规定 `name` 是给用户看的风格名、`slug` 只是目录名且不得出现在对用户的话里；`usage.then` 规定用户选定后只读该套的 `DESIGN.preset.md`、`shell/`、`slides/` 三处；`gate` 以题材条件（如政务）限定可选集合；`sets` 每项携带场景、正式度/密度/语气/性格标签、适用与回避场景以及 preset/shell/slides 路径。

**证据**：
- F-093、F-094：9 套模板目录，53 个文件 = 9 preset + 11 jsx + 32 slide + 1 index.json。
- F-095：每套结构为 `DESIGN.preset.md` + `shell/*.jsx` + `slides/*.slide`；`grove`、`signal` 各 2 个 `.jsx`，其余 7 套各 1 个。
- F-096：每套 `slides/` 仅 3 页或 4 页（3 页 4 套、4 页 5 套）。
- F-097、F-098：`index.json` 顶层 `usage`/`gate`/`sets` 三键；`usage` 五个子键 `shape`/`select`/`gate`/`naming`/`then`。
- F-099：`naming` 规定 slug 不对用户出现；`then` 规定选定后只读该套 preset/shell/slides。
- F-100：`gate` 段 `id=government`、`name=政务`、`sets=[broadside, long-table]`、`contract=../government-contract.md`。
- F-101：`sets` 项字段含 `slug`/`name`/`scenes_zh`/`tags`/`gate`/`best_for_zh`/`avoid_for_zh`/`preset`/`shell`/`slides`。

**反常识**：模板库通常被理解为「整套可套用的成品 deck」，但这里每套只有 3~4 页 `.slide`——它交付的是**可组合的最小骨架**，而非完整演示稿；真正决定视觉一致性的是 `DESIGN.preset.md` 与 `shell/*.jsx` 的分离：前者是设计约束，后者是渲染外壳，`slides` 只是内容实例。更反常识的是「选择模板」被做成了带 gate 的合规判断：政务题材直接限定为 `broadside` 与 `long-table` 两套，风格选择因此有了硬边界；同时 `naming` 明确禁止 slug 外露，与全局 ID 禁令同源——内部标识符不进用户视野。

**行动**：
- 选模板必须走 `index.json` 的 `gate → sets → then` 流程，不要靠遍历目录名或凭风格描述猜测。
- 对用户只呈现 `name` 与场景/适用性描述，不暴露 `slug`；需要引用路径时按 `preset`/`shell`/`slides` 字段照抄。
- 新增模板时同步注册 `sets` 项并补齐 `tags` 与适用/回避场景，否则无法被 gate 与选择流程识别。

---

## 洞察六：安装面与运行面分离——`npx skills add` 装的是 Skill，企业微信能力仍由独立 CLI 提供

**陈述**：该套件有两条独立的交付链：Skill 本体通过 `npx skills add WecomTeam/wecom-unified -y -g` 安装，支持 macOS（x64/arm64）、Linux（x64/arm64）、Windows（x64）并要求 Node.js ≥ 18，可自动检测已安装的宿主平台（WorkBuddy、CodeBuddy、MiniMax Code、Kimi Work、Codex、Cursor 等）；业务能力则依赖 `wecom-cli`，由 npm 包 `@wecom/cli` 提供并有 `1.2.1` 版本下限。仓库同时提供目录形态与 `skills/wecom-unified.zip` 归档（198 个条目，含 `__MACOSX/` 前缀噪声），skill 目录自身 193 个文件。`SKILL.md` frontmatter 只有 `name`、`description`、`allowed-tools` 三项，不含独立版本号。

**证据**：
- F-102：安装命令 `npx skills add WecomTeam/wecom-unified -y -g`。
- F-103、F-104：支持三平台五架构，`Node.js >= 18`；一行命令自动检测已安装平台并完成安装。
- F-105：首次使用时 Skill 自动检查并安装所需 CLI，并引导完成凭证配置。
- F-027、F-106：CLI 由 `npm install -g @wecom/cli` 安装，版本下限 `1.2.1`。
- F-005、F-006、F-008：`skills/wecom-unified.zip` 423870 字节、198 个归档条目；`skills/wecom-unified/` 递归 193 个文件。
- F-019~F-022：frontmatter 仅 `name`/`description`/`allowed-tools` 三行内容，无 version 字段。

**反常识**：「一行命令安装」容易被理解为安装后即可调用企业微信能力，实际安装的只是 Markdown 契约与脚本工具链，真正的接口能力来自另一个 npm 包。两条链的版本节奏也不同：Skill 无独立版本号（以 commit 基线为准），CLI 有显式 `1.2.1` 下限。另一个反常识点是 zip 归档与目录并存并非简单冗余，而是同一 Skill 的另一种分发形态（可离线/手动落盘），且归档内混入 `__MACOSX/` 噪声条目，说明其由 macOS 侧打包产出。

**行动**：
- 部署清单拆成两段：「安装 Skill」与「安装/升级 `@wecom/cli`」，两段分别校验，不要用 Skill 安装成功代替 CLI 可用。
- 离线或内网环境优先取 `skills/wecom-unified.zip`，但仍需单独准备 `@wecom/cli` 的离线安装包。
- 版本追溯以仓库 commit 为准（`SKILL.md` 无 version），升级评审时同时比对 Skill 基线与 CLI 版本下限。

---

## 概念文档知识地图

6 篇概念文档分三组递进：入门组 `00-overview` → `01-preflight-and-identity` 建立边界与门禁；路由组 `02-intent-routing` → `03-references-taxonomy` 理解分流与知识组织；工具组 `04-scripts-toolchain` → `05-ppt-template-system` 进入脚本与模板实现。

### 00-overview — 套件定位与依赖

- **一句话概要**：说明 `wecom-unified` 是「Markdown 契约 + 脚本工具链」的 Skill 包，而非企业微信 SDK，并划清 Skill 与 `wecom-cli` 两条交付链的边界。
- **覆盖要点**：
  - 仓库五条目与双层 `skills/` 结构（F-001~F-004、F-007）
  - Skill 主体 193 个文件、4 个子目录的体量分布（F-008）
  - `references/` 133 篇、`scripts/` 6 个、`assets/templates/` 53 个文件的三块构成（F-009~F-011）
  - 许可与元数据：MIT、frontmatter 三字段、无独立版本号（F-012、F-019~F-022）
  - 安装方式、平台矩阵与 Node.js 下限（F-102~F-105）
- **前置文档**：无（首篇）；建议先读 `sources.md` 了解基线。
- **学习目标**：能画出「宿主平台 → Skill → `wecom-cli` → 企业微信接口」的依赖链，并说明每层的安装与校验方式。

### 01-preflight-and-identity — 前置检查与身份

- **一句话概要**：拆解「版本检查 → 授权状态 → 非交互初始化」三步硬门禁与 `identity whoami` 身份获取，给出可复用的启动检查清单。
- **覆盖要点**：
  - 三步前置检查的标题与必须执行语义（F-024）
  - Step 1 版本下限 `1.2.1`、检查命令与安装后复验（F-025~F-028、F-106）
  - Step 2 `auth show --status` 三分支处理（F-029、F-030）
  - Step 3 `auth init --noninteractive` 的扫码阻塞与初始化后复验（F-031、F-032）
  - 身份获取命令 `wecom-cli identity whoami`（F-033）
- **前置文档**：`00-overview`。
- **学习目标**：能把三步检查写成幂等的启动脚本，并正确区分「未安装 / 版本过低 / 未授权 / 状态异常」四类失败的处置方式。

### 02-intent-routing — 意图路由

- **一句话概要**：说明 `SKILL.md` 如何从自然语言意图与链接特征判定业务域，并强制转到对应 reference 取参数，而不是凭记忆拼命令。
- **覆盖要点**：
  - 三步路由规则与「严禁猜测拼参数」禁令（F-023）
  - 14 个业务域清单及各自 `→ 详见` 链接（F-039、F-040）
  - 触发条件中的链接特征（`doc.weixin.qq.com`、`page.weixin.qq.com`、`drive.weixin.qq.com`）（F-021）
  - sheet 与 smartsheet 的路由判据（`/sheet/`、`/smartsheet/`、`s3_` 前缀、泛称默认）（F-043）
  - 域内特殊分支：doc 的「生成 `.docx` → 导入」、doc-manage 不负责正文（F-044）、smartsheet 的 `851003` Webhook 兜底（F-042）
- **前置文档**：`00-overview`。
- **学习目标**：给定一条自然语言请求或链接，能稳定判定目标业务域并定位到对应域入口文件，且能说出需要避开的路由歧义点。

### 03-references-taxonomy — references 分类学

- **一句话概要**：把 133 篇扁平 reference 的两级命名、逐域数量与命名变体整理成可检索的分类学，支撑定位与后续扩写。
- **覆盖要点**：
  - 133 篇平铺、无子目录的目录形态（F-009、F-045）
  - 14 篇域入口 + 119 篇域内细则的两级命名（F-018、F-046）
  - 逐域篇数：contact/disk/media/message 各 1，doc 与 doc-manage 各 4，calendar 8，meeting/todo 各 7，sheet 18，smartsheet 32，smartpage 14，pptx 27，email 8（F-047~F-062）
  - 大规模域的二级结构：sheet 的 17 篇主题、smartsheet 的 20 篇 `-template-*`、smartpage 的 10 篇 `-formula-*`、pptx 的 14 篇 `-component-*`（F-056~F-061）
  - 命名变体：模板名用下划线（F-058、F-059）、`wecomcli-pptx-pptx-api.md` 双前缀（F-061）
- **前置文档**：`00-overview`、`02-intent-routing`。
- **学习目标**：能仅凭文件名判断某篇 reference 属于哪个域、是入口还是细则，并按既有命名规则新增文档而不破坏检索一致性。

### 04-scripts-toolchain — 脚本工具链

- **一句话概要**：按「纯标准库 / Python 包 / 外部二进制」三层梳理 6 个脚本的输入输出、关键参数与部署依赖，形成选型与排障指南。
- **覆盖要点**：
  - 6 个脚本的清单与体量（F-010）
  - `build_page.py`：纯标准库、10 个子命令、`〔标题〕`/`〔B区内容〕` 占位符（F-068~F-070）
  - `build_docx.py`：JSONL 规格驱动、action 白名单、默认输出目录与重名策略（F-064~F-067）
  - `collect.py` 与 `doc_image_extractor.py`：openpyxl / office 包依赖、显示上限与图片阈值（F-073~F-080）
  - `pptx2image.py` 与 `recalc.py`：soffice 查找链、LibreOffice 宏、`LD_PRELOAD` shim 与外链闸门（F-081~F-089）
  - 与业务 API 的低耦合：无 SDK 导入、仅一处外部 CLI 调用（F-107、F-108）
- **前置文档**：`00-overview`。
- **学习目标**：能针对「生成 HTML / 生成 DOCX / 采集表格 / 抽取图片 / PPT 转图 / 重算公式」六类任务选出正确脚本，并列出其最小运行环境。

### 05-ppt-template-system — PPT 模板系统

- **一句话概要**：解释 `assets/templates/index.json` 的注册式选择协议，以及 `DESIGN.preset.md`、`shell/`、`slides/` 三段式结构如何把视觉骨架与内容实例解耦。
- **覆盖要点**：
  - 9 套模板与 53 个文件构成（F-093、F-094）
  - 每套 `DESIGN.preset.md` + `shell/*.jsx` + `slides/*.slide` 的统一结构（F-095）
  - 每套仅 3~4 页的「最小骨架」定位（F-096）
  - `index.json` 的 `usage`/`gate`/`sets` 三键与 `usage` 五个子键（F-097、F-098）
  - `naming` 的 slug 隐身规则与 `then` 的「选定后只读三处」规则（F-099）
  - 政务 gate 的题材限定与 `sets` 项字段（F-100、F-101）
- **前置文档**：`00-overview`、`02-intent-routing`。
- **学习目标**：能按 `gate → sets → then` 流程为给定场景选出模板，并说明为何不能直接把整套模板当作成品演示稿使用。