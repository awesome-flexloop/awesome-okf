---
type: reference
title: 权威核验报告
description: 秒悟 Meoo 产品功能全景指南束的 P0 核验结论——AI 服务两端点与环境变量、9 个 API 传参值、构建器 13 模型参数、13 vs 9 模型口径冲突、5MB vs 50MB 语境、限额与计数、微信三方权责表、代码块单行还原、时效条目、截图边界、提示词正反例、微信外链、转写噪声处置，逐项给出结论、证据与核验方式
tags: [meoo, miaowu, product-guide, 核验报告, 信源核验]
generated:
  by: reference_agent/deepseek-v4.1-flash
  at: "2026-10-18T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-18T00:00:00+08:00"
status: stable
stale_after: "2027-01-18"
sources:
  - id: S1
    resource: https://docs.meoo.com/
    title: 欢迎来到秒悟Meoo！（Meoo介绍 › 快速开始）
  - id: S2
    resource: https://docs.meoo.com/features/agent-modes
    title: 不同Agent模式差异
  - id: S3
    resource: https://docs.meoo.com/features/models
    title: 支持模型介绍
  - id: S4
    resource: https://docs.meoo.com/features/web-apps
    title: 功能介绍-网页应用搭建
  - id: S5
    resource: https://docs.meoo.com/features/wechat-miniprogram
    title: 【New】小程序搭建&部署
  - id: S6
    resource: https://docs.meoo.com/features/visual-editing
    title: 可视化修改
  - id: S7
    resource: https://docs.meoo.com/features/cloud-services
    title: 云服务能力介绍
  - id: S8
    resource: https://docs.meoo.com/features/ai
    title: AI 服务
  - id: S9
    resource: https://docs.meoo.com/features/asset-center
    title: 秒悟素材中心
  - id: S10
    resource: https://docs.meoo.com/features/file-storage
    title: 文件上传/下载/存储
  - id: S11
    resource: https://docs.meoo.com/features/project-config
    title: 根目录文件配置
  - id: S12
    resource: https://docs.meoo.com/features/skills
    title: 技能创建和使用
  - id: S13
    resource: https://docs.meoo.com/features/skill-marketplace
    title: 技能市场
  - id: S14
    resource: https://docs.meoo.com/features/connectors
    title: 连接器
---

# 权威核验报告

**核验日期**：2026-10-18

**核验范围**：本束 13 项关键声明（端点/传参值/限额/计数/权责表类逐字回验 + 时效、冲突与转写事项判定）。核验方法为「暂存原文逐字比对」：每项与 2026-10-18 WebFetch 抓取的 14 个源页转存稿逐字符对照；本束不做运行验证（未实际调用 API、未上传文件、未提审小程序），所有操作流程均为**文档级转写**。

**总结论**：13 项中，10 项 **✅ 通过（逐字一致或计数一致）**；1 项 **⚠️ conflicting 双源并存**（构建器 13 模型 vs AI 服务 9 传参值，页面定位不同、不调和）；1 项 **⚠️ 语境差异并列**（5MB vs 50MB）；1 项 **⚠️ dated 组**（套餐权益与「后续支持 MCP」等时效条目）；另完成截图边界与转写噪声隔离专项确认（计入核验项八、十二）。事实编号与信源台账见 [source-ledger.md](source-ledger.md)。

## 核验项一：AI 服务两端点与环境变量 ✅ 通过

| 项目 | 内容 |
|------|------|
| 结论 | ✅ 通过 |
| 声明（F-081、F-082、F-083、F-078） | 文本/视觉端点 `https://api.meoo.host/meoo-ai/compatible-mode/v1/chat/completions`；图片端点 `https://api.meoo.host/meoo-ai/api/v1/services/aigc/image-generation/generation`；环境变量 `MEOO_PROJECT_API_KEY`；服务端经 Edge Functions 以 `Deno.env.get("MEOO_PROJECT_API_KEY")` 读取、不暴露前端；开通服务时自动申请 Service AK 并写入该变量 |
| 证据来源 | S8「如何使用」「代码调用参考」三段 |
| 核验方式 | 两个 URL 逐段比对（含 `meoo-ai`、`compatible-mode`、`aigc/image-generation/generation` 等路径段）；环境变量名大小写与下划线逐字比对；`Deno.env.get` 调用形态逐字比对 |

