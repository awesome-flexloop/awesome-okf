---
type: Concept
title: "技能：基础结构、市场与提交解析排障"
description: "以「目录结构 → SKILL.md frontmatter → 子资源目录 → 市场安装 → 提交解析排障」五段归纳 WorkBuddy 开放平台技能资产的自述口径：技能目录树与各子目录用途、frontmatter 字段表与示例差异、技能市场进入与安装调用路径、以及 zip 解析失败时的定位参照与官方联系方式。"
tags: [WorkBuddy, 开放平台, 技能, Skill, SKILL.md, 技能市场, frontmatter, 解析失败排障, OKF]
generated: { by: "process:seven-concepts-e", at: "2026-10-16" }
verified: { by: "process:seven-concepts-v", at: "2026-10-16" }
status: stable
stale_after: "2027-04-16"
sources:
  - { id: D4, resource: "https://open.workbuddy.cn/docs/skill" }
---

# 技能：基础结构、市场与提交解析排障

> 本篇归纳 WorkBuddy 开放平台开发者文档「技能」页（D4）的自述内容：技能是什么、包目录长什么样、`SKILL.md` 的 frontmatter 怎么填、技能市场怎么进入与安装、以及提交 zip 包解析失败时去哪查。事实编号（F-073～F-088）见[来源代号与 F 编号事实登记](../references/article-source.md)；口径分层与核验结论见[核验报告](../references/verification.md)；页级覆盖见[页级采集与覆盖台账](../references/source-manifest.md)。构建与提交技能的完整操作示例见[构建并提交一个技能](../examples/01-build-and-submit-a-skill.md)。
>
> 信源纪律：本篇内容**仅为厂商（腾讯 WorkBuddy）开放平台开发者文档的自述**，**未在本平台实跑**任何创建、上架、审核或调用流程；文档未写明处一律标「**官方未给**」。

## 一、技能市场：进入、安装与创建

技能在开放平台体系中属可发布资产之一，**技能展示在 WorkBuddy 市场上**（F-073）。用户侧的三段路径与开发者侧的一个创建入口构成「市场」这一节的全部可见行为：

| 环节 | 原文行为 | 事实 |
| --- | --- | --- |
| 进入市场 | 点击左侧菜单【专家·技能·连接器】出现二级菜单，选择【技能】，进入【技能市场】 | F-074 |
| 安装 | 点击对应技能右上角加号，安装对应技能，并支持在对话中调用已安装的技能 | F-075 |
| 创建入口 | 点击市场右上角【添加技能】-【创建技能】 | F-076 |
| 创建交互 | 点击创建后跳转进入对话，补全创建技能的提示词，开启创建 | F-077 |

> **安装 → 调用路径**：据上述自述，技能不是「点开即用」，而是先由用户在技能市场**点加号安装**后，**才能在对话中调用**（F-075）。文档未给出安装后的存储位置、更新机制与卸载口径——这些均属**官方未给**，不得据常识补全。
>
> **创建即对话**：创建技能的入口不是表单页，而是**跳转进入对话**、由用户补全提示词开启创建（F-076、F-077）；文档未写明该对话背后使用的能力或模型，属**官方未给**。

## 二、技能基础结构（目录树）

技能包是一个以技能名命名的目录 `{skill-name}/`，其结构逐字如下（F-079）：

```
{skill-name}/
    ├── SKILL.md              # ★ 技能定义（必须）
    ├── references/           # 参考资料（可选）
    │   ├── api-spec.md       #   API 规范、字段类型等
    │   └── examples.md       #   示例数据
    ├── scripts/              # 可执行脚本（可选）
    │   ├── fetch-data.js     #   数据获取脚本
    │   └── transform.py      #   数据处理脚本
    └── templates/            # 模板文件（可选）
        ├── report.sh         #   报告生成模板
        └── workflow.sh       #   工作流模板格式
```

四个成员的唯一性分级为：**`SKILL.md`（技能定义，必须）**，`references/`（参考资料，可选）、`scripts/`（可执行脚本，可选）、`templates/`（模板文件，可选）三者均为可选（F-079）。即最小可用技能包只有一个 `SKILL.md`。

`SKILL.md` 自身使用 **YAML frontmatter + Markdown 正文**（F-080）：frontmatter 承载元信息，其余是技能指令正文。

## 三、`SKILL.md` 的 YAML frontmatter

文档给出的示例 frontmatter 含 9 个键，逐字如下（F-081）：

```
---
name: your-skill-name
display_name: 展示名称
display_name_en:
description: 一句话描述技能能力
description_zh: 简短中文介绍
description_en: A Brief English Introduction
category: writing            # 分类之一
version: 1.0.0
author: 合作方名称
---
 
# 技能指令正文
 
当用户需要做 XX 时，按以下步骤执行：
1. ...
2. ...
3. ...
```