## 核验项二：9 个 API 传参值与三类模型表 ✅ 通过

| 项目 | 内容 |
|------|------|
| 结论 | ✅ 通过 |
| 声明（F-074、F-075、F-076） | 文本 6 个：`qwen3.6-plus`、`qwen3-max`、`kimi-k2.5`、`deepseek-v3.2`、`glm-5`、`MiniMax-M2.5`；视觉 1 个：`qwen3-vl-plus`；图片 2 个：`qwen-image-2.0`、`wan2.7-image`。合计 9 个，与源页三张表格行数 6+1+2 机械一致 |
| 证据来源 | S8「支持的模型」三张表 |
| 核验方式 | 9 个传参值（含大小写：`MiniMax-M2.5` 为大写 M、`qwen3.6-plus` 带小数点版本号）逐一与暂存稿表格逐字比对；模型显示名（Qwen3.6-Plus/Qwen3-Max/Kimi/Deepseek/GLM/MiniMax/Qwen VL/Qwen Image 2.0/Wan2.7）与传参值分列登记，未混用 |
| 复核 | 文本示例注释中的可替换清单 `qwen3.6-plus / qwen3-max / deepseek-v3.2 / glm-5 / MiniMax-M2.5`（F-084）为 5 个（示例本体用 `kimi-k2.5`），与表格 6 个不矛盾，教程中两处数字（表格 6、注释 5+示例 1）均保留语境 |

## 核验项三：构建器 13 模型参数级表述 ✅ 通过（逐字 + 厂商自述标记）

| 项目 | 内容 |
|------|------|
| 结论 | ✅ 通过——数字逐字一致，且全部带「厂商自述」标记 |
| 声明（F-016–F-029） | 13 个模型/四厂商分组（4+3+2+4）；关键数字：训练成本 Qwen3.7-Plus 的 1/9；Qwen3.8-Max 2.4T 参数级；V4.1-Flash 552B MoE、输入激活 8B/输出激活 16B、HBM 1/4、SSD 1/8；V4-Pro 1.6T/49B、1M 窗口、最大输出 384K；V4-Flash 284B/13B、1M 输入/384K 输出、KV Cache 前代 10%、`reasoning_effort` 双模式；Kimi K3 2.8 万亿参数、KDA 架构、896 专家激活 16、扩展效率 2.5 倍、100 万 Token；K2.5 200K+、短板对照 Qwen3.6-Plus 和 GPT-5；GLM-5.3-Flash 320B/激活 18B、成本十分之一、100 万≈1500 页 A4、44 种职业场景；GLM-5.3 Terminal-Bench 3.0 开源第一、较前代约 50%、CogVLM；GLM-5.2 1M 无损、支持 MCP、JSON；Fast-Preview TPS 1.5～2 倍（80\~100 TPS）、超 TPM 排队 |
| 证据来源 | S3 全文 13 个 H2 小节 |
| 核验方式 | 22 处数字逐字回验通过（含 `80\~100` 的转义波浪号按源页「80~100」语义登记）；所有参数级表述在台账与概念页均显式标注「厂商自述」，本束不为其真实性背书；他厂产品名（GPT-5）按源页原文保留并注明出处性质 |

## 核验项四：构建器 13 模型 vs AI 服务 9 传参值 ⚠️ conflicting（双源并存，不调和）