与示例**并列**的是一张 9 条的「Frontmatter 字段」表（字段 / 必填 / 说明），逐字如下（F-082）：

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| name | 否 | 技能标识 |
| description | 是 | 写清用途和触发词 |
| description_zh | 是 | 简短中文介绍 |
| description_en | 是 | 简短英文介绍 |
| allowed-tools | 否 | 工具白名单（逗号分隔） |
| version | 是 | 版本号 |
| disable-model-invocation | 否 | true 则 AI 不会自动触发，只能用户手动调用 |
| user-invocable | 否 | false 则隐藏菜单，仅供 AI 内部使用 |
| author | 是 | 合作方名称 |

> **口径提示（示例 vs 字段表，两处并列不择一）**：示例 frontmatter 中出现的 `display_name`、`display_name_en`、`category` **三项未出现在上表字段表中**（F-083）；反之，字段表中的 `allowed-tools`、`disable-model-invocation`、`user-invocable` **未出现在示例中**（对照 F-081 与 F-082）。文档未说明孰为准，**本篇不替官方裁决**，建包时须回源官方页面核对（该差异已由核验抽查 F-083 回源确认一致）。

## 四、子资源目录（references / scripts / templates）

三个可选子目录各有「用途 / 适用场景 / 使用方式」，逐目录如下。

### references — 参考资料（F-084、F-085）

存放 `SKILL.md` 引用的补充知识文档，**AI 执行技能时会读取这些文件作为上下文**（F-084）；适用场景为 **API 字段类型定义、协议规范、领域知识参考、示例数据**等（F-084）；使用方式为在 `SKILL.md` 中通过 **`@references/xxx.md`** 引用（F-085）。原页示例：

```
references/
├── field-types.md           # 字段类型枚举和用法
├── api-endpoints.md         # API 接口文档
└── best-practices.md        # 最佳实践指南
```

### scripts — 可执行脚本（F-086、F-087）

存放技能执行中需要调用的脚本，**AI 通过 Bash 工具执行**（F-086）；适用场景为**调用外部 API、数据处理、批量操作、需要特定运行时的逻辑**（F-086）；使用方式为在 `SKILL.md` 中**声明调用命令和参数**（F-087）。原页示例：

```
scripts/
├── data-index.js            # 数据查询入口
└── tool-index.js            # 工具集入口
```

### templates — 模板文件（F-088）

存放**可复用的模板脚本或配置文件**（F-088）；适用场景为**标准化操作流程的模板、报告生成模板**（F-088）。原页示例：

```
templates/
├── authenticated-session.sh  # 认证会话模板
└── capture-workflow.sh       # 数据采集工作流模板
```

> **三目录共性**：`references/`、`scripts/`、`templates/` 均为可选（F-079）；文档**未给出**各子目录的数量上限、命名规范或体积约束，属**官方未给**。

## 五、提交 zip 解析失败：排查路径与联系渠道

开发者在开放平台创建技能时，**提交 zip 包后如解析失败**，文档给出的处置是（F-078）：

1. **先就地定位**：参考本页后续的【技能基础结构】（见第二节）与【子资源目录说明】（见第四节）**定位问题**——即用目录树与子目录用途比对包内结构；
2. **定位失败再求助**：**发送邮件至 `openworkbuddy@tencent.com`**（邮件联系运营同学），**或扫描开放平台首页下方的二维码，加入社群沟通**（F-078）。

> **跨页表述差异（并列登记）**：同一条「解析失败」口径在**专家页（D6）**的表述中，参照的小节名写作【**基础结构**】【**配置文件**】，而非技能页的【技能基础结构】【子资源目录说明】（F-078 为 D4、D6 多来源条目）。两页章节名不同属**文档自身措辞差异**，本篇并列表述、不择一。

> **边界与未给项**：
> - 文档**未给出**技能提交后的**审核时长**（核验报告第五节仅指出 D9 分享应用给出「7 个工作日」，其余各类审核时长均未给出）；技能审核时长属**官方未给**。
> - 文档**未给出**解析失败的具体错误码或字段级报错清单，排查只能回到「目录结构比对」这一粗粒度手段。
> - 本篇及全束**未在本机实跑**提交 zip 与解析流程；「解析失败」的成因、提示文案均属**未实跑**，不得写成「已验证可复现」。

同束入口：[技能页 F 编号事实](../references/article-source.md)｜[核验报告](../references/verification.md)｜[页级采集台账](../references/source-manifest.md)｜[构建并提交一个技能（示例）](../examples/01-build-and-submit-a-skill.md)。相关平级束：[WorkBuddy 官方站点与四区文档](../../workbuddy-official-docs/index.md)（产品侧能力口径）。