| 项目 | 内容 |
|------|------|
| 结论 | ⚠️ conflicting——官方文档自身存在两套模型口径，**双源并存、注明页面定位差异与时效风险，禁止单方面「纠正」任何一方** |
| 口径 A（S3，F-016–F-029） | 构建器**选模型**页：13 个模型，命名为 Qwen3.8 系列（Flash/Max）、Qwen3.7 系列（Max/Plus）、DeepSeek-V4 系列（V4.1-Flash/V4-Pro/V4-Flash）、Kimi K3/K2.5、GLM-5.3/5.3-Flash/5.2/5.2-Fast-Preview |
| 口径 B（S8，F-074–F-076） | 运行时 **AI 服务 API 传参值**：9 个，命名为 qwen3.6-plus、qwen3-max、kimi-k2.5、deepseek-v3.2、glm-5、MiniMax-M2.5、qwen3-vl-plus、qwen-image-2.0、wan2.7-image |
| 交集与差异 | 仅 `kimi-k2.5` 命名直接对应（Kimi K2.5）；Qwen 代次不同（3.8/3.7 vs 3.6/3）、DeepSeek 代次不同（V4 vs v3.2）、GLM 代次不同（5.3/5.2 vs 5）；API 侧另有 MiniMax 与两个图片模型为构建器页所无 |
| 第三处旁证（S12，F-129） | 技能构建选模型推荐「Kimi 2.5 效果稳定，GLM-5/MiniMax-M2.5 解决复杂问题效果较好」——命名与口径 B 一致 |
| 证据来源 | S3 采集备注亦自述「两处模型命名存在版本差异……引用时需注意时效」 |
| 教程处置 | 模型概念页（02）与 AI 服务页（07）必须各自呈现本页口径，并交叉链接对方、显式写出「构建期选模型 ≠ 运行时 API 传参值，二者清单随发布节奏各自更新」；读者对接 API 时只以 S8 传参值为准 |

## 核验项五：5MB vs 50MB 两个文件限额 ⚠️ 语境差异（并列引用）

| 项目 | 内容 |
|------|------|
| 结论 | ⚠️ 语境差异——两个数字逐字成立、作用环节不同，并列不调和 |
| 两处口径 | ① F-108/F-112（S10）：**对话框上传**单个文件 5MB 以内、最多 10 个；超过 5MB 的单文件在**沙箱临时存储**、不进云端代码库、实例销毁即清除；② F-070（S7）：**云服务文件管理**中单文件上传上限 50MB，支持上传与 URL 生成 |
| 证据来源 | S10「文件上传」「文件存储」、S7「云服务操作」 |
| 教程处置 | 两个数字在概念页 09 与 06 中必须连同适用环节出现；大图入应用走「云服务存储桶 + CDN URL」四步法（F-115）正是两档限额之间的官方桥接路径，不得写成「平台只允许 5MB」或「可以传 50MB 到对话框」 |

## 核验项六：限额、计数与枚举清单机械一致 ✅ 通过

| 项目 | 内容 |
|------|------|
| 结论 | ✅ 通过 |
| 逐项计数 | 对话框 10 种文件格式（F-107，逐一点数：PDF/Word/Excel/PPT/TXT/Markdown/CSV/HTML/CSS/SVG=10）；小程序七步（F-049，步骤编号 1–7 齐）；三方权责表 10 行（F-055，逐行点数 10 个事项）；审核前清单 7 项（F-057）；FAQ 6 条（F-058）；Agent 模式 4 种（F-011）；网页应用四阶段（F-032）；提示词五要素（F-034）；技能构建三步、上线迭代五步（F-127/F-130/F-131、F-134）；技能市场类型 8 种（开发/测试/回复/文档/数据/设计/效率/运维，F-135）vs 标签 7 类（通用/开发/UI设计/测试/文档/数据/效率，F-137）——两个数字语境不同（文案描述的类型覆盖面 vs 实际标签筛选项），分别保留不混写；素材来源筛选 4 项、回收站保留 30 天（F-100）；视频两玩法、音频三子模式、发起三方式（F-091/F-096/F-097）；SEO/GEO 文件 5 种（F-120）；AI 自动集成四步（F-078）；连接器使用两场景（F-146） |
| 核验方式 | 全部清单逐项点数，与源页列表/表格行数机械一致；8 类型与 7 标签的差异在概念页 12 显式说明 |

## 核验项七：微信小程序权责表与流程表述 ✅ 通过

| 项目 | 内容 |
|------|------|
| 结论 | ✅ 通过 |
| 声明（F-046–F-059） | 第三方服务商身份与账号归属（F-048）；七步流程；双预览与「以真机预览结果作为最终确认依据」（F-050）；备案/审核主体在微信（F-051/F-052）；微信登录配置入口「云服务→登录认证→APPID 和 SECRET」（F-054）；权责表 10 行三方分工；审核前 7 项清单；FAQ 6 条；微信官方外链 4 条 |
| 证据来源 | S5 全文 |
| 核验方式 | 权责表逐行回验（10 行名称与三方单元格责任不串列）；平台角色边界三句关键限定（账号属于用户/审核由微信作出/Meoo 提醒仅为构建经验）逐字保留；4 条微信外链在核验项十三单独验 |
| 边界 | 微信侧备案材料、审核时限、类目全表未抓取，概念页只做指引并把裁决权显式归给微信官方，不脑补 |

## 核验项八：截图信息边界声明 ✅ 通过

| 项目 | 内容 |
|------|------|
| 结论 | ✅ 通过 |
| 涉及源页 | S4（选模型/上传/数据库/发布等截图）、S5（登录配置截图 1 张）、S6（全页操作靠 4 张截图/GIF）、S7（信息图+操作图 2 张）、S9（Tab/面板/卡片墙等十余张截图）、S10（上传/下载/存储桶四步截图）、S12/S13/S14（入口与弹窗截图） |
| 核验方式 | 逐页核对暂存稿中「（原文配图，无文字）」标注；凡按钮位置、面板布局、菜单层级类信息，概念页只采用源页文字层明确写出的路径（如「左上方标题」「左侧栏目版本历史」「设置>连接>连接器」「左下角设置>积分管理」均为文字逐字），无文字层支撑的界面细节一律不写 |
| 特别项 | S7 两张 `aka.doubaocdn.com` 图片直链仅登记于台账噪声表，不作为事实进入正文 |

## 核验项九：S8 代码块单行还原处置 ✅ 通过

| 项目 | 内容 |
|------|------|
| 结论 | ✅ 通过 |
| 声明（F-087、F-083–F-086） | 源页三段 fetch 示例经转换压成单行、围栏无语言标识；概念页 07 引用时按 JavaScript 天然逻辑还原换行缩进；零改写清单：两个端点 URL、`MEOO_PROJECT_API_KEY`、`Deno.env.get`、模型传参值、`messages`/`role`/`content`/`image_url`/`input`/`parameters`/`size: "1024*1024"`、`stream: false`、响应取值 `data.choices[0].message.content` |
| 核验方式 | 还原稿与暂存单行稿做字符串级对照（忽略空白差异），全部标识符与字面量一致；概念页同时保留源页声明「参考示例，实际代码由 Meoo 根据需求生成」，避免读者把示例当作必须手写的固定代码 |

## 核验项十：网页应用提示词方法与三组正反例 ✅ 通过

| 项目 | 内容 |
|------|------|
| 结论 | ✅ 通过 |
| 声明（F-034、F-035、F-038） | 五要素逐字「角色设定 背景上下文 核心功能 技术约束 输出规范」；三组正反例逐字（含原文「餐普规划」用字、「界面风格应简洁现代）」的多余右括号）；数据库话术逐字「开启数据库，并且把前端与数据库链接」 |
| 证据来源 | S4 第 1–2 节 |
| 核验方式 | 长句逐字回验；两处原文「错误」（餐普/括号）在概念页与台账中均保留原样并加注「源页原文如此」，不代为校改，防止把源页缺陷误修成「新事实」 |

## 核验项十一：微信官方四条外链 ✅ 通过

| 项目 | 内容 |
|------|------|
| 结论 | ✅ 通过 |
| 声明（F-059） | `https://developers.weixin.qq.com/miniprogram/introduction/`、`https://developers.weixin.qq.com/miniprogram/product/material.html`、`https://pay.weixin.qq.com/doc/v3/merchant/4012062524`、`https://developers.weixin.qq.com/doc/oplatform/open/intro.html` |
| 核验方式 | 4 条 URL 逐字符比对（域名、路径、商户号数字 `4012062524`）；本束不代抓微信站内容，仅作外链登记 |

## 核验项十二：转写噪声隔离 ✅ 通过

| 项目 | 内容 |
|------|------|
| 结论 | ✅ 通过 |
| 声明 | 9 类转换残片/非正文元素（S4 视频时间轴 0:00/2:01、S7 两张 doubaocdn 截图直链、各页配图标注、S8 单行代码块、S13「使用技」漏字、S4「餐普」与多余括号、分页与 On this page 锚点、S11 FAQ 合并段落、S10「Details」标记）已在 [source-ledger.md](source-ledger.md)「转写噪声登记」逐项留痕 |
| 核验方式 | 两轮机械扫描（ripgrep 正则 `aka\.doubaocdn\.com|2:01|On this page|（原文配图|\.temp/|file:///|_4d3c6c660f48|xn--|http://skill\.md/|http://team\.member\.read/|使用技[^能]`，扫描范围 `concepts/` 全部成稿与束根 `index.md`）：成稿后首轮扫描 0 命中；2026-10-18 fresh-context 独立评审复扫同样 0 命中（评审报告核验项 #5）；整改日按同一正则第三轮复扫仍 0 命中（ripgrep 无匹配退出）。源页原始缺陷在正文引用处以显式注释方式保留（F-035），其余不出现；台账与 log 中的命中为噪声登记面，不在正文门禁范围 |

## 核验项十三：时效（dated）条目组 ⚠️ dated（源页自带时效条件）

| 项目 | 内容 |
|------|------|
| 结论 | ⚠️ dated——事实逐字一致，但附带时效/条件限定，教程须原样保留限定语 |
| dated-1（F-110） | 代码下载权益绑定「LITE 套餐、PRO 套餐和 MAX 套餐」——套餐名与权益可能随 pricing 页调整 |
| dated-2（F-143） | 连接器「当前支持连接器接入外部API能力，后续将支持接入MCP等更多类型的连接器」——未来项，无时间表 |
| dated-3（F-016–F-029 整组） | 构建器 13 模型清单与 S8 九传参值均为 2026-10-18 时点快照，两套清单各自随发布节奏更新（参见核验项四） |
| dated-4（F-045） | 自定义域名「付费解锁」与两档形态——付费政策属可调整商业条款，价格未在源页出现 |
| dated-5（F-051/F-056/F-057） | 微信备案要求、服务类目资质、隐私配置以微信平台最新规则为准，源页自身反复声明 |
| 核验方式 | 限定语与事实成对回验；本束 `stale_after` 设为 2027-01-18（90 天），到期后上述条目优先复核；pricing 页与微信官方页为各自事实的最终裁决源 |

## 独立评审整改复审记录（2026-10-18）

fresh-context 独立评审（报告在 spec 目录 `review.md`）首轮结论 **fail**：7 个 issue（5×P1 + 2×P2，无 P0），其中归属本束的 I-02（部分）、I-03、I-06、I-07 已全部整改并复审：

| Issue | 问题 | 整改 | 复审证据 |
|---|---|---|---|
| I-07 | 本文件 frontmatter sources 第 7 项误写 `  - S7`（缺 `id:`），PyYAML ScannerError、Sphinx `Malformed YAML [myst.topmatter]` 告警 1 条 | 改为 `  - id: S7` | 两束 34 个带 frontmatter 文件经 PyYAML 全量复解析：34 通过、0 失败；`sphinx-build -E -W --keep-going` 全量构建两新束告警归零（见下方命令记录） |
| I-03 | 06/09 概念页及 index/log 的 F 审计标签成簇错配（23 处硬错配、2 处宽挂，涉及 F-069/070/071/072/078/080/111–115） | 以 source-ledger 为唯一基准重映射：CSV 数据操作=F-069、文件管理 50MB=F-070、密钥管理=F-071、GoTrue 认证=F-072、`MEOO_PROJECT_API_KEY` 自动注入=F-078、AI 生成文件下载与 zip/json 限制=F-111、沙箱阈值=F-112、适用范围=F-113、销毁机制=F-114、CDN 四步法=F-115；09 页两处整条机制引用改为区间 F-112–F-114；噪声截图句删除 F 标签 | 重映射后对 06/09/index/log 全部 F 标签逐号回台账对账（语义 + 所属源段双重核对），无错配；07 页 F-078（自动四步）与 F-080（话术示例）原挂载正确，未动 |
| I-06 | 06 页坑点句把源稿「AI 生成文件暂不支持 .zip/.json **下载**」（S10，F-111）反转为「项目文件不支持 **上传**」——动作与语境双重反转，且该否定句源稿不存在 | 改写为下载通道口径并挂 F-111、互链 09 页；删除「不支持上传」表述（源稿仅枚举 10 种支持格式，未作否定陈述） | 与暂存稿 `file-storage.md` 逐字复核；同束 09:57 同事实表述一致 |
| I-02 | 束根 `index.md` 两处姊妹束互链误用 `../../` 前缀（死链） | 改为 `../miaowu-cli-open-guide/index.md` | PowerShell `Test-Path` 解析为 True；全束相对链接复扫无死链 |

复审命令记录（cwd 为子模块根，2026-10-18 整改后实跑）：

- `python scripts/check-bundles-index.py` → exit 0（9 域/62 组/647 束五面一致）
- `python scripts/check-toctrees.py` → exit 0；`python scripts/check-utf8.py` → exit 0（11797 文件）
- PyYAML 批量解析两束 34 个 frontmatter → `parsed: 34 bad: 0`
- 污染正则扫描 `concepts/` 与束根 `index.md` → 0 命中
- `sphinx-build -b html -E -W --keep-going doc _build/html`（-E 强制全量重读）→ 全量告警均归属存量束，两新束 0 条

## 已知局限

- **文档级转写，无运行验证**：本束未实际调用 AI 服务端点、未上传文件、未开通云服务、未提交小程序审核；流程可用性以 2026-10-18 源页文字层为准。
- **全部为厂商单源**：150 条事实均来自 `docs.meoo.com` 自身页面；模型参数、性能排名、「分钟级」等宣传性表述无第三方交叉，已逐条标「厂商自述」。
- **截图信息不可得**：8 个源页的关键操作以截图/GIF/视频承载，WebFetch 仅得文字层；无文字层的界面细节未脑补。
- **两套模型口径并存**：S3 与 S8 的模型清单不一致是官方文档现状而非转写错误，本束采取双源并存策略（核验项四），不代为猜测对应关系。
- **未覆盖邻页**：`/pricing`、`/features/custom-domain`、`/features/collaboration`、`/promotions/referral` 及微信官方站均在 14 源清单外，仅作延伸指引登记。
- **时效**：`stale_after` 2027-01-18。到期优先复核 F-110（套餐权益）、F-143（MCP 进展）、F-016–F-029 与 F-074–F-076（两套模型清单）、F-045（域名付费政策）、F-051/F-056（微信侧规则）。
